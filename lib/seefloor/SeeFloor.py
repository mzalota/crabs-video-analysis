from __future__ import annotations

import numpy

from lib.drifts_interpolate.DriftInterpolatedData import DriftInterpolatedData
from lib.imageProcessing.Camera import Camera
from lib.VideoStream import VideoStream
from lib.model.Point import Point
from lib.infra.GraphPlotter import GraphPlotter
from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsData import RedDotsData
from lib.infra.FolderStructure import FolderStructure
import pandas as pd

from lib.seefloor.SeeFloorFast import SeeFloorFast
from lib.seefloor.PointTranslator import PointTranslator
from lib.seefloor.SeeFloorSlicer import SeeFloorSlicer


class SeeFloor(PandasWrapper):
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'
    _COLNAME_frameNumber = 'frameNumber'

    def __init__(self, driftsData: DriftInterpolatedData, redDotsData: RedDotsData, folderStruct : FolderStructure = None,  df = None) -> SeeFloor:
        self.__driftData = driftsData
        self.__redDotsData = redDotsData
        self.__df = df
        self._folderStruct = folderStruct
        self.__fastObj = SeeFloorFast(df)
        self.__pointTranslator = PointTranslator(self.__fastObj)
        self.__slicer = SeeFloorSlicer(self.__pointTranslator, self.__fastObj)

    @staticmethod
    def createFromFolderStruct(folderStruct: FolderStructure) -> SeeFloor:

        driftsData = DriftInterpolatedData.createFromFolderStruct(folderStruct)
        redDotsData = RedDotsData.createFromFolderStruct(folderStruct)

        filepath = folderStruct.getSeefloorFilepath()
        if folderStruct.fileExists(filepath):
            #df = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
            df = PandasWrapper.readDataFrameFromCSV(filepath)
        else:
            df = None
        newObj = SeeFloor(driftsData, redDotsData, folderStruct, df)
        return newObj

    def getDriftData(self) -> DriftInterpolatedData:
        return self.__driftData

    def getRedDotsData(self) -> RedDotsData:
        return self.__redDotsData

    def maxFrameID(self):
        # type: () -> int
        return self.__df[self._COLNAME_frameNumber].max()
        # return self._max_frame_id()

    def minFrameID(self):
        # type: () -> int
        return self.__df[self._COLNAME_frameNumber].min()

    def __getPandasDF(self):
        # type: () -> pd.DataFrame
        try:
            return self.__df
        except AttributeError:
            return None

    def getFrame(self, yMMAway: int, fromFrameID: int) ->int:
        # type: (float, int) -> int
        df = self.__getPandasDF()
        if df is None:
            return None

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


    def getXDriftPixels(self, fromFrameID, toFrameID):
        # type: (int, int) -> int
        xDriftMM = self.getXDriftMM(fromFrameID, toFrameID)
        # mmPerPixel = self.getRedDotsData().getMMPerPixel(fromFrameID)
        mmPerPixel = self.getRedDotsData().getMMPerPixel(toFrameID)
        xDrift = xDriftMM/mmPerPixel
        return int(xDrift)

    def __getYDriftPixels(self, fromFrameID, toFrameID):
        # type: (int, int) -> int
        yDriftMM = self.__getYDriftMM(fromFrameID, toFrameID)
        # mmPerPixel = self.getRedDotsData().getMMPerPixel(fromFrameID)
        mmPerPixel = self.getRedDotsData().getMMPerPixel(toFrameID)
        yDrift = yDriftMM/mmPerPixel
        result = int(yDrift)

        return result

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

    def __getYDriftMM(self, fromFrameID, toFrameID):
        # type: (int, int) -> float
        startYCoordMM = self.getYCoordMMOrigin(fromFrameID)
        endYCoordMM = self.getYCoordMMOrigin(toFrameID)
        return endYCoordMM-startYCoordMM

    def translatePointCoord(self, pointLocation: Point, origFrameID: int, targetFrameID: int) -> Point:
        return self.__pointTranslator.translatePointCoordinate(pointLocation, origFrameID, targetFrameID)
    def mm_per_pixel(self, frame_id):
        return self.__fastObj._mm_per_pixel(frame_id)

    def heightMM(self, frame_id):
        # type: (int) -> float
        mmPerPixel = self.mm_per_pixel(frame_id)
        height_mm = Camera.create().frame_height() * float(mmPerPixel)
        return height_mm

    def widthMM(self,frame_id):
        # type: (int) -> float
        mmPerPixel = self.mm_per_pixel(frame_id)
        width_mm = Camera.create().frame_width() * float(mmPerPixel)
        return width_mm

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
        self.__driftData = DriftInterpolatedData.createFromFolderStruct(self._folderStruct)
        self.__redDotsData = RedDotsData.createFromFolderStruct(self._folderStruct)
        self.saveToFile()

    def saveToFile(self):
        filepath = self._folderStruct.getSeefloorFilepath()
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

        camera = Camera.create()
        dfMerged["bottom_corner_mm"] = camera.frame_height() * dfMerged["mm_per_pixel"] + dfMerged["driftY_sum_mm"]
        # dfMerged["bottom_corner_mm"] = Frame.FRAME_HEIGHT * dfMerged["mm_per_pixel"] + dfMerged["driftY_sum_mm"]
        dfMerged["seconds"] = dfMerged["frameNumber"]/VideoStream.FRAMES_PER_SECOND
        dfMerged = dfMerged.sort_values(by=['frameNumber'])
        return dfMerged

    #translates the point stepwise for each frame between orig and target.

    def saveGraphSeefloorY(self):
        filePath = self._folderStruct.getGraphSeefloorAdvancementY()
        graphTitle = self._folderStruct.getVideoFilename() + " seefloor advancement along Y (vertical/forward) axis (mm)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftY_sum_mm"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphSeefloorX(self):
        # filePath = self.__folderStruct.getSubDirpath()+"/graph_x.png"#self.__folderStruct.getRedDotsGraphAngle()
        filePath = self._folderStruct.getGraphSeefloorAdvancementX()
        graphTitle = self._folderStruct.getVideoFilename() + " seefloor advancement along X (horizontal/sideways) axis (mm)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftX_sum_mm"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphSeefloorXY(self):
        # filePath = self.__folderStruct.getSubDirpath()+"/graph_xy.png"#self.__folderStruct.getRedDotsGraphAngle()
        filePath = self._folderStruct.getGraphSeefloorPathXY()
        graphTitle = self._folderStruct.getVideoFilename() + " seefloor advancement X and Y axis (mm)"
        xColumn = "driftX_sum_mm"
        yColumns = ["driftY_sum_mm"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFileVertical(xColumn, yColumns, graphTitle, filePath)

    def saveGraphDriftsMillimeters(self):
        # filePath = self.__folderStruct.getSubDirpath()+"/graph_drifts.png"#self.__folderStruct.getRedDotsGraphAngle()
        filePath = self._folderStruct.getGraphDriftPerFrameMM()
        graphTitle = self._folderStruct.getVideoFilename() + " drift (mm)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftY_mm", "driftX_mm"] #"driftX", "driftY"

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphDriftsPixels(self):
        filePath = self._folderStruct.getGraphDriftPerFramePixels()
        graphTitle = self._folderStruct.getVideoFilename() + " drift (pixels)"
        xColumn = ["frameNumber", "seconds"]
        yColumns = ["driftY", "driftX"]

        graphPlotter = GraphPlotter(self.__getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def jumpToSeefloorSlice(self, frame_id, frames_to_jump):
        return self.__slicer.jumpToSeefloorSlice(frame_id, frames_to_jump)

    def getPrevFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, -1)

    def getNextFrame(self, frame_id: int) -> int:
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, 1)

