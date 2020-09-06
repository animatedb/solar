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

def getDateMDY(dateStr:str) -> dt.datetime:
    return dt.datetime.strptime(dateStr, '%m/%d/%y')

def getDateYMD(dateStr:str) -> dt.datetime:
    return dt.datetime.strptime(dateStr, '%Y/%m/%d')

# Generates weekly declination.
# The declination of the sun is the angle between a plane perpendicular
# to a line between the earth and the sun and the earth's axis.
# https://www.itacanet.org/the-sun-as-a-source-of-energy/part-3-calculating-solar-angles/
def getDecl(minGen:float, maxGen:float, numDays:int) -> List[float]:
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
    numWeeks = int(numDays/7)
    for timeIndex in range(0, numWeeks):
        declIndex = timeIndex + dateShift
        weekDecl.append(declination[declIndex%52*7] * kwhMult + kwhOffset)
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
# use Solar use data
def scaleTemperatures(lowTemps:List[int], use:List[float]) -> List[float]:
    invLowTemps = []
    lowMin = min(lowTemps)
    lowRange = max(lowTemps) - lowMin
    useLow = min(use)
    useRange = max(use) - useLow
    for t in lowTemps:
        invLowTemps.append(t * useRange/lowRange)
    invLow = min(invLowTemps)
    invRange = max(invLowTemps) - invLow
    for i, t in enumerate(lowTemps):
        invLowTemps[i] = invRange - (invLowTemps[i] - invLow) + useLow
    return invLowTemps

# genUseFn Solar generation and use filename
def getGenUse(genUseFn:str) -> Tuple[List[dt.datetime], List[float], List[float]]:
    with open(genUseFn, 'r') as f:
        csvData = csv.reader(f)
        dateData = []
        genData = []
        useData = []
        for row in csvData:
            genIndex = ord('O')-ord('A')
            if row[genIndex] and row[0] != 'Date':
                dateData.append(getDateMDY(row[0]))
                genData.append(float(row[genIndex]))
                useData.append(float(row[ord('P')-ord('A')]))
    return dateData, genData, useData

# Column A is date, O is generation/day, P is Use/day
# genUseFn Solar generation and use filename
def plotAll(genUseFn:str, temperatureFn:str) -> None:
    showTemperature = True
    dateData, genData, useData = getGenUse(genUseFn)
    if showTemperature:
        temperatureDates, lowTemperatures, highTemperatures = getTemperature(temperatureFn)
        temperatureDates, lowTemperatures, highTemperatures = weeklyTemps(
            temperatureDates, lowTemperatures, highTemperatures)
    declination = getDecl(9, 24, len(dateData)*7)

    fig = plt.figure()
    fig.set_size_inches(10, 7)

    fig.autofmt_xdate()
    temprColor = '#d0d0d0'
    ax = fig.gca()

    ax.grid(color='#eeeeee')
    ax.set_axisbelow(True)
    ax.tick_params(axis='x', rotation=65)

#    numWeeks = (dateData[-1] - dateData[0]).days / 7
#    ax.xaxis.set_major_locator(plt.MaxNLocator(numWeeks))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.scatter(dateData, genData, label='Generation')
    plt.plot(dateData, genData)
    plt.scatter(dateData, useData, label='Use')
    plt.plot(dateData, useData)
    plt.scatter(dateData, declination, label='Declination')
    plt.plot(dateData, declination)
    plt.title('Solar Generation and Use')
    plt.ylabel('kWh')

    if showTemperature:
        PlotLows = False
        if PlotLows:
            temperatures = lowTemperatures
            label = 'Avg. Daily Low Temp'
            yLabel = 'Avg. Daily Low Temperature (F)'
        else:   # avg daily temperature averaged for week
            temperatures = []
            for tempi, lowTemp in enumerate(lowTemperatures):
                temperatures.append(lowTemp + highTemperatures[tempi])
            label = 'Avg. Daily Temp'
            yLabel = 'Avg. Daily Temperature (F)'
        invTemperatures = scaleTemperatures(temperatures, useData)
        plt.scatter(temperatureDates, invTemperatures, label=label,
	    c=temprColor, zorder=0)
        plt.plot(temperatureDates, invTemperatures, color=temprColor, zorder=0)

        axTemperature = ax.twinx()   # right side Y axis
        axTemperature.yaxis.set_label_position('right')
        axTemperature.yaxis.tick_right()
        axTemperature.set_ylabel(yLabel)
        tempYticks = numpy.linspace(0.85, 0.105, 10)
        tempYTemp = numpy.round(numpy.linspace(min(lowTemperatures), max(lowTemperatures), 10), 1)
#        plt.yticks([0.85,0.105], [min(lowTemperatures), max(lowTemperatures)])
        plt.yticks(tempYticks, tempYTemp)
#    axTemperature.tick_params(axis='y', labelcolor=temprColor)

    ax.legend()
#    axRight.legend()
    plt.savefig('SolGenIrrad.svg', bbox_inches='tight')



if __name__ == "__main__":
	plotAll('../SolarGeneration.csv', 'Temperature/Source/noaa.csv')

