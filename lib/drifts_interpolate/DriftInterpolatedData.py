import math

import pandas as pd

from lib.data.PandasWrapper import PandasWrapper
from lib.model.Vector import Vector
from lib.infra.FolderStructure import FolderStructure


class DriftInterpolatedData(PandasWrapper):
    # __driftData = None
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftData):
        # type: (pd.DataFrame) -> DriftInterpolatedData
        self.setDF(driftData)

    def setDF(self, driftData):
        # type: (pd.DataFrame) -> None
        self.__driftData = self.__sort_by_frameNumber(driftData)
        self.__initializePerfOptimizingVariables()

    def __sort_by_frameNumber(self, driftData):
        df_tmp = driftData.copy().sort_values(by=[self.__COLNAME_frameNumber])
        return df_tmp.reset_index(drop=True)

    def __initializePerfOptimizingVariables(self):
        df_copy = self.__driftData.copy()
        dfIndexIsFrameNumber = df_copy.reset_index().set_index(self.__COLNAME_frameNumber)
        self.__indexDict = dfIndexIsFrameNumber["index"].to_dict()

        self.__maxFrameID = self.__driftData[self.__COLNAME_frameNumber].max()
        self.__minFrameID = self.__driftData[self.__COLNAME_frameNumber].min()
        self.__driftXDict = self.__driftData[self.__COLNAME_driftX].to_dict()
        self.__driftYDict = self.__driftData[self.__COLNAME_driftY].to_dict()
        self.__frameIDDict = self.__driftData[self.__COLNAME_frameNumber].to_dict()

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> DriftInterpolatedData
        filepath = folderStruct.getDriftsFilepath()
        if folderStruct.fileExists(filepath):
            df = PandasWrapper.readDataFrameFromCSV(filepath)
            # dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum
        else:
            df = DriftInterpolatedData.__createEmptyDF()

        return DriftInterpolatedData(df)

    @staticmethod
    def __createEmptyDF():
        column_names = [DriftInterpolatedData.__COLNAME_frameNumber,
                        DriftInterpolatedData.__COLNAME_driftX,
                        DriftInterpolatedData.__COLNAME_driftY]
        df = pd.DataFrame(columns=column_names)
        return df

    @staticmethod
    def createFromDataFrame(driftData):
        # type: (pd.DataFrame) -> DriftInterpolatedData
        return DriftInterpolatedData(driftData)

    def saveToFile(self, filepath):
        # type: (String) -> None
        self.getDF().to_csv(filepath, sep='\t', index=False)

    def getDF(self):
        # type: () -> pd.DataFrame
        return self.__driftData

    def getCount(self):
        return len(self.__driftData.index)

    def __getXDrift(self, index):
        return self.__driftXDict[index]

    def __getYDrift(self, index):
        return self.__driftYDict[index]

    def __getFrameID(self, index):
        return self.__frameIDDict[index]

    def __getIndexOfFrame(self, frameID):
        if frameID in self.__indexDict:
            return self.__indexDict[frameID]
        else:
            return None

    def __pixelsYDriftPerFrame(self, index):
        if index <= 0:
            return 0

        numberOfFramesJumped = self.__numberOfFramesFromPrevIndex(index)
        driftPerFrame = self.__getYDrift(index) / numberOfFramesJumped
        return driftPerFrame

    def __pixelsXDriftPerFrame(self, index):
        if index <= 0:
            return 0

        numberOfFramesJumped = self.__numberOfFramesFromPrevIndex(index)
        driftPerFrame = self.__getXDrift(index) / numberOfFramesJumped
        return driftPerFrame

    def __numberOfFramesFromPrevIndex(self, index):
        prevFrameNumber = self.__getFrameID(index - 1)
        frameNumber = self.__getFrameID(index)
        numberOfFramesJumped = (int(frameNumber) - int(prevFrameNumber))
        return numberOfFramesJumped

    def __frameIDThatIsYPixelsAwayFromIndex(self, frameID, pixelsAway):
        index = self.__getIndexOfFrame(frameID)
        driftPerFrame = self.__pixelsYDriftPerFrame(index)
        if driftPerFrame == 0:
            framesToBacktrack = 0
        else:
            framesToBacktrack = math.floor(pixelsAway / driftPerFrame)

        frameID = int(self.__getFrameID(index))
        frameToUse = frameID - framesToBacktrack

        return frameToUse

    def __driftToNearbyFrame(self, index, nearbyFrameID):

        framesToJump = int(self.__getFrameID(index)) - nearbyFrameID

        yPixelsDriftPerFrame = self.__pixelsYDriftPerFrame(index)
        yPixelsAway = math.floor(yPixelsDriftPerFrame * framesToJump)

        xPixelsDriftPerFrame = self.__pixelsXDriftPerFrame(index)
        xPixelsAway = math.floor(xPixelsDriftPerFrame * framesToJump)

        return Vector(xPixelsAway, yPixelsAway)

    def __nextFrameIDInFile(self, frameID):
        if int(frameID) >= int(self.maxFrameID()):
            return self.maxFrameID()

        if int(frameID) <= int(self.minFrameID()):
            return self.minFrameID()

        index = self.__getIndexOfFrame(frameID)
        while index is None:
            frameID += 1
            index = self.__getIndexOfFrame(frameID)

        return frameID

    def maxFrameID(self):
        return self.__maxFrameID

    def minFrameID(self):
        return self.__minFrameID

    def _yPixelsBetweenFrames(self, fromFrameID, toFrameID):
        drift = self.__driftBetweenFrames(fromFrameID, toFrameID)
        if drift is None:
            return None

        return drift.y

    def __driftBetweenFrames(self, fromFrameID, toFrameID):
        # type: (int, int) -> Vector

        if fromFrameID < self.minFrameID() or toFrameID < self.minFrameID():
            # return Vector(0,0)
            return None

        if fromFrameID > self.maxFrameID() or toFrameID > self.maxFrameID():
            # return Vector(0, 0)
            return None

        if (fromFrameID > toFrameID):
            drift = self.__driftBetweenFrames(toFrameID, fromFrameID)
            return Vector(-(drift.x), -(drift.y))

        if (fromFrameID == toFrameID):
            return Vector(0, 0)

        return self.__getDriftBetweenTwoFramesPixels(fromFrameID, toFrameID)

    def __getDriftBetweenTwoFramesPixels(self, fromFrameID, toFrameID):

        # assuming fromFrameID is less than or equal to toFrameID and both are within valid range
        startingFrameIDInDataFrame = self.__nextFrameIDInFile(fromFrameID)
        startIndex = self.__getIndexOfFrame(startingFrameIDInDataFrame)
        endingFrameIDInDataFrame = self.__nextFrameIDInFile(toFrameID)
        endIndex = self.__getIndexOfFrame(endingFrameIDInDataFrame)

        driftToStartingFrame = self.__driftToNearbyFrame(startIndex, fromFrameID)

        cumulativeDrift = self.__driftBetweenFramesInDataFrame(endIndex, startIndex)

        driftFromEndingFrame = self.__driftToNearbyFrame(endIndex, toFrameID)

        totalYDrift = cumulativeDrift.y + driftToStartingFrame.y - driftFromEndingFrame.y
        totalXDrift = cumulativeDrift.x + driftToStartingFrame.x - driftFromEndingFrame.x

        return Vector(totalXDrift, totalYDrift)

    def __driftBetweenFramesInDataFrame(self, endIndex, nextIndex):
        cumulativeYDrift = 0
        cumulativeXDrift = 0
        while nextIndex < endIndex:
            nextIndex = nextIndex + 1
            cumulativeYDrift += self.__getYDrift(nextIndex)
            cumulativeXDrift += self.__getXDrift(nextIndex)
        return Vector(cumulativeXDrift, cumulativeYDrift)

    def getNextFrame(self, yPixelsAway, fromFrameID):
        # type: (int, int) -> int

        startingFrameIDInDataFrame = self.__nextFrameIDInFile(fromFrameID)
        startingFrameIndex = self.__getIndexOfFrame(startingFrameIDInDataFrame)

        driftToStartingFrame = self.__driftToNearbyFrame(startingFrameIndex, fromFrameID)
        yPixelsToStartingFrame = driftToStartingFrame.y

        nextFrameIDInDataFrame = startingFrameIDInDataFrame
        cumulativeYDrift = yPixelsToStartingFrame
        while cumulativeYDrift < yPixelsAway and nextFrameIDInDataFrame < self.maxFrameID():
            # keep checking next frameID in DataFrame until found one that is just a bit further away from "fromFrameID" than "pixelsAway"
            # print("DriftData::getNextFrame nextFrameIDInDataFrame", nextFrameIDInDataFrame)
            nextIndex = self.__getIndexOfFrame(nextFrameIDInDataFrame) + 1
            nextFrameIDInDataFrame = self.__getFrameID(nextIndex)
            cumulativeYDrift += self.__getYDrift(nextIndex)

        # go back zero-to-four frames to minimize the number of pixels overshot.
        pixelsToBacktrack = cumulativeYDrift - yPixelsAway
        searchedFrameID = self.__frameIDThatIsYPixelsAwayFromIndex(nextFrameIDInDataFrame, pixelsToBacktrack)

        if searchedFrameID < self.minFrameID():
            searchedFrameID = self.minFrameID()

        if searchedFrameID >= self.maxFrameID():
            searchedFrameID = self.maxFrameID()

        return searchedFrameID
