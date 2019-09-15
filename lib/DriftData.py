import math
import pandas as pd

from lib.MyTimer import MyTimer
from lib.common import Vector


class DriftData:
    #__driftData = None
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftData):
        # type: (pd.DataFrame) -> DriftData

        self.__driftData = driftData

        dfIndexIsFrameNumber = driftData.reset_index().set_index(self.__COLNAME_frameNumber)
        self.__tmpDict = dfIndexIsFrameNumber["index"].to_dict()

        self.__maxFrameID = self.__driftData[self.__COLNAME_frameNumber].max()
        self.__minFrameID = self.__driftData[self.__COLNAME_frameNumber].min()

        self.__driftXDict = self.__driftData[self.__COLNAME_driftX].to_dict()
        self.__driftYDict = self.__driftData[self.__COLNAME_driftY].to_dict()
        self.__frameIDDict = self.__driftData[self.__COLNAME_frameNumber].to_dict()

        #print(driftData.count())

    @staticmethod
    def createFromFile(filepath):
        # type: (String) -> DriftData
        dfRaw = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
        #dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum

        return DriftData(dfRaw)

    @staticmethod
    def createFromDataFrame(driftData):
        # type: (pd.DataFrame) -> DriftData
        return DriftData(driftData)

    def getCount(self):
        return len(self.__driftData.index)

    def __getXDrift(self, index):
        return self.__driftXDict[index]
        #return self.__driftData[self.__COLNAME_driftX][index]

    def __getYDrift(self, index):
        return self.__driftYDict[index]
        #return self.__driftData[self.__COLNAME_driftY][index]

    def __getFrameID(self, index):
        return self.__frameIDDict[index]
        #return self.__driftData[self.__COLNAME_frameNumber][index]

    def getIndex(self, frameID):

        if frameID in self.__tmpDict:
            return self.__tmpDict[frameID]
        else:
            return None

        #print self.__tmpDriftData.head()
        #foundFrame = self.__tmpDriftData[frameID]
        if frameID in self.__tmpDriftData.index:
            #print self.__tmpDriftData.loc[frameID]
            return self.__tmpDriftData.loc[frameID]["index"]
        else:
            return None

        #if len(foundFrame.index)==1:
        #    return foundFrame["index"]
        #else:
        #    return None


    def getIndex_orig(self, frameID):
        foundFrame = self.__driftData.loc[self.__driftData[self.__COLNAME_frameNumber] == frameID]
        if len(foundFrame.index)==1:
            return foundFrame.index[0]
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
        index = self.getIndex(frameID)

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

        index = self.getIndex(frameID)
        while index is None:
            frameID+=1
            index = self.getIndex(frameID)

        return frameID

    def maxFrameID(self):
        #if not self.__maxFrameID:
        #if not hasattr(self, "__maxFrameID"):
        #    self.__maxFrameID = self.__driftData[self.__COLNAME_frameNumber].max()

        return self.__maxFrameID
        #return self.__driftData[self.__COLNAME_frameNumber].max()

    #def minFrameID(self):
    #    return self.__driftData[self.__COLNAME_frameNumber].min()

    def minFrameID(self):
        #if not self.__minFrameID:
        if not hasattr(self, "__minFrameID"):
            self.__minFrameID = self.__driftData[self.__COLNAME_frameNumber].min()
        return self.__minFrameID

        #return self.__driftData[self.__COLNAME_frameNumber][0]


    def yPixelsBetweenFrames(self,fromFrameID, toFrameID):
        drift = self.driftBetweenFrames(fromFrameID, toFrameID)
        #if drift.x ==0 and drift.y == 0:
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

        #timer = MyTimer("__getDriftBetweenTwoFrames")
        #assuming fromFrameID is less than or equal to toFrameID and both are within valid range
        startingFrameIDInDataFrame = self.__nextFrameIDInFile(fromFrameID)
        startIndex = self.getIndex(startingFrameIDInDataFrame)
        #timer.lap("here 10")
        endingFrameIDInDataFrame = self.__nextFrameIDInFile(toFrameID)
        endIndex = self.getIndex(endingFrameIDInDataFrame)
        #timer.lap("here 20")

        driftToStartingFrame = self.__driftToNearbyFrame(startIndex, fromFrameID)
        #timer.lap("here 30")

        cumulativeDrift = self.__driftBetweenFramesInDataFrame(endIndex, startIndex)
        #timer.lap("here 40")

        driftFromEndingFrame = self.__driftToNearbyFrame(endIndex, toFrameID)
        #timer.lap("here 50")

        totalYDrift = cumulativeDrift.y + driftToStartingFrame.y - driftFromEndingFrame.y
        totalXDrift = cumulativeDrift.x + driftToStartingFrame.x - driftFromEndingFrame.x

        #timer.lap("here 80")

        return Vector(totalXDrift, totalYDrift)

    def __driftBetweenFramesInDataFrame(self, endIndex, nextIndex):
        cumulativeYDrift = 0
        cumulativeXDrift = 0
        while nextIndex < endIndex:
            nextIndex = nextIndex + 1
            cumulativeYDrift += self.__getYDrift(nextIndex)
            cumulativeXDrift += self.__getXDrift(nextIndex)
        return Vector(cumulativeXDrift,cumulativeYDrift)

    def getNextFrame(self, yPixelsAway, fromFrameID):
        # type: (int, int) -> int

        startingFrameIDInDataFrame = self.__nextFrameIDInFile(fromFrameID)
        startingFrameIndex = self.getIndex(startingFrameIDInDataFrame)

        driftToStartingFrame = self.__driftToNearbyFrame(startingFrameIndex, fromFrameID)
        yPixelsToStartingFrame = driftToStartingFrame.y

        nextFrameIDInDataFrame = startingFrameIDInDataFrame
        cumulativeYDrift= yPixelsToStartingFrame
        while cumulativeYDrift < yPixelsAway and nextFrameIDInDataFrame < self.maxFrameID():
            #keep checking next frameID in DataFrame until found one that is just a bit further away from "fromFrameID" than "pixelsAway"
            nextIndex = self.getIndex(nextFrameIDInDataFrame) + 1
            nextFrameIDInDataFrame = self.__getFrameID(nextIndex)
            cumulativeYDrift += self.__getYDrift(nextIndex)

        #go back zero-to-four frames to minimize the number of pixels overshot.
        pixelsToBacktrack = cumulativeYDrift - yPixelsAway
        searchedFrameID = self.__frameIDThatIsYPixelsAwayFromIndex(nextFrameIDInDataFrame, pixelsToBacktrack)

        return searchedFrameID
