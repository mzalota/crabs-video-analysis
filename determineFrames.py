import math

import csv
import pandas as pd


def determineFrames():

    rootDirectory = "C:/workspaces/AnjutkaVideo/output/"

    framesFilePath = rootDirectory+"/V5__R_20180915_211343_toCut_2.csv"

    #cutFramesFilePath = rootDirectory+"/V5__R_20180915_211343_framesToCut_aaaa.csv"
    #cutFramesFile = open(cutFramesFilePath, 'wb')

    # Creating an empty Dataframe with column names only
    #dfObj = pd.DataFrame(columns=['FrameNumber', 'UserName', 'Action'])
    dfObj = pd.DataFrame(columns=['frameNumber', 'count'])
    #print("Dataframe Contens ", dfObj)

    yDrift = 0
    frameNumber = 0
    prevFrameNumber= 0
    cumulativeDrift = 0
    printedFrames = 1
    prevFrameToUse = 0
    with open(framesFilePath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print('Column names are: '+", ".join(row))
                line_count += 1
            else:
                prevFrameNumber = frameNumber
                prevYDrift = yDrift

                frameNumber = row[0]
                yDrift = float(row[1].replace(",","."))

                prevCumulativeDrift = cumulativeDrift
                cumulativeDrift += yDrift

                driftPerFrame = yDrift/(int(frameNumber)-int(prevFrameNumber))
                #print (frameNumber, yDrift, cumulativeDrift, prevFrameNumber, prevYDrift, prevCumulativeDrift, driftPerFrame)

                nextFrameBreak= 1080*printedFrames
                if cumulativeDrift > (nextFrameBreak):
                    pixelsToBacktrack = cumulativeDrift - nextFrameBreak
                    framesToBacktrack = pixelsToBacktrack/driftPerFrame
                    frameToUse = int(frameNumber)-math.floor(framesToBacktrack)
                    frameJump = frameToUse - prevFrameToUse
                    print (int(frameToUse), printedFrames, frameJump, cumulativeDrift, pixelsToBacktrack, framesToBacktrack, math.floor(framesToBacktrack))
                    printedFrames = printedFrames+1
                    prevFrameToUse = frameToUse

                    dfObj = dfObj.append({'frameNumber': int(frameToUse), 'count': line_count}, ignore_index=True)

                    #cutFramesFile.write(str(int(frameToUse)) + "\n")
                    #cutFramesFile.flush()

                line_count += 1
        print('Processed '+str(line_count)+' lines.')

    #print("Dataframe Contens ", dfObj)
    return dfObj
    #cutFramesFile.close()

framesToSaveToFile = determineFrames()
print("Dataframe Contens ", framesToSaveToFile)


#for index, row in framesToSaveToFile.head(n=5).iterrows():
for index, row in framesToSaveToFile.iterrows():
     print(index, row['frameNumber'],row['count'])
