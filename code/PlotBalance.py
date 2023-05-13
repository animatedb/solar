import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List


def plotTotalSurplus(periodMeasurements:dict[str, List]):
#	dateData = []
#	surpData = []
#	for row in csvData:
#	    totalSurplusColIndex = 'U'
#	    surpIndex = ord(totalSurplusColIndex)-ord('A')
#	    if row[surpIndex] and row[0] != 'Date':
#		dateData.append(getDateMDY(row[0]))
#		surpData.append(float(row[surpIndex]))
    dateData = periodMeasurements['Date']
    meterData = periodMeasurements['Main Meter']

    fig = plt.figure()
    fig.set_size_inches(10, 7)
    ax = fig.gca()
    fig.autofmt_xdate()
    ax.grid(color='#eeeeee')
    ax.set_axisbelow(True)

    newDate = True
    if newDate:
        ax.xaxis.reset_ticks()
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)	# Pad in vertical points
        ax.tick_params(axis='x', rotation=0)
        ax.xaxis.set_major_locator(mdates.YearLocator(month=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        # minus sign gets rid of leading zero.
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%-m'))
        for tick in ax.xaxis.get_minor_ticks():
            tick.label.set_fontsize(8)
    else:
        ax.tick_params(axis='x', rotation=65)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.scatter(dateData, meterData, label='Balance')
    plt.plot(dateData, meterData)
    ax.legend()
    plt.ylabel('kWh')
    plt.savefig('SolBalance.svg')
