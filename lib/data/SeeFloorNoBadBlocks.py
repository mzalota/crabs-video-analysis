import numpy

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
        # type: (DriftData, BadFramesData, RedDotsData) -> SeeFloorNoBadBlocks
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

    def getDF(self):
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
        df = self.getDF()
        if df is None:
            return None

        # print("SeeFloorNoBadBlocks.getFrame() yMMAway")

        yCoordMMOrigin = self.__getYCoordMMOrigin(fromFrameID)
        yCoordMMDestination = yCoordMMOrigin + yMMAway

        if yCoordMMDestination < self.__getYCoordMMOrigin(self.minFrameID()):
            return self.minFrameID()

        if yCoordMMDestination > self.__getYCoordMMOrigin(self.maxFrameID()):
            return self.maxFrameID()

        result = df.loc[(df['driftY_sum_mm'] < yCoordMMDestination)].max()["frameNumber"]
        if result and not numpy.isnan(result):
            nextFrameID = int(result)
        else:
            print("Something wierd ine SeeFloor.getFrame: yCoordMMDestination", yCoordMMDestination, "fromFrameID", fromFrameID, "yMMAway", yMMAway,
                  "yCoordMMOrigin", yCoordMMOrigin)
            nextFrameID = fromFrameID
        return nextFrameID

    def driftBetweenFrames(self, fromFrameID, toFrameID):
        # type: (int, int) -> Vector

        if fromFrameID < self.__driftData.minFrameID() or toFrameID < self.__driftData.minFrameID():
            # return Vector(0,0)
            return None

        if fromFrameID > self.__driftData.maxFrameID() or toFrameID > self.__driftData.maxFrameID():
            # return Vector(0, 0)
            return None

        if (fromFrameID == toFrameID):
            return Vector(0, 0)

        driftX = self.getXDriftPixels(fromFrameID, toFrameID)
        driftY = self.getYDriftPixels(fromFrameID, toFrameID)

        return Vector(driftX, driftY)

    def getXDriftPixels(self, fromFrameID, toFrameID):
        # type: (int, int) -> int
        xDriftMM = self.getXDriftMM(fromFrameID, toFrameID)
        #mmPerPixel = self.getRedDotsData().getMMPerPixel(fromFrameID)
        mmPerPixel = self.getRedDotsData().getMMPerPixel(toFrameID)
        xDrift = xDriftMM/mmPerPixel
        return int(xDrift)

    def getYDriftPixels(self, fromFrameID, toFrameID):
        # type: (int, int) -> int
        yDriftMM = self.getYDriftMM(fromFrameID, toFrameID)
        mmPerPixel = self.getRedDotsData().getMMPerPixel(fromFrameID)
        yDrift = yDriftMM/mmPerPixel
        return int(yDrift)

    def getXDriftMM(self,fromFrameID, toFrameID):
        # type: (int, int) -> float
        startXCoordMM = self.__getXCoordMMOrigin(fromFrameID)
        endXCoordMM = self.__getXCoordMMOrigin(toFrameID)
        return endXCoordMM-startXCoordMM

    def getYDriftMM(self,fromFrameID, toFrameID):
        # type: (int, int) -> float
        startYCoordMM = self.__getYCoordMMOrigin(fromFrameID)
        endYCoordMM = self.__getYCoordMMOrigin(toFrameID)
        return endYCoordMM-startYCoordMM

    def heightMM(self,frame_id):
        # type: (int) -> float
        mmPerPixel = self.__getValueFromDF("mm_per_pixel", frame_id)
        return Frame.FRAME_HEIGHT*float(mmPerPixel)

    def widthMM(self,frame_id):
        # type: (int) -> float
        mmPerPixel = self.__getValueFromDF("mm_per_pixel", frame_id)
        return Frame.FRAME_WIDTH*float(mmPerPixel)


    def __getYCoordMMOrigin(self, frame_id):
        # type: (int) -> float
        retValue = self.__getValueFromDF("driftY_sum_mm", frame_id)
        return float(retValue)

    def __getXCoordMMOrigin(self, frame_id):
        # type: (int) -> float
        retValue = self.__getValueFromDF("driftX_sum_mm", frame_id)
        return float(retValue)

    def __getValueFromDF(self, columnName, frame_id):
        df = self.getDF()
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
        dfRedDots = dfRedDots[["frameNumber","distance", "mm_per_pixel"]]

        return self.__mergeDriftsAndRedDots(dfDrifts, dfRedDots)

    def __mergeDriftsAndRedDots(self, dfDrifts, dfRedDots):
        dfMerged = pd.merge(dfDrifts, dfRedDots, on='frameNumber', how='outer', suffixes=('_drift', '_reddots'))
        dfMerged["driftY_mm"] = dfMerged["driftY"] * dfMerged["mm_per_pixel"]
        dfMerged["driftX_mm"] = dfMerged["driftX"] * dfMerged["mm_per_pixel"]
        dfMerged["driftY_sum_mm"] = dfMerged["driftY_mm"].cumsum()
        dfMerged["driftX_sum_mm"] = dfMerged["driftX_mm"].cumsum()
        dfMerged["bottom_corner_mm"] = Frame.FRAME_HEIGHT * dfMerged["mm_per_pixel"] + dfMerged["driftY_sum_mm"]
        dfMerged = dfMerged.sort_values(by=['frameNumber'])
        return dfMerged

    def getPrevFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, -1)

    def getNextFrame(self, frame_id):
        # type: (int) -> int
        return self.jumpToSeefloorSlice(frame_id, 1)


    def translatePointCoordinate(self, pointLocation, origFrameID, targetFrameID):
        # type: (Point, int,int) -> Point
        drift = self.driftBetweenFrames(origFrameID, targetFrameID)
        scalingFactor = self.getRedDotsData().scalingFactor(origFrameID, targetFrameID)

        newPoint = pointLocation.translateBy(drift)
        X = newPoint.x
        if X < Frame.FRAME_WIDTH / 2:
            xOffsetFromMiddle = (Frame.FRAME_WIDTH / 2 - X) / scalingFactor
            newX = int(Frame.FRAME_WIDTH / 2 - xOffsetFromMiddle)
            # print ("X smaller old ", X, "newX",newX,"xOffsetFromMiddle",xOffsetFromMiddle,Frame.FRAME_WIDTH)
            newPoint = Point(newX, newPoint.y)
        if X > Frame.FRAME_WIDTH / 2:
            xOffsetFromMiddle = (X - Frame.FRAME_WIDTH / 2) / scalingFactor
            newX = int(Frame.FRAME_WIDTH / 2 + xOffsetFromMiddle)
            # print ("X bigger old ", X, "newX",newX,"xOffsetFromMiddle",xOffsetFromMiddle,Frame.FRAME_WIDTH)
            newPoint = Point(newX, newPoint.y)

        Y = newPoint.y
        if Y < Frame.FRAME_HEIGHT / 2:
            yOffsetFromMiddle = (Frame.FRAME_HEIGHT / 2 - Y) / scalingFactor
            newY = int(Frame.FRAME_HEIGHT / 2 - yOffsetFromMiddle)
            newPoint = Point(newPoint.x, newY)

        if Y > Frame.FRAME_HEIGHT / 2:
            yOffsetFromMiddle = (Y - Frame.FRAME_HEIGHT / 2) / scalingFactor
            newY = int(Frame.FRAME_HEIGHT / 2 + yOffsetFromMiddle)
            newPoint = Point(newPoint.x, newY)

        return newPoint

    def saveGraphSeefloorY(self):
        filePath = self.__folderStruct.getSubDirpath()+"/graph_y.png"#self.__folderStruct.getRedDotsGraphAngle()
        graphTitle = self.__folderStruct.getVideoFilename()+ " seefloor advancement along Y (vertical) axis"
        xColumn = "frameNumber"
        yColumns = ["driftY_sum_mm"]

        graphPlotter = GraphPlotter(self.getDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphSeefloorX(self):
        filePath = self.__folderStruct.getSubDirpath()+"/graph_x.png"#self.__folderStruct.getRedDotsGraphAngle()
        graphTitle = self.__folderStruct.getVideoFilename()+ " seefloor advancement along X (horizontal) axis "
        xColumn = "frameNumber"
        yColumns = ["driftX_sum_mm"]

        graphPlotter = GraphPlotter(self.getDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphSeefloorXY(self):
        filePath = self.__folderStruct.getSubDirpath()+"/graph_xy.png"#self.__folderStruct.getRedDotsGraphAngle()
        graphTitle = self.__folderStruct.getVideoFilename()+ " seefloor advancement along X (horizontal) axis "
        xColumn = "driftX_sum_mm"
        yColumns = ["driftY_sum_mm"]

        graphPlotter = GraphPlotter(self.getDF())
        graphPlotter.saveGraphToFileVertical(xColumn, yColumns, graphTitle, filePath)

    def saveGraphDrifts(self):
        filePath = self.__folderStruct.getSubDirpath()+"/graph_drifts.png"#self.__folderStruct.getRedDotsGraphAngle()
        graphTitle = self.__folderStruct.getVideoFilename()+ " drift (pixels)"
        xColumn = "frameNumber"
        yColumns = ["driftY_mm", "driftX_mm"] #"driftX", "driftY"

        graphPlotter = GraphPlotter(self.getDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)