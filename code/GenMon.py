#!/usr/bin/env python3
# mypy --strict
import datetime as dt
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as numpy
import math as math
import csv as csv
from typing import Dict, List, Tuple

def getDateMDY(dateStr:str) -> dt.datetime:
    return dt.datetime.strptime(dateStr, '%m/%d/%y')

def getRowColumn(row, column:str) -> float:
    return float(row[ord(column)-ord('A')])

def getDailyGenUse(genMonFn:str) -> Tuple[List[dt.datetime], Dict[str, float]]:
    # Columns are ordered generally for least stable values first/at bottom.
    # Order by most variation at the top of the stack?
    dateColumn = 'A'
    columns = (
        ('Gen Roof', 'N'),
        ('Gen Ground', 'O'),
        ('Use Other', 'T'),
        ('Use Bath Heat', 'R'),
        ('Use Living Heat', 'Q'),
        ('Use Car', 'P'),
        )
    dates:List[dt.datetime] = []
    genUseData:Dict[List[float]] = {}
    with open(genMonFn, 'r') as f:
        csvData = csv.reader(f)
        for rowi, row in enumerate(csvData):
            if rowi > 4:    # Skip header rows
                dateColIndex = ord(dateColumn) - ord('A')
                dates.append(getDateMDY(row[dateColIndex]))
                csvData = csv.reader(f)
                for col in columns:
                    if col[0] not in genUseData:
                        genUseData[col[0]]:List[float] = []
                    genUseData[col[0]].append(getRowColumn(row, col[1]))
    return dates, genUseData

def plot(genMonFn:str):
    dates, genUse = getDailyGenUse(genMonFn)
    # gen
    genKeys = [key for key in genUse.keys() if 'Gen' in key]
    useKeys = [key for key in genUse.keys() if 'Use' in key]
#    gen = { key:genUse[key] for key in genKeys }
    gen = [ genUse[key] for key in genKeys ]
    use = [ genUse[key] for key in useKeys ]
    totalGen = [x + y for x, y in zip(gen[0], gen[1])]

    fig = plt.figure()
    fig.set_size_inches(10, 7)
    fig.autofmt_xdate()
    ax = fig.gca()
    ax.set_axisbelow(True)
#    ax.xaxis.set_major_locator(mdates.YearLocator(month=6))
#    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    useLabels = [ x.replace('Use ', '') for x in useKeys]
    ax.stackplot(dates, *use, labels=useLabels)

    roofGenColor = '#B0B0B0'
    roofGen = genUse['Gen Roof']
    plt.scatter(dates, roofGen, label='Roof Gen .6 kW', color=roofGenColor, s=8)
    plt.plot(dates, roofGen, color=roofGenColor)

    totalGenColor = '#000000'
    plt.scatter(dates, totalGen, label='Total Gen', color=totalGenColor, s=8)
    plt.plot(dates, totalGen, color=totalGenColor)

    ax.legend()
    plt.title('Solar Generation and Use - 3.24+.6 kW System')
    plt.ylabel('Daily Solar Generation and Energy Use (kWh)')
    plt.savefig('ElecGenMon.svg', bbox_inches='tight')

if __name__ == "__main__":
    plot('../ElecGenMon.csv')

