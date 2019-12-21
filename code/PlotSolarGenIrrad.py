#!/usr/bin/env python
import datetime as dt
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as numpy
import math as math
import csv as csv

def getDateMDY(dateStr):
    return dt.datetime.strptime(dateStr, '%m/%d/%y')

def getDateYMD(dateStr):
    return dt.datetime.strptime(dateStr, '%Y/%m/%d')

# Generates weekly declination.
# The declination of the sun is the angle between a plane perpendicular
# to a line between the earth and the sun and the earth's axis.
# https://www.itacanet.org/the-sun-as-a-source-of-energy/part-3-calculating-solar-angles/
#def getDecl(minGen:float, maxGen:float, numDays:int):
def getDecl(minGen, maxGen, numDays):
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
    numWeeks = numDays/7
    for timeIndex in range(0, numWeeks):
	declIndex = timeIndex + dateShift
	if declIndex >= 52:
	    declIndex -= 52
	weekDecl.append(declination[declIndex*7] * kwhMult + kwhOffset)
    return weekDecl

# Averages temperatures from daily into weekly temperatures.
def weeklyTemps(dates, lowTemps, highTemps):
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

def getTemperature(fn):
    with open(fn, 'r') as f:
        csvData = csv.reader(f)
        dates = []
        lowTemps = []
        highTemps = []
        for row in csvData:
            if len(row) > 2:
		dates.append(getDateYMD(row[0]))
		lowTemps.append(int(row[2]))
		highTemps.append(int(row[1]))
    return dates, lowTemps, highTemps

# scale temperatures to usage kWh data
def scaleTemperatures(lowTemps, use):
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

def getGenUse(genUseFn):
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
def plotAll(genUseFn, temperatureFn):
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

# This only displays years. It displayed full string when axis was string instead of datetime.
#    numWeeks = (dateData[-1] - dateData[0]).days / 14
#    ax.xaxis.set_major_locator(plt.MaxNLocator(numWeeks))

    plt.scatter(dateData, genData, label='Generation')
    plt.plot(dateData, genData)
    plt.scatter(dateData, useData, label='Use')
    plt.plot(dateData, useData)
    plt.scatter(dateData, declination, label='Declination')
    plt.plot(dateData, declination)
    plt.ylabel('kWh')

    if showTemperature:
        invLowTemperatures = scaleTemperatures(lowTemperatures, useData)
        plt.scatter(temperatureDates, invLowTemperatures, label='Inverted Low Temperature',
	    c=temprColor, zorder=0)
        plt.plot(temperatureDates, invLowTemperatures, color=temprColor, zorder=0)

        axTemperature = ax.twinx()   # right side Y axis
        axTemperature.yaxis.set_label_position('right')
        axTemperature.yaxis.tick_right()
        axTemperature.set_ylabel('Inverted Low Temperature')
	tempYticks = numpy.linspace(0.85, 0.105, 10)
	tempYTemp = numpy.round(numpy.linspace(min(lowTemperatures), max(lowTemperatures), 10), 1)
#        plt.yticks([0.85,0.105], [min(lowTemperatures), max(lowTemperatures)])
	plt.yticks(tempYticks, tempYTemp)
#    axTemperature.tick_params(axis='y', labelcolor=temprColor)

    ax.legend()
#    axRight.legend()
    plt.savefig('SolGenIrrad.svg')



if __name__ == "__main__":
	plotAll('../SolarGeneration.csv')

