from lib.BadFramesData import BadFramesData
from lib.DriftData import DriftData
from lib.FramesStitcher import FramesStitcher
from lib.RedDotsData import RedDotsData


class SeeFloor:
    def __init__(self, driftsData, badFramesData, redDotsData):
        # type: (DriftData, BadFramesData, RedDotsData) -> SeeFloor
        self.__badFramesData = badFramesData
        self.__driftData = driftsData

    def maxFrameID(self):
        maxFrameID = self.__driftData.maxFrameID()
        maxFrameID = self.__badFramesData.firstGoodFrameBefore(maxFrameID)
        return maxFrameID

    def minFrameID(self):
        minFrameID = self.__driftData.minFrameID()
        minFrameID = self.__badFramesData.firstGoodFrameAfter(minFrameID)
        return minFrameID

    def jumpToSeefloorSlice(self, frame_id, frames_to_jump = 1):
        return self.jump_to_next_seefloor_slice(frame_id,frames_to_jump)

    def jump_to_previous_seefloor_slice(self, frame_id, frames_to_jump = 1):
        if self.__badFramesData.is_bad_frame(frame_id):
            new_frame_id = self.__badFramesData.firstGoodFrameBefore(frame_id)
            if new_frame_id < self.__driftData.minFrameID():
                new_frame_id = self.__driftData.minFrameID()
            return new_frame_id
        else:
            pixels_to_jump = -FramesStitcher.FRAME_HEIGHT*frames_to_jump
            new_frame_id =  int(self.__driftData.getNextFrame(pixels_to_jump, frame_id))
            return new_frame_id

    def jump_to_next_seefloor_slice(self, frame_id, frames_to_jump = 1):
        if self.__badFramesData.is_bad_frame(frame_id):
            new_frame_id = self.__badFramesData.firstGoodFrameAfter(frame_id)
            if new_frame_id > self.__driftData.maxFrameID():
                new_frame_id = self.__driftData.maxFrameID()
            return new_frame_id

        pixels_to_jump = FramesStitcher.FRAME_HEIGHT*frames_to_jump
        new_frame_id = int(self.__driftData.getNextFrame(pixels_to_jump, frame_id))


        print ("new_frame_id", new_frame_id)
        new_frame_id = self.jump_to_previous_seefloor_slice(new_frame_id,1)

        return new_frame_id