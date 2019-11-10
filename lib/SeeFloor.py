from lib.BadFramesData import BadFramesData
from lib.CrabsData import CrabsData
from lib.DriftData import DriftData
from lib.Frame import Frame
from lib.RedDotsData import RedDotsData
from lib.FolderStructure import FolderStructure
import pandas as pd
import numpy

class SeeFloor:
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftsData, badFramesData, redDotsData, folderStruct = None,  df = None):
        # type: (DriftData, BadFramesData, RedDotsData) -> SeeFloor
        self.__badFramesData = badFramesData
        self.__driftData = driftsData
        self.__redDotsData = redDotsData
        self.__df = df
        self.__folderStruct = folderStruct
        self.__crabsData = CrabsData(self.__folderStruct)

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> SeeFloor

        driftsData = DriftData.createFromFolderStruct(folderStruct)
        badFramesData = BadFramesData.createFromFolderStruct(folderStruct)
        redDotsData = RedDotsData.createFromFolderStruct(folderStruct)

        filepath = folderStruct.getSeefloorFilepath()
        if folderStruct.fileExists(filepath):
            df = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
        else:
            df = None
        newObj = SeeFloor(driftsData, badFramesData, redDotsData, folderStruct,df)
        return newObj

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
        pixels_to_jump = Frame.FRAME_HEIGHT * (-1)
        new_frame_id = int(self.__getNextFrame(frame_id, pixels_to_jump))

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
        pixels_to_jump = Frame.FRAME_HEIGHT
        new_frame_id = int(self.__getNextFrame(frame_id, pixels_to_jump))

        if (last_good_frame < new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels.
            #so jump to the last good frame in this segment
            return last_good_frame
        else:
            return new_frame_id

    def getDF(self):
        # type: () -> pd
        try:
            return self.__df
        except AttributeError:
            return None

    def __getNextFrame(self, frame_id, pixels_to_jump):
        nextFrameID = self.__getNextFrameMM(pixels_to_jump, frame_id)
        if nextFrameID is None:
            return self.__driftData.getNextFrame(pixels_to_jump, frame_id)
        else:
            return nextFrameID

    def __getNextFrameMM(self, pixels_to_jump, frame_id):
        scale = self.__redDotsData.getMMPerPixel(frame_id)
        mm_to_jump = pixels_to_jump * scale
        return self.getFrame(mm_to_jump,frame_id)

    def getFrame(self, yMMAway, fromFrameID):
        # type: (float, int) -> int
        df = self.getDF()
        if df is None:
            return None

        yCoordMMOrigin = self.__getYCoordMMOrigin(fromFrameID)
        yCoordMMDestination = yCoordMMOrigin + yMMAway

        if yCoordMMDestination < self.__getYCoordMMOrigin(self.minFrameID()):
            return self.minFrameID()

        if yCoordMMDestination > self.__getYCoordMMOrigin(self.maxFrameID()):
            return self.maxFrameID()

        result = df.loc[(df['driftY_sum_mm'] < yCoordMMDestination)].max()["frameNumber"]
        if result:
            nextFrameID = int(result)
        else:
            print("Something wierd ine SeeFloor.getFrame: yCoordMMDestination", yCoordMMDestination, "fromFrameID", fromFrameID, "yMMAway", yMMAway,
                  "yCoordMMOrigin", yCoordMMOrigin)
            nextFrameID = fromFrameID
        return nextFrameID

    def __getYCoordMMOrigin(self, frame_id):
        df = self.getDF()
        if df is None:
            return None
        result = df.loc[(df['frameNumber'] == frame_id)]["driftY_sum_mm"]
        if result.empty:
            print ("Unexpected Result: in __getYCoordMMOrigin: frame_id", frame_id)
            return 0
        return int(result)

    def saveToFile(self):
        filepath = self.__folderStruct.getSeefloorFilepath()
        self.__df = self.__interpolate()
        self.__df.to_csv(filepath, sep='\t', index=False)

    def __interpolate(self):
        dfDrifts = self.getDriftData().interpolate2()
        dfRedDots = self.getRedDotsData().interpolatedDF()
        dfRedDots = dfRedDots[["frameNumber","distance", "mm_per_pixel"]]

        return self.__mergeDriftsAndRedDots(dfDrifts, dfRedDots)

    def __mergeDriftsAndRedDots(self, dfDrifts, dfRedDots):
        dfMerged = pd.merge(dfDrifts, dfRedDots, on='frameNumber', how='outer', suffixes=('_drift', '_reddots'))
        dfMerged["driftY_mm"] = dfMerged["driftY"] * dfMerged["mm_per_pixel"]
        # dfMerged["driftX_mm"] = dfMerged["driftX"] * dfMerged["mm_per_pixel"]
        dfMerged["driftY_sum_mm"] = dfMerged["driftY_mm"].cumsum()
        # dfMerged["driftX_sum_mm"] = dfMerged["driftX_mm"].cumsum()
        dfMerged["bottom_corner_mm"] = 1080 * dfMerged["mm_per_pixel"] + dfMerged["driftY_sum_mm"]
        dfMerged = dfMerged.sort_values(by=['frameNumber'])
        return dfMerged

    def getPrevFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, -1)

    def getNextFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, 1)

    def crabsOnFrame(self, frame_id):
        # type: (int) -> dict
        crabsData = self.__crabsData
        prev_frame_id = self.getPrevFrame(frame_id)
        next_frame_id = self.getNextFrame(frame_id)
        markedCrabs = crabsData.crabsBetweenFrames(prev_frame_id, next_frame_id)
        return markedCrabs
