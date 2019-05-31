import csv
import pandas as pd
import math

from DriftData import DriftData


class FramesStitcher:
    #__image = None

    def __init__(self):
        # type: () -> FramesStitcher

        # Creating an empty Dataframe with column names only
        self.__framesToStitch = pd.DataFrame(columns=['frameNumber', 'cumulativeDrift'])

    def determineFrames(self, rootDirectory, csvFileName):

        framesFilePath = rootDirectory + "/" + csvFileName + ".csv"

        driftData = pd.read_csv(framesFilePath, delimiter="\t", na_values="(null)")
        self.__processRows(driftData)

        return self.__framesToStitch

    def __processRows(self, ddFile):


        cumulativeDrift = 0

        driftData = DriftData(ddFile)

        self.__addNextFrame(driftData.getFrameID(0), 0)

        line_count =0
        for index in range(1, driftData.getCount()):

            yDrift = driftData.getYDrift(index)  #float(row[2].replace(",", "."))
            cumulativeDrift += yDrift

            #print (driftData.getFrameID(index), yDrift, cumulativeDrift, self.__nextCumulativeDriftToStop(), driftData.pixelsDriftPerFrame(index), index)
            if cumulativeDrift >= self.__nextCumulativeDriftToStop():
                self.__addFrameToStitch(cumulativeDrift, driftData, index)

            line_count+=1

        print('Processed ' + str(line_count) + ' lines.')


    def __addFrameToStitch(self, cumulativeDrift, dd, index):

        pixelsToBacktrack = cumulativeDrift - self.__nextCumulativeDriftToStop()
        frameIDToStitch = dd.frameIDThatIsPixelsAwayFromIndex(index, pixelsToBacktrack)

        pixelsActuallyBacktracked  = dd.pixelsToFrameIDFromIndex(index, frameIDToStitch)

        cumulativeDriftForUsedFrame = int(cumulativeDrift - pixelsActuallyBacktracked)
        #print ("addingToResult", int(frameIDToStitch), cumulativeDrift, cumulativeDriftForUsedFrame, pixelsToBacktrack, pixelsActuallyBacktracked)

        self.__addNextFrame(frameIDToStitch, cumulativeDriftForUsedFrame)

    def __nextCumulativeDriftToStop(self):
        indexOfLastFrameToStitch = len(self.__framesToStitch.index) - 1
        lastCumulativeDrift = int(self.__framesToStitch['cumulativeDrift'][indexOfLastFrameToStitch])
        nextCumulativeDriftToStop = lastCumulativeDrift + 1080
        return nextCumulativeDriftToStop

    def __addNextFrame(self, frameID, cumulativeDrift):
        self.__framesToStitch = self.__framesToStitch.append({'frameNumber': int(frameID), 'cumulativeDrift': cumulativeDrift}, ignore_index=True)


