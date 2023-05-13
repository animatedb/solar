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
    print(periodMeasurements.keys())

    fig = plt.figure()
    fig.set_size_inches(10, 7)
    ax = fig.gca()
    fig.autofmt_xdate()
    ax.grid(color='#eeeeee')
    ax.set_axisbelow(True)
    ax.tick_params(axis='x', rotation=65)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.scatter(dateData, meterData, label='Balance')
    plt.plot(dateData, meterData)
    ax.legend()
    plt.ylabel('kWh')
    plt.savefig('SolBalance.svg')
