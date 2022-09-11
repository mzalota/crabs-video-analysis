import numpy

from lib.FrameId import FrameId
from lib.VideoStream import VideoStream
from lib.data.BadFramesData import BadFramesData
from lib.data.DriftData import DriftData
from lib.Frame import Frame
from lib.data.GraphPlotter import GraphPlotter
from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsData import RedDotsData
from lib.FolderStructure import FolderStructure
import pandas as pd

from lib.common import Vector, Point

class SeeFloorNoBadBlocks(PandasWrapper):
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftsData, redDotsData, folderStruct = None,  df = None):
        # type: (DriftData, BadFramesData, RedDotsData, FolderStructure) -> SeeFloorNoBadBlocks
        self.__driftData = driftsData
        self.__redDotsData = redDotsData
        self.__df = df
        self.__folderStruct = folderStruct
        #self.__crabsData = CrabsData(self.__folderStruct)

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> SeeFloorNoBadBlocks

        driftsData = DriftData.createFromFolderStruct(folderStruct)
        redDotsData = RedDotsData.createFromFolderStruct(folderStruct)

        filepath = folderStruct.getSeefloorFilepath()
        if folderStruct.fileExists(filepath):
            #df = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
            df = PandasWrapper.readDataFrameFromCSV(filepath)
        else:
            df = None
        newObj = SeeFloorNoBadBlocks(driftsData, redDotsData, folderStruct, df)
        return newObj

    def getDriftData(self):
        # type: () -> DriftData
        return self.__driftData

    def getRedDotsData(self):
        # type: () -> RedDotsData
        return self.__redDotsData

    def maxFrameID(self):
        # type: () -> int
        maxFrameID = self.__driftData.maxFrameID()
        return maxFrameID

    def minFrameID(self):
        # type: () -> int
        minFrameID = self.__driftData.minFrameID()
        return minFrameID

    def jumpToSeefloorSlice(self, frame_id, frames_to_jump):
        # type: (int, int) -> int
        if frame_id < self.getDriftData().minFrameID():
            return int(self.getDriftData().minFrameID())

        if frame_id > self.getDriftData().maxFrameID():
            return int(self.getDriftData().maxFrameID())

        new_frame_id = frame_id
        while frames_to_jump != 0:
            if frames_to_jump > 0:

                if frames_to_jump>0 and frames_to_jump<1:
                    #its a fractional jump
                    new_frame_id = int(self._jump_to_next_seefloor_slice(new_frame_id, frames_to_jump))
                    frames_to_jump = 0
                else:
                    new_frame_id = int(self._jump_to_next_seefloor_slice(new_frame_id))
                    frames_to_jump = frames_to_jump-1
            if frames_to_jump < 0:
                new_frame_id = int(self._jump_to_previous_seefloor_slice(new_frame_id))
                frames_to_jump = frames_to_jump+1

        return new_frame_id

    def _adjust_outofbound_values(self, frame_id):
        # type: (int) -> int
        if frame_id < self.getDriftData().minFrameID():
            return self.getDriftData().minFrameID()

        if frame_id > self.getDriftData().maxFrameID():
            return self.getDriftData().maxFrameID()

        return frame_id


    def _jump_to_previous_seefloor_slice(self, frame_id):
        # type: (int) -> int
        if frame_id < self.getDriftData().minFrameID():
            return self.getDriftData().minFrameID()

        if frame_id > self.getDriftData().maxFrameID():
            return self.getDriftData().maxFrameID()

        # we are in a good segment and not in its first frame.
        pixels_to_jump = Frame.FRAME_HEIGHT * (-1)
        new_frame_id = int(self._getNextFrame(pixels_to_jump, frame_id))
        return new_frame_id

    def _jump_to_next_seefloor_slice(self, frame_id, fraction=1):
        # type: (int) -> int
        if frame_id < self.getDriftData().minFrameID():
            return self.getDriftData().minFrameID()

        if frame_id > self.getDriftData().maxFrameID():
            return self.getDriftData().maxFrameID()

        # we are in a good segment and not in its last frame.
        pixels_to_jump = Frame.FRAME_HEIGHT * fraction
        new_frame_id = int(self._getNextFrame(pixels_to_jump, frame_id))
        return new_frame_id

    def __getPandasDF(self):
        # type: () -> pd.DataFrame
        try:
            return self.__df
        except AttributeError:
            return None

    def _getNextFrame(self, pixels_to_jump, frame_id):
        nextFrameID = self.__getNextFrameMM(pixels_to_jump, frame_id)
        if nextFrameID is None:
            return self.__driftData.getNextFrame(pixels_to_jump, frame_id)
        else:
            return nextFrameID

    def __getNextFrameMM(self, pixels_to_jump, frame_id):
        if self.__redDotsData is None:
            return None
        scale = self.__redDotsData.getMMPerPixel(frame_id)
        mm_to_jump = pixels_to_jump * scale
        return self.getFrame(mm_to_jump,frame_id)

    def getNextFrameMM(self, thisFrameID):
        thisFrameHeightMM = self.heightMM(int(thisFrameID))
        return self.getFrame(thisFrameHeightMM, thisFrameID)

    def getPrevFrameMM(self, thisFrameID):
        thisFrameHeightMM = self.heightMM(int(thisFrameID))
        return self.getFrame(-thisFrameHeightMM, thisFrameID)


    def getFrame(self, yMMAway, fromFrameID):
        # type: (float, int) -> int
        df = self.__getPandasDF()
        if df is None:
            return None

        # print("SeeFloorNoBadBlocks.getFrame() yMMAway")

        yCoordMMOrigin = self.getYCoordMMOrigin(fromFrameID)
        yCoordMMDestination = yCoordMMOrigin + yMMAway

        if yCoordMMDestination < self.getYCoordMMOrigin(self.minFrameID()):
            return self.minFrameID()

        if yCoordMMDestination > self.getYCoordMMOrigin(self.maxFrameID()):
            return self.maxFrameID()

        result = df.loc[(df['driftY_sum_mm'] < yCoordMMDestination)].max()["frameNumber"]
        if result and not numpy.isnan(result):
            nextFrameID = int(result)
        else:
            print("Something wierd ine SeeFloor.getFrame: yCoordMMDestination", yCoordMMDestination, "fromFrameID", fromFrameID, "yMMAway", yMMAway,
                  "yCoordMMOrigin", yCoordMMOrigin)
            nextFrameID = fromFrameID
        return nextFrameID

    def __driftBetweenFramesPixels(self, fromFrameID, toFrameID):
        # type: (int, int) -> Vector

        if fromFrameID < self.__driftData.minFrameID() or toFrameID < self.__driftData.minFrameID():
            # return Vector(0,0)
            return None

        if fromFrameID > self.__driftData.maxFrameID() or toFrameID > self.__driftData.maxFrameID():
            # return Vector(0, 0)
            return None

        if (fromFrameID == toFrameID):
            return Vector(0, 0)

        # driftX = self.getXDriftPixels(fromFrameID, toFrameID)
        # driftY = self.getYDriftPixels(fromFrameID, toFrameID)
        # result = Vector(driftX, driftY)
        # return result

        result_new = Vector(self.get_x_drift_px(fromFrameID, toFrameID), self.get_y_drift_px(fromFrameID, toFrameID))
        #print("__driftBetweenFramesPixels orig "+str(result), " new: ", str(result_new))
        return result_new


    def getXDriftPixels(self, fromFrameID, toFrameID):
        # type: (int, int) -> int
        xDriftMM = self.getXDriftMM(fromFrameID, toFrameID)
        # mmPerPixel = self.getRedDotsData().getMMPerPixel(fromFrameID)
        mmPerPixel = self.getRedDotsData().getMMPerPixel(toFrameID)
        xDrift = xDriftMM/mmPerPixel
        return int(xDrift)

    def getYDriftPixels(self, fromFrameID, toFrameID):
        # type: (int, int) -> int
        yDriftMM = self.getYDriftMM(fromFrameID, toFrameID)
        # mmPerPixel = self.getRedDotsData().getMMPerPixel(fromFrameID)
        mmPerPixel = self.getRedDotsData().getMMPerPixel(toFrameID)
        yDrift = yDriftMM/mmPerPixel
        result = int(yDrift)

        return result

    def get_drift_instantaneous(self, frame_id):
        # type: (int) -> Vector
        drift_x = self.__getValueFromDF(self.__COLNAME_driftX, frame_id)
        drift_y = self.__getValueFromDF(self.__COLNAME_driftY, frame_id)
        return Vector(drift_x, drift_y)

    def zoom_instantaneous(self, frame_id):
        # type: (int) -> float
        if frame_id <= self.minFrameID():
            return 1

        scale_this = self.__getValueFromDF("mm_per_pixel", frame_id)
        scale_prev = self.__getValueFromDF("mm_per_pixel", frame_id-1)
        change = scale_this / scale_prev
        return change


    def get_y_drift_px(self, fromFrameID, toFrameID):
        # type: (int, int) -> float
        df = self.__getPandasDF()
        cumulative_y = df["driftY"].cumsum()

        from_cum_drift = cumulative_y.iloc[self.__idx_of_frame_id(fromFrameID)]
        to_cum_drift = cumulative_y.iloc[self.__idx_of_frame_id(toFrameID)]

        return to_cum_drift - from_cum_drift

    def get_x_drift_px(self, fromFrameID, toFrameID):
        # type: (int, int) -> float
        df = self.__getPandasDF()
        cumulative_x = df["driftX"].cumsum()

        from_cum_drift = cumulative_x.iloc[self.__idx_of_frame_id(fromFrameID)]
        to_cum_drift = cumulative_x.iloc[self.__idx_of_frame_id(toFrameID)]

        return to_cum_drift - from_cum_drift

    def __idx_of_frame_id(self, frame_id):
        df = self.__getPandasDF()
        return df['frameNumber'][df['frameNumber'] == frame_id].index.tolist()[0]

    def getXDriftMM(self, fromFrameID, toFrameID):
        # type: (int, int) -> float
        startXCoordMM = self.getXCoordMMOrigin(fromFrameID)
        endXCoordMM = self.getXCoordMMOrigin(toFrameID)
        return endXCoordMM-startXCoordMM

    def getYDriftMM(self, fromFrameID, toFrameID):
        # type: (int, int) -> float
        startYCoordMM = self.getYCoordMMOrigin(fromFrameID)
        endYCoordMM = self.getYCoordMMOrigin(toFrameID)
        return endYCoordMM-startYCoordMM

    def heightMM(self,frame_id):
        # type: (int) -> float
        mmPerPixel = self.__getValueFromDF("mm_per_pixel", frame_id)
        return Frame.FRAME_HEIGHT*float(mmPerPixel)

    def widthMM(self,frame_id):
        # type: (int) -> float
        mmPerPixel = self.__getValueFromDF("mm_per_pixel", frame_id)
        return Frame.FRAME_WIDTH*float(mmPerPixel)


    def getYCoordMMOrigin(self, frame_id):
        # type: (int) -> float
        retValue = self.__getValueFromDF("driftY_sum_mm", frame_id)
        return float(retValue)

    def getXCoordMMOrigin(self, frame_id):
        # type: (int) -> float
        retValue = self.__getValueFromDF("driftX_sum_mm", frame_id)
        return float(retValue)

    def __getValueFromDF(self, columnName, frame_id):
        df = self.__getPandasDF()
        if df is None:
            return 0

        result = df.loc[(df['frameNumber'] == frame_id)][columnName]
        if result.empty:
            print ("Unexpected Result: in __getValueFromDF: frame_id", frame_id, "columnName", columnName)
            return 0

        # convert to array
        vals = result.values
        if len(vals) != 1:
            print ("Unexpected Result: in __getYCoordMMOrigin: frame_id", frame_id, "vals", vals, "result", result)
            return 0

        return vals[0]

    def refreshItself(self):
        self.__driftData = DriftData.createFromFolderStruct(self.__folderStruct)
        self.__redDotsData = RedDotsData.createFromFolderStruct(self.__folderStruct)
        self.saveToFile()

    def saveToFile(self):
        filepath = self.__folderStruct.getSeefloorFilepath()
        self.__df = self.__interpolate()
        self.__df.to_csv(filepath, sep='\t', index=False)

    def __interpolate(self):
        dfDrifts = self.getDriftData().getDF()
        dfRedDots = self.getRedDotsData().getPandasDF()
        dfRedDots = dfRedDots[["frameNumber", "distance", "mm_per_pixel"]]

        return self.__mergeDriftsAndRedDots(dfDrifts, dfRedDots)

    def __mergeDriftsAndRedDots(self, dfDrifts, dfRedDots):
        dfMerged = pd.merge(dfDrifts, dfRedDots, on='frameNumber', how='outer', suffixes=('_drift', '_reddots'))
        dfMerged["driftY_mm"] = dfMerged["driftY"] * dfMerged["mm_per_pixel"]
        dfMerged["driftX_mm"] = dfMerged["driftX"] * dfMerged["mm_per_pixel"]
        dfMerged["driftY_sum_mm"] = dfMerged["driftY_mm"].cumsum()
        dfMerged["driftX_sum_mm"] = dfMerged["driftX_mm"].cumsum()
        dfMerged["bottom_corner_mm"] = Frame.FRAME_HEIGHT * dfMerged["mm_per_pixel"] + dfMerged["driftY_sum_mm"]
        # dfMerged["center_coord_y_mm"] = int(Frame.FRAME_HEIGHT/2) * dfMerged["mm_per_pixel"] + dfMerged["driftY_sum_mm"]
        # dfMerged["center_coord_x_mm"] = int(Frame.FRAME_WIDTH/2) * dfMerged["mm_per_pixel"] + dfMerged["driftX_sum_mm"]
        dfMerged["seconds"] = dfMerged["frameNumber"]/VideoStream.FRAMES_PER_SECOND
        dfMerged = dfMerged.sort_values(by=['frameNumber'])
        return dfMerged

    def getPrevFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, -1)

    def getNextFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, 1)

    def translatePointCoordinate_new(self, pointLocation, origFrameID, targetFrameID):
        # type: (Point, int,int) -> Point

        #It seems that the "focal point" of picture when zooming in or zooming out is at one quarter above bottom edge equidistant from left and right. check out drift vectors for each featureMatcher in detectDrifts.

        target_mm_per_pixel = self.__getValueFromDF("mm_per_pixel", targetFrameID)
        center_coordinate_x_mm_target = - int(Frame.FRAME_WIDTH/2) * target_mm_per_pixel + self.__getValueFromDF("driftX_sum_mm", targetFrameID)
        center_coordinate_y_mm_target = -int(3*Frame.FRAME_HEIGHT/4) * target_mm_per_pixel + self.__getValueFromDF("driftY_sum_mm", targetFrameID)
        center_coordinate_mm_target = Point(center_coordinate_x_mm_target, center_coordinate_y_mm_target)

        orig_mm_per_pixel = self.__getValueFromDF("mm_per_pixel", origFrameID)
        center_coordinate_x_mm_orig = int(Frame.FRAME_WIDTH/2) * orig_mm_per_pixel + self.__getValueFromDF("driftX_sum_mm", origFrameID)
        center_coordinate_y_mm_orig = -int(3*Frame.FRAME_HEIGHT/4) * orig_mm_per_pixel + self.__getValueFromDF("driftY_sum_mm", origFrameID)
        center_coordinate_mm_orig = Point(center_coordinate_x_mm_orig, center_coordinate_y_mm_orig)

        point_coordinate_x_mm = (-pointLocation.x) * orig_mm_per_pixel + self.__getValueFromDF("driftX_sum_mm", origFrameID)
        point_coordinate_y_mm = (-pointLocation.y) * orig_mm_per_pixel + self.__getValueFromDF("driftY_sum_mm", origFrameID)
        point_coordinate_mm = Point(point_coordinate_x_mm, point_coordinate_y_mm)

        print("origFrameID", origFrameID, "targetFrameID",targetFrameID, "pointLocation", str(pointLocation),  "point_coordinate_mm", str(point_coordinate_mm), "center_coordinate_mm_target", str(center_coordinate_mm_target), "center_coordinate_mm_orig", str(center_coordinate_mm_orig))

        distance_x_mm = point_coordinate_x_mm - center_coordinate_x_mm_target
        distance_y_mm = point_coordinate_y_mm - center_coordinate_y_mm_target


        point_x_px = int(Frame.FRAME_WIDTH/2) - int(distance_x_mm/target_mm_per_pixel)
        point_y_px = int(3*Frame.FRAME_HEIGHT/4) - int(distance_y_mm/target_mm_per_pixel)

        point = Point(point_x_px, point_y_px)
        print ("newPoint: ", str(point), "oldPoint: ", str(self.translatePointCoordinate_old(pointLocation, origFrameID, targetFrameID)))

        return point

    def translatePointCoordinate(self, pointLocation, origFrameID, targetFrameID):
        # type: (Point, int,int) -> Point
        point_location_new = pointLocation

        individual_frames = FrameId.sequence_of_frames(origFrameID, targetFrameID)
        for idx in range(len(individual_frames) - 1):
            from_frame_id = individual_frames[idx]
            to_frame_id = individual_frames[idx + 1]
            point_location_new = self.__translate_point_one_frame(point_location_new, from_frame_id, to_frame_id)

        return point_location_new

    def __translate_point_one_frame(self, pointLocation, origFrameID, targetFrameID):
        # type: (Point, int,int) -> Point
        drift = self.get_drift_instantaneous(targetFrameID)
        depth_scaling_factor = self.zoom_instantaneous(targetFrameID)
        if targetFrameID < origFrameID:
            drift = drift.invert()
            depth_scaling_factor = 1/depth_scaling_factor

        point_after_drift = pointLocation.translateBy(drift)
        point_after_depth_scaling = self.adjust_location_for_depth_change_zoom(point_after_drift, depth_scaling_factor)
        return point_after_depth_scaling

    @staticmethod
    def adjust_location_for_depth_change_zoom(point, scaling_factor):
        # type: (Point, float) -> Point
        mid_frame_width = Frame.FRAME_WIDTH / 2
        x_offset_from_middle_old = point.x - mid_frame_width
        x_offset_from_middle_new = x_offset_from_middle_old / scaling_factor
        new_x = mid_frame_width + x_offset_from_middle_new

        mid_frame_height = Frame.FRAME_HEIGHT / 2
        y_offset_from_middle_old = point.y - mid_frame_height
        y_offset_from_middle_new = y_offset_from_middle_old / scaling_factor
        new_y = mid_frame_height + y_offset_from_middle_new

        return Point(int(new_x), int(new_y))

    def saveGraphSeefloorY(self):
        # filePath = self.__folderStruct.getSubDirpath()+"/graph_y.png"#self.__folderStruct.getRedDotsGraphAngle()
        filePath = self.__folderStruct.getGraphSeefloorAdvancementY()
        graphTitle = self.__folderStruct.getVideoFilename()+ " seefloor advancement along Y (vertical/forward) axis (mm)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftY_sum_mm"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphSeefloorX(self):
        # filePath = self.__folderStruct.getSubDirpath()+"/graph_x.png"#self.__folderStruct.getRedDotsGraphAngle()
        filePath = self.__folderStruct.getGraphSeefloorAdvancementX()
        graphTitle = self.__folderStruct.getVideoFilename()+ " seefloor advancement along X (horizontal/sideways) axis (mm)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftX_sum_mm"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphSeefloorXY(self):
        # filePath = self.__folderStruct.getSubDirpath()+"/graph_xy.png"#self.__folderStruct.getRedDotsGraphAngle()
        filePath = self.__folderStruct.getGraphSeefloorPathXY()
        graphTitle = self.__folderStruct.getVideoFilename()+ " seefloor advancement X and Y axis (mm)"
        xColumn = "driftX_sum_mm"
        yColumns = ["driftY_sum_mm"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFileVertical(xColumn, yColumns, graphTitle, filePath)

    def saveGraphDriftsMillimeters(self):
        # filePath = self.__folderStruct.getSubDirpath()+"/graph_drifts.png"#self.__folderStruct.getRedDotsGraphAngle()
        filePath = self.__folderStruct.getGraphDriftPerFrameMM()
        graphTitle = self.__folderStruct.getVideoFilename()+ " drift (mm)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftY_mm", "driftX_mm"] #"driftX", "driftY"

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphDriftsPixels(self):
        filePath = self.__folderStruct.getGraphDriftPerFramePixels()
        graphTitle = self.__folderStruct.getVideoFilename()+ " drift (pixels)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftY", "driftX"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)