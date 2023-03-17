#!/usr/bin/env python3
import os as os

def convertFile(inFileName, outFile):
    print(inFileName)
    year = inFileName.split('-')[1]
    singleLine = ''
    with open(inFileName, 'r') as inFile:
        # The lines in some files don't have carriage returns,
        # so make one line that has all rows no matter what the
        # file input format is.
        #
        # All of the following formats are combined into a single line.
        # Format 1: Up to 2021-03
        #   2021030170430.002021030267400.002021030370460.002021030467420 ...
        # Format 2: 2021-04 to 2021-09
        #   2021\n04\n01\n85\n49\n0.00\n2021\n04\n02\n71\n48\n0.00 ...
        # Format 3: 2021-10 to now
        #   2021 10 01 89 55 0.00\n2021 10 02 89 57 0.00
        for line in inFile.readlines():
            singleLine += line.rstrip().replace(' ', '')

    # The lines in some files don't have carriage returns, so split on
    # the year.
    # This requires the following column order:
    #   Year, Month, Day, Max Temp, Min Temp, the following are ignored
    # After the split, the year is removed, and we don't need rain, etc.
    rows = singleLine.split(year)
    goodRow = ''
    for rowNum, row in enumerate(rows[1:]):
        args = []
        args.append(year)
        # If the max and min are blank, no characters are
        # present, and the length is greater or equal to 8.
        # If it is 8, the previous goodRow is used.
        # If the rain column is a trace, it is 'T' and length is 9.
        if len(row) >= 12:
            goodRow = row
        elif len(row) == 9:
            goodRow = row.replace('T', '0.01')
        else:
            print(goodRow)
        for index in range(0, 4):
            argStr = goodRow[index*2:index*2+2]
            try:
                args.append(str(int(argStr)))
            except:
                print('Bad Format: ', inFileName, rowNum, goodRow)
                exit()
        date = '/'.join(args[0:3])
        print(','.join([date, args[3], args[4]]), file=outFile)

def convertNoaa():
    path = 'Source'
    with open(os.path.join(path, '../noaa.csv'), 'w') as outFile:
        for file in sorted(os.listdir(path)):
            name, ext = os.path.splitext(file)
            if ext == '.txt':
                inFn = os.path.join(path, file)
                convertFile(inFn, outFile)

if __name__ == "__main__":
    convertNoaa()
