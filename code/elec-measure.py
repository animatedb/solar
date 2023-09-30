#!/usr/bin/env python3

# sudo apt install python3-pip
# sudo pip3 install matplotlib

# mypy --strict
import datetime as dt
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as numpy
import math as math
import csv as csv
import SolarUseIrrad as sui
import PlotBalance as pb
from typing import Dict, List, Tuple

# Power drop/loss from a cable depends on length.
# https://sciencing.com/cable-length-vs-power-drop-12184174.html
# https://teslamotorsclub.com/tmc/threads/charging-efficiency.122072/
# https://www.solarreviews.com/blog/how-do-tesla-chargers-compare-to-other-electric-car-chargers
# https://saxton.org/tom_saxton/2010/07/tesla-roadster-charging-rates.html
# https://www.reddit.com/r/teslamotors/comments/8wt28u/l2_charging_efficiency_questions_model_3/
# Fixed loss for cooling battery while charging.
# Roadster - Charging is close to 270Wh/mile @ 240V-32A, but 414 Wh/mile at 120V-12A (which inverter?)
# Tesla model 3 RWD has 7.7 kW onboard charger, other teslas have 11.5 kW
# Originally used Tripp-Lite SPS-615-HG hospital grade surge protector 15' (closer to 16') 1800W
# Then used Husky HD#448-665 15' extension cord from Home Depot. 14/3
# Sonoff Pow R2 99% accuracy
#
# Losses for extension cord
# 10 AWG .1 ohms for 100'
# 12 AWG .16 ohms for 100'	15' is 0.024 ohms
#	0.024 * 15A = 0.36V drop @ 15A		0.36V * 15A = 5.4W
# 14 AWG .25 ohms for 100'	15' is 0.0375 ohms
#	0.0375 * 15A = 0.5625V drop @ 15A	0.05625 * 15A = 8.4W	
# The car reports about 77% of the energy compared to the wall plug.
CarCalibration = 1.0
GroundCapacity = '.6'

def getDateMDY(dateStr:str) -> dt.datetime:
    if dateStr[-3] == '/':
        return dt.datetime.strptime(dateStr, '%m/%d/%y')    # y = 2 digit year
    else:
        return dt.datetime.strptime(dateStr, '%m/%d/%Y')    # Y = 4 digit year

##def addLists(list1:List[float], list2:List[float], list3:List[float]=None) -> List[float]:
##    if list3:
##        return [list1[i] + list2[i] + list3[i] for i in range(len(list1))]
##    else:
##        return [list1[i] + list2[i] for i in range(len(list1))]    

def addLists(*lists:List[float]) -> List[float]:
    totals = lists[0].copy()
    for singleList in lists[1:]:
        for i in range(len(singleList)):
            totals[i] += singleList[i]
    return totals

def clip(list1:List[float]) -> List[float]:
    return [v if v >= 0 else 0 for v in list1]

def subtractLists(list1:List[float], list2:List[float]) -> List[float]:
#    return clip([list1[i] - list2[i] for i in range(len(list1))])
    return [list1[i] - list2[i] for i in range(len(list1))]

def getGenKeys() -> List[str]:
    return ['Roof Solar', 'Ground Solar']

def getUseKeys() -> List[str]:
    return ['Fridge', 'TV / Cable', 'Computers', 'Bath Heat', 'Living Heat', 'Car']

def addDerivedValues(meas) -> None:
    meas['Total Solar'] = addLists(*[meas[key] for key in getGenKeys()])
    meas['Measured Use'] = addLists(*[meas[key] for key in getUseKeys()])
    meas['Total Use'] = addLists(meas['Total Solar'], meas['Main Meter'])
    meas['Other'] = subtractLists(meas['Total Use'], meas['Measured Use'])


class Measurements(dict):
    # headers must be the same every time this is called.
    # rowValues must align with headers.
    def addRowValues(self, headers:List[str], rowValues:List[str]):
        for headerI, header in enumerate(headers):
            if header != 'Comments':            # Discard comments
                if header not in self:
                    self[header] = []
                if header == 'Date':
                    self[header].append(getDateMDY(rowValues[headerI]))
                else:
                    conversion = 1.0
                    if header == 'Roof Solar':  # Convert MWH to KWH
                        conversion = 1000.0
                    if header == 'Car':
                        conversion = CarCalibration
                    # Convert all float column values.
                    val = 0.0
                    if len(rowValues[headerI]) > 0:
                        val = float(rowValues[headerI]) * conversion
                    self[header].append(val)

    # This preserves the Date, and adds a PeriodDays so that both are present.
    # Returns the differences of neigboring rows.
    def getPeriodMeasurements(self, startDate=None) -> dict[str, List]:
        periodMeasurements = {}
        startDateIndex = 1 	# Default if no startDate is used
        if startDate:
            dates = self['Date']
            for dateI, date in enumerate(dates):
                if getDateMDY(startDate) <= dates[dateI]:
                    startDateIndex = dateI
                    break
        for key in self.keys():
            # n is indexed for each row.
            for n in range(startDateIndex, len(self['Date'])):
                y = self[key]
                if key not in periodMeasurements:
                    periodMeasurements[key] = []
                if key == 'Date':
                    if 'PeriodDays' not in periodMeasurements:
                        periodMeasurements['PeriodDays'] = []
                    periodDays = (y[n]-y[n-1]).days
                    periodMeasurements['PeriodDays'].append(periodDays)
                    periodMeasurements['Date'].append(y[n])
                else:
                    try:
                        diffVal = y[n]-y[n-1]
                        # Main Meter can go down. Monitoring plugs can be reset to zero
                        # and increase from there.
                        if diffVal < 0 and key != 'Main Meter':
                            diffVal = y[n]
                        if n-startDateIndex+1 < len(periodMeasurements):
                            periodDays = periodMeasurements['PeriodDays'][n-startDateIndex+1]
                        periodMeasurements[key].append(diffVal / periodDays)
