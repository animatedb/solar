#!/usr/bin/env python
# mypy --strict
import datetime as dt
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as numpy
import math as math
import csv as csv
from typing import List, Tuple

MaxDecl:int = 24

def getDateMDY(dateStr:str) -> dt.datetime:
    if dateStr[-3] == '/':
        return dt.datetime.strptime(dateStr, '%m/%d/%y')    # y = 2 digit year
    else:
        return dt.datetime.strptime(dateStr, '%m/%d/%Y')    # Y = 4 digit year

def getDateYMD(dateStr:str) -> dt.datetime:
    return dt.datetime.strptime(dateStr, '%Y/%m/%d')

def calcDatePercent(selectedDate:dt.datetime, dateData:List[dt.datetime]) -> float:
    return (selectedDate - dateData[0]) / (dateData[-1] - dateData[0])

# Generates weekly declination.
# The declination of the sun is the angle between a plane perpendicular
# to a line between the earth and the sun and the earth's axis.
# https://www.itacanet.org/the-sun-as-a-source-of-energy/part-3-calculating-solar-angles/
def getDecl(minGen:float, maxGen:float, dayPeriods:List[int]) -> List[float]:
    # Weekly declination for one year
    declination = []
    for n in range(0, 365):
        d = 23.45 * math.pi / 180 * math.sin(2 * math.pi * (284 + n) / 365)
        declination.append(d)
    minDecl = min(declination)
    maxDecl = max(declination)
    weekDecl = []
    kwhMult = (maxGen-minGen)/(maxDecl-minDecl)
    kwhOffset = minGen - minDecl * kwhMult
    # Summer solstice is june 21, winter is dec 21, so peaks should be at those dates.
    # First date is 9/7/2018
#    dateShift = int(52*8.4/12)	# 36
    # 243 days between 1/1/2018 and 9/7/2018 / 7 = 35.57
    dateShift = 36	# in weeks
    totalDays = 0
    for period in dayPeriods:
        weekIndex = totalDays / 7
        declIndex = int(weekIndex + dateShift)
        value = declination[declIndex%52*7] * kwhMult + kwhOffset
        if weekIndex > 160:   # 10/10/2021 Y&H 1000W inverter
            value *= 1.04
        if weekIndex > 194:   # 5/25/2022 Vevor/Marsrock inverter - same as Mophorn/WVC? 4*300W
            value *= 1.08
        weekDecl.append(value)
        totalDays += period
    return weekDecl

# Averages temperatures from daily into weekly temperatures.
def weeklyTemps(dates:List[dt.datetime], lowTemps:List[int], highTemps:List[int]
    ) -> Tuple[List[dt.datetime], List[int], List[int]]:
    summedWeekLowTemp = 0
    summedWeekHighTemp = 0
    avgDates = []
    avgLowTemps = []
    avgHighTemps = []
    for datei, date  in enumerate(dates):
        summedWeekLowTemp += lowTemps[datei]
        summedWeekHighTemp += highTemps[datei]
        if date.weekday() == 5:
            avgDates.append(date)
            if datei < 7:
                divisor = datei+1
            else:
                divisor = 7
            avgLowTemps.append(summedWeekLowTemp/divisor)
            avgHighTemps.append(summedWeekHighTemp/divisor)
            summedWeekLowTemp = 0
            summedWeekHighTemp = 0
    return avgDates, avgLowTemps, avgHighTemps

def getTemperature(fn:str) -> Tuple[List[dt.datetime], List[int], List[int]]:
    with open(fn, 'r') as f:
        csvData = csv.reader(f)
        dates = []
        lowTemps = []
        highTemps = []
        for rowi, row in enumerate(csvData):
            if len(row) > 2:
                try:
                    dates.append(getDateYMD(row[0]))
                except ValueError:
                    raise(ValueError('Bad format ' + str(rowi)))
                lowTemps.append(int(row[2]))
                highTemps.append(int(row[1]))
    return dates, lowTemps, highTemps

