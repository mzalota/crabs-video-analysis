import math
import pandas as pd

class DriftData:
    #__driftData = None

    def __init__(self, driftData):
        # type: (pd.DataFrame) -> DriftData
        self.__driftData = driftData
        print(driftData.count())

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

    def __getYDrift(self, index):
        return self.__driftData['driftY'][index]

    def __getFrameID(self, index):
        return self.__driftData['frameNumber'][index]

    def minFrameID(self):
        return self.__driftData['frameNumber'][0]

    def getIndex(self, frameID):
        foundFrame = self.__driftData.loc[self.__driftData['frameNumber'] == frameID]
        if len(foundFrame.index)==1:
            return foundFrame.index[0]
        else:
            return None

    def __pixelsYDriftPerFrame(self, index):
        if index <= 0:
            return 0

        prevFrameNumber = self.__getFrameID(index-1)
        frameNumber = self.__getFrameID(index)
        numberOfFramesJumped = (int(frameNumber) - int(prevFrameNumber))
        driftPerFrame = self.__getYDrift(index) / numberOfFramesJumped
        return driftPerFrame

    def __frameIDThatIsPixelsAwayFromIndex(self, frameID, pixelsAway):
        index = self.getIndex(frameID)

        driftPerFrame = self.__pixelsYDriftPerFrame(index)

        framesToBacktrack = math.floor(pixelsAway / driftPerFrame)

        frameID = int(self.__getFrameID(index))
        frameToUse = frameID - framesToBacktrack

        return frameToUse

    def __yPixelsToNearbyFrame(self, index, nearbyFrameID):

        yPixelsDriftPerFrame = self.__pixelsYDriftPerFrame(index)

        framesToJump = int(self.__getFrameID(index)) - nearbyFrameID
        yPixelsAway = math.floor(yPixelsDriftPerFrame * framesToJump)

        return yPixelsAway

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
        return self.__driftData['frameNumber'].max()

    def minFrameID(self):
        return self.__driftData['frameNumber'].min()

    def yPixelsBetweenFrames(self,fromFrameID, toFrameID):
        if fromFrameID<self.minFrameID() or toFrameID < self.minFrameID():
            return None

        startingFrameIDInDataFrame = self.__nextFrameIDInFile(fromFrameID)
        endingFrameIDInDataFrame = self.__nextFrameIDInFile(toFrameID)
        print ("startingFrameIDInDataFrame", startingFrameIDInDataFrame)
        print ("endingFrameIDInDataFrame", endingFrameIDInDataFrame)

        startingFrameIndex = self.getIndex(startingFrameIDInDataFrame)
        yPixelsToStartingFrame = self.__yPixelsToNearbyFrame(startingFrameIndex, fromFrameID)

        startIndex = self.getIndex(startingFrameIDInDataFrame)
        print ("startIndex", startIndex)

        endIndex = self.getIndex(endingFrameIDInDataFrame)
        if endIndex<startIndex:
            endIndex=startIndex


        nextIndex = startIndex
        cumulativeYDrift = 0
        #if (endIndex-startIndex) > 1:
        while nextIndex < endIndex:
            nextIndex = nextIndex + 1
            cumulativeYDrift += self.__getYDrift(nextIndex)

        print ("endIndex", endIndex)

        yPixelsfromEndingFrame = self.__yPixelsToNearbyFrame(endIndex, toFrameID)
        print ("yPixelsfromEndingFrame", yPixelsfromEndingFrame)
        print ("yPixelsToStartingFrame", yPixelsToStartingFrame)

        if (endingFrameIDInDataFrame != toFrameID):
            #addingLastPiece = (self.__getYDrift(endIndex) - yPixelsfromEndingFrame)
            addingLastPiece = (- yPixelsfromEndingFrame)
        else:
            addingLastPiece = 0
        totalDrift = cumulativeYDrift + yPixelsToStartingFrame + addingLastPiece
        print ("distance", totalDrift)
        return totalDrift

    def getNextFrame(self, yPixelsAway, fromFrameID):

        startingFrameIDInDataFrame = self.__nextFrameIDInFile(fromFrameID)
        startingFrameIndex = self.getIndex(startingFrameIDInDataFrame)
        yPixelsToStartingFrame = self.__yPixelsToNearbyFrame(startingFrameIndex, fromFrameID)

        nextFrameIDInDataFrame = startingFrameIDInDataFrame
        cumulativeYDrift= yPixelsToStartingFrame
        while cumulativeYDrift < yPixelsAway and nextFrameIDInDataFrame < self.maxFrameID():
            #keep checking next frameID in DataFrame until found one that is just a bit further away from "fromFrameID" than "pixelsAway"
            nextIndex = self.getIndex(nextFrameIDInDataFrame) + 1
            nextFrameIDInDataFrame = self.__getFrameID(nextIndex)
            cumulativeYDrift += self.__getYDrift(nextIndex)

        #go back zero-to-four frames to minimize the number of pixels overshot.
        pixelsToBacktrack = cumulativeYDrift - yPixelsAway
        searchedFrameID = self.__frameIDThatIsPixelsAwayFromIndex(nextFrameIDInDataFrame, pixelsToBacktrack)

        return searchedFrameID
