from lib.data.BadFramesData import BadFramesData
from lib.data.DriftData import DriftData
from lib.Frame import Frame
from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsData import RedDotsData
from lib.FolderStructure import FolderStructure
import pandas as pd

from lib.common import Vector
from lib.data.SeeFloorNoBadBlocks import SeeFloorNoBadBlocks


class SeeFloor(SeeFloorNoBadBlocks):
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftsData, badFramesData, redDotsData, folderStruct = None,  df = None):
        # type: (DriftData, BadFramesData, RedDotsData, FolderStructure, pd.DataFrame) -> SeeFloor

        SeeFloorNoBadBlocks.__init__(self, driftsData, redDotsData, folderStruct,  df)
        self.__badFramesData = badFramesData

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> SeeFloor

        driftsData = DriftData.createFromFolderStruct(folderStruct)
        badFramesData = BadFramesData.createFromFolderStruct(folderStruct)
        redDotsData = RedDotsData.createFromFolderStruct(folderStruct)

        filepath = folderStruct.getSeefloorFilepath()
        if folderStruct.fileExists(filepath):
            df = PandasWrapper.readDataFrameFromCSV(filepath)
        else:
            df = None
        newObj = SeeFloor(driftsData, badFramesData, redDotsData, folderStruct,df)
        return newObj

    def setBadFramesData(self, badFramesData):
        # type: (BadFramesData) -> None
        self.__badFramesData = badFramesData

    def maxFrameID(self):
        # type: () -> int
        maxFrameID = self.getDriftData().maxFrameID()
        maxFrameID = self.__badFramesData.firstGoodFrameBefore(maxFrameID)
        return maxFrameID

    def minFrameID(self):
        # type: () -> int
        minFrameID = self.getDriftData().minFrameID()
        minFrameID = self.__badFramesData.firstGoodFrameAfter(minFrameID)
        return minFrameID

    def _jump_to_previous_seefloor_slice(self, frame_id):
        # type: (int) -> int
        if frame_id < self.getDriftData().minFrameID():
            return self.getDriftData().minFrameID()

        if frame_id > self.getDriftData().maxFrameID():
            return self.getDriftData().maxFrameID()

        first_good_frame = self.getDriftData().minFrameID()

        if self.__badFramesData.is_bad_frame(frame_id):
            # we are currently in a bad frame. Jump out of this bad segment to the closest previous good frame
            new_frame_id = self.__badFramesData.firstGoodFrameBefore(frame_id)
            return self._adjust_outofbound_values(new_frame_id)

        if self.__badFramesData.thereIsBadFrameBefore(frame_id):
            first_good_frame = self.__badFramesData.firstBadFrameBefore(frame_id) + 1
            if frame_id == first_good_frame:
                #frame_id is the first frame in this good segment. Jump over the previous bad segment
                return self._jump_to_previous_seefloor_slice(frame_id - 1)

        # we are in a good segment and not in its first frame.
        new_frame_id = SeeFloorNoBadBlocks._jump_to_previous_seefloor_slice(self, frame_id)

        if (first_good_frame >= new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels back.
            #so jump to the first good frame in this segment
            return first_good_frame
        else:
            return new_frame_id


    def _jump_to_next_seefloor_slice(self, frame_id):
        # type: (int) -> int
        if frame_id < self.getDriftData().minFrameID():
            return self.getDriftData().minFrameID()

        if frame_id > self.getDriftData().maxFrameID():
            return self.getDriftData().maxFrameID()

        last_good_frame = self.getDriftData().maxFrameID()

        if self.__badFramesData.is_bad_frame(frame_id):
            #we are currently in a bad frame. Jump out of this bad segment to the closest next good frame
            new_frame_id = self.__badFramesData.firstGoodFrameAfter(frame_id)
            return self._adjust_outofbound_values(new_frame_id)

        if self.__badFramesData.thereIsBadFrameAfter(frame_id):
            last_good_frame = self.__badFramesData.firstBadFrameAfter(frame_id) - 1
            if frame_id == last_good_frame:
                #frame_id is the last good frame before a bad segment. Jump over this bad segment to the first next good frame
                return self._jump_to_next_seefloor_slice(frame_id + 1)

        # we are in a good segment and not in its last frame.
        new_frame_id = SeeFloorNoBadBlocks._jump_to_next_seefloor_slice(self, frame_id)

        if (last_good_frame < new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels.
            #so jump to the last good frame in this segment
            return last_good_frame
        else:
            return new_frame_id

