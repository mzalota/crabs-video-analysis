from lib.BadFramesData import BadFramesData
from lib.DriftData import DriftData
from lib.RedDotsData import RedDotsData


class SeeFloor:
    def __init__(self, driftsData, badFramesData, redDotsData):
        # type: (DriftData, BadFramesData, RedDotsData) -> SeeFloor
        self.__driftsData = driftsData

    def maxFrameID(self):
        return self.__driftsData.maxFrameID()

    def minFrameID(self):
        return self.__driftsData.minFrameID()