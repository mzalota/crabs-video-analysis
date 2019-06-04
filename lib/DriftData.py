import math


class DriftData:
    #__driftData = None

    def __init__(self, driftData):
        # type: (pd.DataFrame) -> DriftData
        self.__driftData = driftData
        #print(driftData.count())

    def getCount(self):
        return len(self.__driftData.index)

    def getYDrift(self, index):
        return self.__driftData['driftY'][index]

    def getFrameID(self, index):
        return self.__driftData['frameNumber'][index]

    def getIndex(self, frameID):
        foundFrame = self.__driftData.loc[self.__driftData['frameNumber'] == frameID]
        if len(foundFrame.index)==1:
            return foundFrame.index[0]
        else:
            return None

    def pixelsDriftPerFrame(self, index):
        if index <= 0:
            return 0

        prevFrameNumber = self.getFrameID(index-1)
        frameNumber = self.getFrameID(index)
        driftPerFrame = self.getYDrift(index) / (int(frameNumber) - int(prevFrameNumber))
        return driftPerFrame

    def frameIDThatIsPixelsAwayFromIndex(self, frameID, pixelsAway):
        index = self.getIndex(frameID)

        driftPerFrame = self.pixelsDriftPerFrame(index)

        framesToBacktrack = math.floor(pixelsAway / driftPerFrame)

        frameID = int(self.getFrameID(index))
        frameToUse = frameID - framesToBacktrack

        return frameToUse

    def pixelsToFrameIDFromIndex(self, frameIDOfIndex, frameID):
        index = self.getIndex(frameIDOfIndex)

        framesToJump = int(frameIDOfIndex) - frameID

        pixelsDriftPerFrame = self.pixelsDriftPerFrame(index)

        pixelsAway = math.floor(pixelsDriftPerFrame * framesToJump)
        return pixelsAway

    def nextFrameIDInFile(self, frameID):
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

    def getNextFrame(self, pixelsAway, fromFrameID):

        startingFrameIDInDataFrame = self.nextFrameIDInFile(fromFrameID)
        pixelsToStartingFrame = self.pixelsToFrameIDFromIndex(startingFrameIDInDataFrame, fromFrameID)

        nextFrameIDInDataFrame = startingFrameIDInDataFrame
        cumulativeDrift= pixelsToStartingFrame
        while cumulativeDrift < pixelsAway and nextFrameIDInDataFrame < self.maxFrameID():
            #keep checking next frameID in DataFrame until found one that is just a bit further away from "fromFrameID" than "pixelsAway"
            nextIndex = self.getIndex(nextFrameIDInDataFrame) + 1
            nextFrameIDInDataFrame = self.getFrameID(nextIndex)
            cumulativeDrift += self.getYDrift(nextIndex)

        #go back zero-to-four frames to minimize the number of pixels overshot.
        pixelsToBacktrack = cumulativeDrift-pixelsAway
        searchedFrameID = self.frameIDThatIsPixelsAwayFromIndex(nextFrameIDInDataFrame, pixelsToBacktrack)

        return searchedFrameID
