from lib.BadFramesData import BadFramesData
from lib.DriftData import DriftData
from lib.RedDotsData import RedDotsData


class SeeFloor:
    def __init__(self, driftsData, badFramesData, redDotsData):
        # type: (DriftData, BadFramesData, RedDotsData) -> SeeFloor
        self.__badFramesData = badFramesData
        self.__driftsData = driftsData

    def maxFrameID(self):
        maxFrameID = self.__driftsData.maxFrameID()
        maxFrameID = self.__badFramesData.firstGoodFrameBefore(maxFrameID)
        return maxFrameID

    def minFrameID(self):
        minFrameID = self.__driftsData.minFrameID()
        minFrameID = self.__badFramesData.firstGoodFrameAfter(minFrameID)
        return minFrameID