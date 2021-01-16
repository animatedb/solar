#!/usr/bin/env python3
import os as os

def convertFile(inFileName, outFile):
    print(inFileName)
    year = inFileName.split('-')[1]
    with open(inFileName, 'r') as inFile:
        for line in inFile.readlines():
            # The lines don't have carriage returns, so split on
            # the year.
            # This requires the following column order:
            #   Year, Month, Day, Max Temp, Min Temp, the following are ignored
            # After the split, the year is removed, and we don't need rain, etc.
            rows = line.split(year)
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
    with open(os.path.join(path, 'noaa.csv'), 'w') as outFile:
        for file in sorted(os.listdir(path)):
            name, ext = os.path.splitext(file)
            if ext == '.txt':
                inFn = os.path.join(path, file)
                convertFile(inFn, outFile)

if __name__ == "__main__":
    convertNoaa()
