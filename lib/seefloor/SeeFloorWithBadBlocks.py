import pandas as pd

from lib.drifts_interpolate.DriftInterpolatedData import DriftInterpolatedData
from lib.infra.FolderStructure import FolderStructure
from lib.data.BadFramesData import BadFramesData
from lib.data.PandasWrapper import PandasWrapper
from lib.reddots_interpolate.RedDotsData import RedDotsData
from lib.seefloor.SeeFloor import SeeFloor
from lib.seefloor.SeeFloorSlicerService import SeeFloorSlicerService


class SeeFloorWithBadBlocks(SeeFloor):
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    _COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftsData, badFramesData, redDotsData, folderStruct = None,  df = None):
        # type: (DriftData, BadFramesData, RedDotsData, FolderStructure, pd.DataFrame) -> SeeFloor

        super().__init__(driftsData, redDotsData, folderStruct,  df)
        self.__badFramesData = badFramesData

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> SeeFloor

        driftsData = DriftInterpolatedData.createFromFolderStruct(folderStruct)
        badFramesData = BadFramesData.createFromFolderStruct(folderStruct)
        redDotsData = RedDotsData.createFromFolderStruct(folderStruct)

        filepath = folderStruct.getSeefloorFilepath()
        if folderStruct.fileExists(filepath):
            df = PandasWrapper.readDataFrameFromCSV(filepath)
        else:
            df = None
        newObj = SeeFloor(driftsData, badFramesData, redDotsData, folderStruct, df)
        return newObj

    def setBadFramesData(self, badFramesData):
        # type: (BadFramesData) -> None
        self.__badFramesData = badFramesData

    def maxFrameID_nobadBlocks(self):
        # type: () -> int
        maxFrameID = self._max_frame_id_badBlocks()
        maxFrameID = self.__badFramesData.firstGoodFrameBefore(maxFrameID)
        return maxFrameID

    def minFrameID_nobadBlocks(self):
        # type: () -> int
        minFrameID = self._min_frame_id_badBlocks()
        minFrameID = self.__badFramesData.firstGoodFrameAfter(minFrameID)
        return minFrameID

    def _min_frame_id_badBlocks(self):
        #return self.minFrameID()
         return self.getDriftData().minFrameID()

    def _max_frame_id_badBlocks(self):
        #return self.maxFrameID()
        return self.getDriftData().maxFrameID()

    def _jump_to_previous_seefloor_slice(self, frame_id):
        # type: (int) -> int
        if frame_id < self._min_frame_id_badBlocks():
            return self._min_frame_id_badBlocks()

        if frame_id > self._max_frame_id_badBlocks():
            return self._max_frame_id_badBlocks()

        first_good_frame = self._min_frame_id_badBlocks()

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
        new_frame_id = SeeFloorSlicerService._jump_to_previous_seefloor_slice(self, frame_id)

        if (first_good_frame >= new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels back.
            #so jump to the first good frame in this segment
            return first_good_frame
        else:
            return new_frame_id

    def _jump_to_next_seefloor_slice(self, frame_id, fraction = 1):
        # type: (int) -> int
        if frame_id < self._min_frame_id_badBlocks():
            return self._min_frame_id_badBlocks()

        if frame_id > self._max_frame_id_badBlocks():
            return self._max_frame_id_badBlocks()

        last_good_frame = self._max_frame_id_badBlocks()

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
        new_frame_id = SeeFloorSlicerService._jump_to_next_seefloor_slice(self, frame_id)

        if (last_good_frame < new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels.
            #so jump to the last good frame in this segment
            return last_good_frame
        else:
            return new_frame_id

    def _adjust_outofbound_values(self, frame_id):
        # type: (int) -> int
        if frame_id < self._min_frame_id_badBlocks():
            return self._min_frame_id_badBlocks()

        if frame_id > self._max_frame_id_badBlocks():
            return self._max_frame_id_badBlocks()

        return frame_id