# scale temperatures to usage kWh data
# use is Solar use data
def scaleTemperatures(temps:List[int], use:List[float]) -> List[float]:
    invTemps = []
    tempMin = min(temps)
    tempRange = max(temps) - tempMin
    useLow = min(use)
    useRange = max(use) - useLow
    for t in temps:
        invTemps.append(t * useRange/tempRange)
    invLow = min(invTemps)
    invRange = max(invTemps) - invLow
    for i, t in enumerate(temps):
        invTemps[i] = invRange - (invTemps[i] - invLow) + useLow
    scaledMaxTemp = MaxDecl * tempRange/useRange
    scaledMinTemp = tempMin * tempRange/useRange
    return invTemps, scaledMinTemp, scaledMaxTemp
#    tempToUseScale = useRange/tempRange
#    return invTemps, tempToUseScale

# genUseFn Solar generation and use filename
def getGenUse(genUseFn:str) -> Tuple[List[dt.datetime], List[float], List[float]]:
    with open(genUseFn, 'r') as f:
        csvData = csv.reader(f)
        dateData = []
        genData = []
        useData = []
        for row in csvData:
            genColumnIndex = ord('B')-ord('A')
            useColumnIndex = ord('B')-ord('A')
            if '/' in row[0]:
                dateData.append(getDateMDY(row[0]))
                genData.append(float(row[genColumnIndex]))
                useData.append(float(row[useColumnIndex]))
               
    return dateData, genData, useData

def intround(x, resolution):
    return resolution * round(x/resolution)