#                        if key == 'Roof Solar':
#                            i = n - startDateIndex
#                            print(i, self['Date'][i], y[i], y[i-1])
                    except TypeError:
                        periodMeasurements[key].append(0.0)
        if False:
            for key in periodMeasurements:
                if key == 'Roof Solar':
                    print('rf', periodMeasurements[key][-3:])
        if False:
            n = 46
            for key in periodMeasurements:
                if key in ['Date', 'PeriodDays', 'Roof Solar',
                        'Ground Solar', 'Total Solar',
                        'Car', 'Living Heat', 'Bath Heat',
                        'Total Solar', 'Main Meter', 'Total Use',
                        'Measured Use', 'Other'
                           ]:
    # Looks like mistake in source .csv file for 11-5 to 11-14-2022. Original graph did not
    # use weekly data for 11-14. Roof Solar is wrong.
    # with day period: n=28, 11-14-2022 other is 2.47, total use = 5.85, measured use = 3.33
        # PeriodDays = 3
                    print(key, periodMeasurements[key][n])
##                    if key != 'PeriodDays':
##                        y = self[key]
##                        di = startDateIndex+n
##                        print(' ', y[di], y[di-1])
##            print(periodMeasurements['Roof Solar'][n:50])
        return periodMeasurements


def readMeasurementsFile(measurementsFn:str) -> Measurements:
    measurements = Measurements()
    with open(measurementsFn, 'r') as f:
        csvData = csv.reader(f)
        headers = []
        for rowI, row in enumerate(csvData):
            # First row is used as header identification.
            if len(headers) == 0:
                headers = row
            # First column must be a date.
            if '/' in row[0]:
                try:
                    measurements.addRowValues(headers, row)
                except ValueError as e:
                    raise ValueError('row ', rowI+1) from e
    if len(measurements) == 0:
        raise ValueError('No dates found in column A')
    return measurements


def getRowColumn(row, column:str) -> float:
    return float(row[ord(column)-ord('A')])

def plotDetails(periodMeasurements:dict[str, List]):
    genKeys = getGenKeys()
    useKeys = ['Other']
    useKeys.extend(getUseKeys())
    gen = [ periodMeasurements[key] for key in genKeys ]
    use = [ periodMeasurements[key] for key in useKeys ]
    dates = periodMeasurements['Date']
    totalGen = [x + y for x, y in zip(gen[0], gen[1])]

    fig = plt.figure()
    fig.set_size_inches(10, 7)
    fig.autofmt_xdate()
    ax = fig.gca()
    ax.set_axisbelow(True)
#    ax.xaxis.set_major_locator(mdates.YearLocator(month=6))
#    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.stackplot(dates, *use, labels=useKeys)

    roofGenColor = '#B0B0B0'
    roofGen = periodMeasurements['Roof Solar']
    plt.scatter(dates, roofGen, label='Roof Solar', color=roofGenColor, s=8)
    plt.plot(dates, roofGen, color=roofGenColor)

    totalGenColor = '#000000'
    plt.scatter(dates, totalGen, label='Total Solar', color=totalGenColor, s=8)
    plt.plot(dates, totalGen, color=totalGenColor)

    ax.legend()
    plt.title('Solar Generation and Use - 3.24+' + GroundCapacity + ' kW System')
    plt.ylabel('Daily Solar Generation and Energy Use (kWh)')
    plt.savefig('ElecMeas.svg', bbox_inches='tight')

if __name__ == "__main__":
    measurements = readMeasurementsFile('ElecMeasure.csv')
    periodMeasurements = measurements.getPeriodMeasurements('05/07/22')
    addDerivedValues(periodMeasurements)
    plotDetails(periodMeasurements)

    periodMeasurements = measurements.getPeriodMeasurements()

    pb.plotTotalSurplus(measurements)

    addDerivedValues(periodMeasurements)
    sui.plotAll(periodMeasurements, 'Temperature/noaa.csv')
