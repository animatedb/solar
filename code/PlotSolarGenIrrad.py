#!/usr/bin/env python
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import math
import csv

# Generates weekly declination.
# The declination of the sun is the angle between a plane perpendicular
# to a line between the earth and the sun and the earth's axis.
#def plotDecl(minGen:float, maxGen:float, numDays:int):
def plotDecl(minGen, maxGen, numDays):
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
    dateShift = int(52*8.05/12)
    numWeeks = numDays/7
    for timeIndex in range(0, numWeeks):
	declIndex = timeIndex + dateShift
	if declIndex >= 52:
	    declIndex -= 52
	weekDecl.append(declination[declIndex*7] * kwhMult + kwhOffset)
    return weekDecl

# Column A is date, O is generation/day, P is Use/day
def plotDailyGenUse(fn):
    with open(fn, 'r') as f:
        csvData = csv.reader(f)
        dateData = []
        genData = []
        useData = []
        for row in csvData:
            genIndex = ord('O')-ord('A')
            if row[genIndex] and row[0] != 'Date':
                dateData.append(row[0])
                genData.append(float(row[genIndex]))
                useData.append(float(row[ord('P')-ord('A')]))
	declination = plotDecl(9, 24, len(dateData)*7)
#	print(dateData)
#	print(genData)
#        plt.locator_params(axis='x', nbins=12)	# doesn't work for dates

	fig = plt.figure()
	fig.set_size_inches(10, 7)
	ax = fig.gca()
        fig.autofmt_xdate()
        ax.grid(color='#eeeeee')
	ax.set_axisbelow(True)
	ax.tick_params(axis='x', rotation=65)


        plt.scatter(dateData, genData, label='Generation')
	plt.plot(dateData, genData)
        plt.scatter(dateData, useData, label='Use')
	plt.plot(dateData, useData)
        plt.scatter(dateData, declination, label='Declination')
	plt.plot(dateData, declination)

        ax.legend()
        plt.savefig('SolGenIrrad.svg')


plotDailyGenUse('../SolarGeneration.csv')

#if __name__ == "__main__":
#    main()

