import csv
import pandas as pd
import math

from DriftData import DriftData


class FramesStitcher:
    #__heightOfFrame = None
    #__framesToStitch = None

    def __init__(self):
        # type: () -> FramesStitcher

        self.__heightOfFrame = 1080
        # Creating an empty Dataframe with column names only
        self.__framesToStitch = pd.DataFrame(columns=['frameNumber'])

    def determineFrames(self, rootDirectory, csvFileName):

        framesFilePath = rootDirectory + "/" + csvFileName + ".csv"

        ddFile = pd.read_csv(framesFilePath, delimiter="\t", na_values="(null)")
        ddFile = ddFile.rename(columns={ddFile.columns[0]: "rowNum"}) # rename first column to be rowNum

        driftData = DriftData(ddFile)
        self.__constructFramesToStitch(driftData)

        return self.__framesToStitch

    def __constructFramesToStitch(self, driftData):

        nextFrameID = driftData.getFrameID(0)
        while nextFrameID < driftData.maxFrameID():
            #print ("nextFrameID", nextFrameID)
            self.__addNextFrame(nextFrameID)
            nextFrameID = driftData.getNextFrame(self.__heightOfFrame, nextFrameID)
        self.__addNextFrame(driftData.maxFrameID())

    def __addNextFrame(self, frameID):
        self.__framesToStitch = self.__framesToStitch.append({'frameNumber': int(frameID)}, ignore_index=True)


