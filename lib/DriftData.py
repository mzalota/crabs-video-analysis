import math

import numpy
import pandas as pd

from lib.MyTimer import MyTimer
from lib.common import Vector
from lib.FolderStructure import FolderStructure


class DriftData:
    #__driftData = None
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftData):
        # type: (pd.DataFrame) -> DriftData

        self.__driftData = self.__sort_by_frameNumber(driftData)

        self.__initializePerfOptimizingVariables()

        #print(driftData.count())

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
    def createFromFile(folderStruct):
        # type: (FolderStructure) -> DriftData
        filepath = folderStruct.getDriftsFilepath()
        dfRaw = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
        #dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum

        return DriftData(dfRaw)

    @staticmethod
    def createFromDataFrame(driftData):
        # type: (pd.DataFrame) -> DriftData
        return DriftData(driftData)

    def saveToFile(self,filepath):
        # type: (String) -> None
        #self.getDF().to_csv(filepath, sep='\t', index=False)
        self.getDF().to_csv(filepath, sep='\t', index=False)

    def getDF(self):
        # type: () -> pd.DataFrame
        return self.__driftData

    def getInterpolatedDF(self):
        # type: () -> pd.DataFrame
        return self.__interpolate(self.__driftData)

    def getCount(self):
        return len(self.__driftData.index)

    def __getXDrift(self, index):
        return self.__driftXDict[index]

    def __getYDrift(self, index):
        return self.__driftYDict[index]

    def __getFrameID(self, index):
        #print("driftData.____getFrameID index", index,self.__frameIDDict)
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
            frameID+=1
            index = self.__getIndexOfFrame(frameID)

        return frameID

    def maxFrameID(self):
        return self.__maxFrameID

    def minFrameID(self):
        return self.__minFrameID

    def yPixelsBetweenFrames(self,fromFrameID, toFrameID):
        drift = self.driftBetweenFrames(fromFrameID, toFrameID)
        if drift is None:
            return None

        return drift.y

    def driftBetweenFrames(self,fromFrameID, toFrameID):
        # type: (int, int) -> Vector

        if fromFrameID<self.minFrameID() or toFrameID < self.minFrameID():
            #return Vector(0,0)
            return None

        if fromFrameID>self.maxFrameID() or toFrameID>self.maxFrameID():
            #return Vector(0, 0)
            return None

        if (fromFrameID > toFrameID):
            drift = self.driftBetweenFrames(toFrameID, fromFrameID)
            return Vector(-(drift.x), -(drift.y))

        if (fromFrameID == toFrameID):
            return Vector(0,0)

        return self.__getDriftBetweenTwoFrames(fromFrameID, toFrameID)

    def __getDriftBetweenTwoFrames(self, fromFrameID, toFrameID):

        #assuming fromFrameID is less than or equal to toFrameID and both are within valid range
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
        return Vector(cumulativeXDrift,cumulativeYDrift)

    def interpolate(self):
        self.__driftData = self.__interpolate(self.__driftData)

    def __interpolate(self, data):
        # type: (pd) -> pd
        data.loc[data['driftY'] == -999, ['driftY', 'driftX']] = numpy.nan
        data.loc[data['driftX'] == -888, ['driftX', 'driftY']] = numpy.nan

        data.loc[data['driftX'] < -20, ['driftX', 'driftY']] = numpy.nan
        data.loc[data['driftX'] > 30, ['driftX', 'driftY']] = numpy.nan

        data.loc[data['driftY'] < -20, ['driftX', 'driftY']] = numpy.nan
        data.loc[data['driftY'] > 80, ['driftX', 'driftY']] = numpy.nan

        return data.interpolate(limit_direction='both')

    def interpolate2(self):
        # type: () -> pd
        minVal = self.minFrameID()
        maxVal = self.maxFrameID()

        df = self.getInterpolatedDF().copy()

        df = df.set_index("frameNumber")
        everyFrame = pd.DataFrame(numpy.arange(start=minVal, stop=maxVal, step=1), columns=["frameNumber"]).set_index(
            "frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        df = df.interpolate(limit_direction='both')
        df["driftX"] = df["driftX"] / 2
        df["driftY"] = df["driftY"] / 2
        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY]]
        return df

    def getNextFrame(self, yPixelsAway, fromFrameID):
        # type: (int, int) -> int

        startingFrameIDInDataFrame = self.__nextFrameIDInFile(fromFrameID)
        startingFrameIndex = self.__getIndexOfFrame(startingFrameIDInDataFrame)

        driftToStartingFrame = self.__driftToNearbyFrame(startingFrameIndex, fromFrameID)
        yPixelsToStartingFrame = driftToStartingFrame.y

        nextFrameIDInDataFrame = startingFrameIDInDataFrame
        cumulativeYDrift= yPixelsToStartingFrame
        while cumulativeYDrift < yPixelsAway and nextFrameIDInDataFrame < self.maxFrameID():
            #keep checking next frameID in DataFrame until found one that is just a bit further away from "fromFrameID" than "pixelsAway"
            #print("DriftData::getNextFrame nextFrameIDInDataFrame", nextFrameIDInDataFrame)
            nextIndex = self.__getIndexOfFrame(nextFrameIDInDataFrame) + 1
            nextFrameIDInDataFrame = self.__getFrameID(nextIndex)
            cumulativeYDrift += self.__getYDrift(nextIndex)

        #go back zero-to-four frames to minimize the number of pixels overshot.
        pixelsToBacktrack = cumulativeYDrift - yPixelsAway
        searchedFrameID = self.__frameIDThatIsYPixelsAwayFromIndex(nextFrameIDInDataFrame, pixelsToBacktrack)

        if searchedFrameID < self.minFrameID():
            searchedFrameID = self.minFrameID()

        if searchedFrameID >= self.maxFrameID():
            searchedFrameID = self.maxFrameID()

        return searchedFrameID


    # Correct "single outliers" (where prev and next data points are not outliers)
    def replaceOutlierBetweenTwoPoints(self, data, colName, normalJump):
        col = data[colName]
        prev = col.shift(periods=1)
        next = col.shift(periods=-1)
        diffNextPrev = abs(prev - next)
        meanPrevNext = (next + prev) / 2
        deviation = abs(col - meanPrevNext)
        single_outlier = (deviation > normalJump) & (diffNextPrev < normalJump)
        data[colName] = col.mask(single_outlier, meanPrevNext)


    def replaceIfThirdIsOutlier2(self, data, colName, normalJump, normalMin, normalMax):
        # outlierThreshold = 30
        # normalJump = 5

        col = data[colName]
        prevPrev = col.shift(periods=2)
        nextNext = col.shift(periods=-2)
        prev = col.shift(periods=1)
        next = col.shift(periods=-1)

        meanPrevs = (prevPrev + prev) / 2
        deviation = abs(col - meanPrevs)

        diffPrevs = prev - prevPrev

        # outlier_fromPrevs = (deviationY > outlierThreshold) & (abs(diffPrevsY) < normalJump)
        prevsAreNotOutliers = (abs(diffPrevs) < normalJump) & (prevPrev > normalMin) & (prevPrev < normalMax) & (
                    prev > normalMin) & (prev < normalMax)

        outlier_fromPrevs = ((col < normalMin) | (col > normalMax)) & (deviation > normalJump) & prevsAreNotOutliers

        data["prevsAreNotOutliers"] = prevsAreNotOutliers
        data["outlier_fromPrevs"] = outlier_fromPrevs
        data[colName] = col.mask(outlier_fromPrevs, prev + diffPrevs)

