from lib.BadFramesData import BadFramesData
from lib.DriftData import DriftData
from lib.FramesStitcher import FramesStitcher
from lib.RedDotsData import RedDotsData


class SeeFloor:
    def __init__(self, driftsData, badFramesData, redDotsData):
        # type: (DriftData, BadFramesData, RedDotsData) -> SeeFloor
        self.__badFramesData = badFramesData
        self.__driftData = driftsData
        self.__redDotsData = redDotsData

    def getDriftData(self):
        return self.__driftData

    def getRedDotsData(self):
        return self.__redDotsData

    def setBadFramesData(self, badFramesData):
        self.__badFramesData = badFramesData

    def maxFrameID(self):
        maxFrameID = self.__driftData.maxFrameID()
        maxFrameID = self.__badFramesData.firstGoodFrameBefore(maxFrameID)
        return maxFrameID

    def minFrameID(self):
        minFrameID = self.__driftData.minFrameID()
        minFrameID = self.__badFramesData.firstGoodFrameAfter(minFrameID)
        return minFrameID

    def jumpToSeefloorSlice(self, frame_id, frames_to_jump):
        if frame_id < self.__driftData.minFrameID():
            return int(self.__driftData.minFrameID())

        if frame_id > self.__driftData.maxFrameID():
            return int(self.__driftData.maxFrameID())

        new_frame_id = frame_id
        while frames_to_jump != 0:
            if frames_to_jump > 0:
                new_frame_id = int(self.__jump_to_next_seefloor_slice(new_frame_id))
                frames_to_jump = frames_to_jump-1
            if frames_to_jump < 0:
                new_frame_id = int(self.__jump_to_previous_seefloor_slice(new_frame_id))
                frames_to_jump = frames_to_jump+1

        return new_frame_id

    def __adjust_outofbound_values(self,frame_id):
        if frame_id < self.__driftData.minFrameID():
            return self.__driftData.minFrameID()

        if frame_id > self.__driftData.maxFrameID():
            return self.__driftData.maxFrameID()

        return frame_id


    def __jump_to_previous_seefloor_slice(self, frame_id):
        if frame_id < self.__driftData.minFrameID():
            return self.__driftData.minFrameID()

        if frame_id > self.__driftData.maxFrameID():
            return self.__driftData.maxFrameID()

        if self.__badFramesData.is_bad_frame(frame_id):
            # we are currently in a bad frame. Jump out of this bad segment to the closest previous good frame
            new_frame_id = self.__badFramesData.firstGoodFrameBefore(frame_id)
            return self.__adjust_outofbound_values(new_frame_id)

        if self.__badFramesData.thereIsBadFrameBefore(frame_id):
            first_good_frame = self.__badFramesData.firstBadFrameBefore(frame_id) + 1
            if frame_id == first_good_frame:
                #frame_id is the first frame in this good segment. Jump over the previous bad segment
                return self.__jump_to_previous_seefloor_slice(frame_id - 1)
        else:
            first_good_frame = self.__driftData.minFrameID()

        # we are in a good segment and not in its first frame.
        pixels_to_jump = FramesStitcher.FRAME_HEIGHT * (-1)
        new_frame_id = int(self.__driftData.getNextFrame(pixels_to_jump, frame_id))

        if (first_good_frame >= new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels back.
            #so jump to the first good frame in this segment
            return first_good_frame
        else:
            return new_frame_id


    def __jump_to_next_seefloor_slice(self, frame_id):
        if frame_id < self.__driftData.minFrameID():
            return self.__driftData.minFrameID()

        if frame_id > self.__driftData.maxFrameID():
            return self.__driftData.maxFrameID()

        if self.__badFramesData.is_bad_frame(frame_id):
            #we are currently in a bad frame. Jump out of this bad segment to the closest next good frame
            new_frame_id = self.__badFramesData.firstGoodFrameAfter(frame_id)
            return self.__adjust_outofbound_values(new_frame_id)

        if self.__badFramesData.thereIsBadFrameAfter(frame_id):
            last_good_frame = self.__badFramesData.firstBadFrameAfter(frame_id) - 1
            if frame_id == last_good_frame:
                #frame_id is the last good frame before a bad segment. Jump over this bad segment to the first next good frame
                return self.__jump_to_next_seefloor_slice(frame_id + 1)
        else:
            last_good_frame= self.__driftData.maxFrameID()

        # we are in a good segment and not in its last frame.
        pixels_to_jump = FramesStitcher.FRAME_HEIGHT
        new_frame_id = int(self.__driftData.getNextFrame(pixels_to_jump, frame_id))

        if (last_good_frame < new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels.
            #so jump to the last good frame in this segment
            return last_good_frame
        else:
            return new_frame_id

