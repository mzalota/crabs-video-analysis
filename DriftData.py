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

    def pixelsDriftPerFrame(self, index):
        if index <=0:
            return 0

        prevFrameNumber = self.getFrameID(index-1)
        frameNumber = self.getFrameID(index)
        driftPerFrame = self.getYDrift(index) / (int(frameNumber) - int(prevFrameNumber))
        return driftPerFrame

    def frameIDThatIsPixelsAwayFromIndex(self, index, pixelsAway):

        driftPerFrame = self.pixelsDriftPerFrame(index)

        framesToBacktrack = math.floor(pixelsAway / driftPerFrame)

        frameID = int(self.getFrameID(index))
        frameToUse = frameID - framesToBacktrack

        return frameToUse

    def pixelsToFrameIDFromIndex(self, index, frameID):

        frameIDOfIndex = int(self.getFrameID(index))
        framesToJump = frameIDOfIndex - frameID

        pixelsDriftPerFrame = self.pixelsDriftPerFrame(index)

        pixelsAway = math.floor(pixelsDriftPerFrame * framesToJump)
        return pixelsAway