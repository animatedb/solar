#!/usr/bin/env python
import datetime as dt
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv

def getDateMDY(dateStr:str) -> dt.datetime:
    return dt.datetime.strptime(dateStr, '%m/%d/%y')

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
                dateData.append(getDateMDY(row[0]))
                genData.append(float(row[genIndex]))
                useData.append(float(row[ord('P')-ord('A')]))
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

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        plt.scatter(dateData, genData, label='Generation')
        plt.plot(dateData, genData)
        plt.scatter(dateData, useData, label='Use')
        plt.plot(dateData, useData)

        ax.legend()

#        plt.xlabel('Date')
        plt.ylabel('kWh')
#        plt.savefig('SolGenUse.png')
        plt.savefig('SolGenUse.svg')

def plotTotalSurplus(fn):
    with open(fn, 'r') as f:
        csvData = csv.reader(f)
        dateData = []
        surpData = []
        for row in csvData:
            surpIndex = ord('R')-ord('A')
            if row[surpIndex] and row[0] != 'Date':
                dateData.append(getDateMDY(row[0]))
                surpData.append(float(row[surpIndex]))
        fig = plt.figure()
        fig.set_size_inches(10, 7)
        ax = fig.gca()
        fig.autofmt_xdate()
        ax.grid(color='#eeeeee')
        ax.set_axisbelow(True)
        ax.tick_params(axis='x', rotation=65)

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        plt.scatter(dateData, surpData, label='Balance')
        plt.plot(dateData, surpData)
        ax.legend()
        plt.ylabel('kWh')
        plt.savefig('SolBalance.svg')



if __name__ == "__main__":
	plotDailyGenUse('SolarGeneration.csv')
	plotTotalSurplus('SolarGeneration.csv')

