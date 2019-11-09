from lib.BadFramesData import BadFramesData
from lib.DriftData import DriftData
from lib.FramesStitcher import FramesStitcher
from lib.RedDotsData import RedDotsData
from lib.FolderStructure import FolderStructure
import pandas as pd
import numpy

class SeeFloor:
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftsData, badFramesData, redDotsData, df):
        # type: (DriftData, BadFramesData, RedDotsData) -> SeeFloor
        self.__badFramesData = badFramesData
        self.__driftData = driftsData
        self.__redDotsData = redDotsData
        self.__df = df


    @staticmethod
    def createFromFile(folderStruct):
        # type: (FolderStructure) -> SeeFloor

        filepath = folderStruct.getSeefloorFilepath()
        if folderStruct.fileExists(filepath):
            driftsData = DriftData.createFromFile(folderStruct.getDriftsFilepath())
            badFramesData = BadFramesData.createFromFile(folderStruct)
            redDotsData = RedDotsData.createFromFile(folderStruct)
            df = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
            newObj = SeeFloor(driftsData, badFramesData, redDotsData, df)
            return newObj
        else:
            return None

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
        pixels_to_jump = FramesStitcher.FRAME_HEIGHT
        new_frame_id = int(self.__getNextFrame(frame_id, pixels_to_jump))

        if (last_good_frame < new_frame_id):
            #the current good segment does not enough runway from frame_id to jump FramesStitcher.FRAME_HEIGHT pixels.
            #so jump to the last good frame in this segment
            return last_good_frame
        else:
            return new_frame_id

    def scienceDf(self):
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
        df = self.scienceDf()
        if df is None:
            return None
        scale = self.__redDotsData.getMMPerPixel(frame_id)
        mm_to_jump = pixels_to_jump * scale

        nextFrameID = self.getNextFrame(mm_to_jump,frame_id)
        return nextFrameID

    def getNextFrame(self, yMMAway, fromFrameID):
        # type: (float, int) -> int
        df = self.scienceDf()
        if df is None:
            return None

        yCoordMMOrigin = self.getYCoordMMOrigin(fromFrameID)
        yCoordMMDestination = yCoordMMOrigin + yMMAway
        nextFrameID = int(df.loc[(df['driftY_sum_mm'] < yCoordMMDestination)].max()["frameNumber"])
        return nextFrameID

    def getYCoordMMOrigin(self, frame_id):
        df = self.scienceDf()
        if df is None:
            return None
        return int(df.loc[(df['frameNumber'] == frame_id)]["driftY_sum_mm"])

    def scienceData(self, filepath):

        minVal = self.minFrameID()
        maxVal = self.maxFrameID()

        df = self.getDriftData().getInterpolatedDF().copy()
        df = df.set_index("frameNumber")

        everyFrame = pd.DataFrame(numpy.arange(start=minVal, stop=maxVal, step=1),
                                  columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        df = df.interpolate(limit_direction='both')
        # df['distance'] = pow(pow(df["centerPoint_x_dot2"] - df["centerPoint_x_dot1"], 2) + pow(
        #   df["centerPoint_y_dot2"] - df["centerPoint_y_dot1"], 2), 0.5)  # .astype(int)

        # df[self.__COLNAME_mm_per_pixel] = self.__distance_between_reddots_mm / df['distance']
        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY]]

        dfRedDots = self.getRedDotsData().interpolatedDF()

        dfRedDots = dfRedDots[["frameNumber","distance", "mm_per_pixel"]]
        dfMerged = pd.merge(df, dfRedDots, on='frameNumber', how='outer', suffixes=('_drift', '_reddots'))

        dfMerged["driftX_orig"] = dfMerged["driftX"]
        dfMerged["driftX"] = dfMerged["driftX"] / 2
        #dfMerged["driftY_orig"] = dfMerged["driftY"]
        dfMerged["driftY"] = dfMerged["driftY"] / 2
        dfMerged["driftY_mm"] = dfMerged["driftY"] * dfMerged["mm_per_pixel"]
        #dfMerged["driftX_mm"] = dfMerged["driftX"] * dfMerged["mm_per_pixel"]
        dfMerged["driftY_sum_mm"] = dfMerged["driftY_mm"].cumsum()
        #dfMerged["driftX_sum_mm"] = dfMerged["driftX_mm"].cumsum()
        dfMerged["driftY_sum_px"] = dfMerged["driftY"].cumsum()
        #dfMerged["driftX_sum_px"] = dfMerged["driftX"].cumsum()
        dfMerged["bottom_corner_mm"] = 1080 * dfMerged["mm_per_pixel"] + dfMerged["driftY_sum_mm"]

        dfMerged = dfMerged.sort_values(by=['frameNumber'])
        dfMerged.to_csv(filepath, sep='\t', index=False)

        return dfMerged

        #return df