# Column A is date, O is generation/day, P is Use/day
# genUseFn Solar generation and use filename
def plotAll(periodMeasurements:dict[str, List], temperatureFn:str) -> None:
    showAnnotations = True
    showTemperature = True
    dateData = periodMeasurements['Date']
    periodDays = periodMeasurements['PeriodDays']
    genData = periodMeasurements['Total Solar']
    useData = periodMeasurements['Total Use']
    if showTemperature:
        temperatureDates, lowTemperatures, highTemperatures = getTemperature(temperatureFn)
        temperatureDates, lowTemperatures, highTemperatures = weeklyTemps(
            temperatureDates, lowTemperatures, highTemperatures)
    declination = getDecl(9, MaxDecl, periodDays)

    fig = plt.figure()
    fig.set_size_inches(10, 7)

    fig.autofmt_xdate()
    temprColor = '#d0d0d0'
    ax = fig.gca()

    ax.grid(color='#eeeeee')
    ax.set_axisbelow(True)
    ax.tick_params(axis='x')

    ax.xaxis.set_major_locator(mdates.YearLocator(month=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    # minus sign gets rid of leading zero.
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%-m'))
    for tick in ax.xaxis.get_minor_ticks():
        tick.label.set_fontsize(8)

    plt.scatter(dateData, genData, label='Generation', s=4)
    plt.plot(dateData, genData)
    plt.scatter(dateData, useData, label='Use', s=4)
    plt.plot(dateData, useData)
    plt.scatter(dateData, declination, label='Declination', s=4)
    plt.plot(dateData, declination)
    plt.title('Solar Generation and Use - 3.24+.5 kW System')
    plt.ylabel('Avg. Daily Solar Generation and Energy Use (kWh)')

    for tick in ax.xaxis.get_major_ticks():
        tick.set_pad(8)

    if showTemperature:
        PlotLows = False
        if PlotLows:
            temperatures = lowTemperatures
            label = 'Avg. Daily Low Temp'
            yLabel = 'Avg. Daily Low Temperature (F)'
        else:   # avg daily temperature averaged for week
            temperatures = []
            for tempi, lowTemp in enumerate(lowTemperatures):
                temperatures.append((lowTemp + highTemperatures[tempi]) / 2)
            label = 'Avg. Daily Temp'
            yLabel = 'Inverted Avg. Daily Temperature (F)'
        invTemperatures, scaledMinTemp, scaledMaxTemp = scaleTemperatures(temperatures, useData)
#        invTemperatures, tempToUseScale = scaleTemperatures(temperatures, useData)
        plt.scatter(temperatureDates, invTemperatures, label=label,
	    c=temprColor, zorder=0, s=4)
        plt.plot(temperatureDates, invTemperatures, color=temprColor, zorder=0)

        axTemperature = ax.twinx()   # right side Y axis
        axTemperature.yaxis.set_label_position('right')
        axTemperature.yaxis.tick_right()
        axTemperature.set_ylabel(yLabel)

        old = False
        if old:
            tempYticks = numpy.linspace(0.85, 0.105, 10)
            tempYTemp = numpy.round(numpy.linspace(min(lowTemperatures), max(lowTemperatures), 10), 1)
        else:
            resolution = 1
            textRes = 5
##            minTemp = intround(0, resolution)
##            maxTemp = intround(MaxDecl * tempToUseScale, resolution)
##            numTemps = int((maxTemp-minTemp)/resolution)+1
##            tempYticks = numpy.linspace(maxTemp, minTemp, numTemps)
##            tempYTemp = [x for x in numpy.linspace(min(temperatures), max(temperatures), numTemps)]

            # Some real fudging here. Need to figure out pyplot details on axis.
            # So for now, print this, and if it is wrong by looking at graph, adjust numbers below.
            print('Min Temp, Max Temp, count', min(lowTemperatures), max(lowTemperatures),
                  max(lowTemperatures) - min(lowTemperatures))
            tempYTicks = []
            tempYTemp = []
            numTicks = 40
            startTick = 33
            endTick = 70
            for x in range(startTick, endTick):
                tempYTicks.append(endTick-x)
                if not (x % textRes):
                    tempYTemp.append(str(int(x)))
                else:
                    tempYTemp.append('')

    if showAnnotations:
        annotate(plt, fig, ax, dateData, '3/18/20', 'Covid', -0.05, .24)
        annotate(plt, fig, ax, dateData, '9/12/20', 'Fires', -0.02, .28)
        annotate(plt, fig, ax, dateData, '11/12/20', 'Heat Pump', .03, .24)
        annotate(plt, fig, ax, dateData, '3/30/21', 'Elec. Car', .01, .20)
        annotate(plt, fig, ax, dateData, '8/15/21', 'Fires', .065, .28)
        annotate(plt, fig, ax, dateData, '10/10/21', '+.5 kW', .08, .24)
        annotate(plt, fig, ax, dateData, '5/25/22', 'New .5 kW Inverter', .065, .28)

#        plt.yticks([0.85,0.105], [min(lowTemperatures), max(lowTemperatures)])
        if showTemperature:
            plt.yticks(tempYTicks, tempYTemp)
#    axTemperature.tick_params(axis='y', labelcolor=temprColor)

    ax.legend()
#    axRight.legend()
    ax.set_ylim(ymin=0)
    plt.savefig('SolGenIrrad.svg', bbox_inches='tight')

# The xFudgePerc moves left a bit and can be used to adjust X for size of text, etc.
def annotate(plt, fig, ax, dateData, date, text, xFudgePerc, yPerc):
    bbox = ax.yaxis.get_tightbbox(fig.canvas.get_renderer())
    rightMarginWidth = (bbox.x1-bbox.x0)
    # leftAxisPerc is about 0.05 or 5%.
    leftAxisPerc = rightMarginWidth / (fig.get_size_inches()[0] * fig.dpi) + xFudgePerc
    datePerc = calcDatePercent(getDateMDY(date), dateData)
    # These move all annotations horizontally and vertically
    datePerc *= 0.91    # Graph may go longer than dateData.
    yPerc *= 0.78       # Height of graph changes also.
    plt.annotate(xy=[datePerc-leftAxisPerc, yPerc], text=text, xycoords='figure fraction')
