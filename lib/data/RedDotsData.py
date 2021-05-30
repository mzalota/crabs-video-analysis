import math

import pandas as pd
import numpy

from lib.FolderStructure import FolderStructure
from lib.data.GraphPlotter import GraphPlotter
from lib.data.PandasWrapper import PandasWrapper
from lib.common import Point
from lib.data.RedDotsManualData import RedDotsManualData
from lib.data.RedDotsRawData import RedDotsRawData


class RedDotsData(PandasWrapper):
    #__rawDF = None
    #__manualDF = None
    #__interpolatedDF = None
    # columns = ["frameNumber","centerPoint_x_dot1","centerPoint_y_dot1", "origin_dot1", "centerPoint_x_dot2", "centerPoint_y_dot2", "origin_dot2", "distance", "mm_per_pixel", "angle"]

    __VALUE_redDot1 = "redDot1"
    __VALUE_redDot2 = "redDot2"

    VALUE_ORIGIN_interpolate = "interpolate"
    VALUE_ORIGIN_manual = "manual"
    VALUE_ORIGIN_raw = "raw"

    COLNAME_frameNumber = 'frameNumber'
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"
    __COLNAME_mm_per_pixel = "mm_per_pixel"
    __COLNAME_angle = "angle"
    __COLNAME_distance = "distance"

    __distance_between_reddots_mm = 300

    def __init__(self, folderStruct, redDotsManual):
        # type: (FolderStructure, RedDotsManualData) -> RedDotsData
        self.__folderStruct = folderStruct
        self.__redDotsManual = redDotsManual

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> RedDotsData
        redDotsManual = RedDotsManualData(folderStruct)
        newObj = RedDotsData(folderStruct, redDotsManual)
        return newObj

    @staticmethod
    def createWithRedDotsManualData(folderStruct, redDotsManual):
        # type: (FolderStructure, RedDotsManualData) -> RedDotsData

        newObj = RedDotsData(folderStruct, redDotsManual)
        return newObj

    def addManualDots(self, frameID, box):
        self.__redDotsManual.addManualDots(frameID,box)
        self.saveInterpolatedDFToFile()

    def getPandasDF(self):
        # type: () -> pd
        try:
            return self.__interpolatedDF
        except AttributeError:
            # attribute self.__interpolatedDF have not been initialized yet
            filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
            if self.__folderStruct.fileExists(filepath):
                self.__interpolatedDF = self.readDataFrameFromCSV(filepath)
            else:
                self.__interpolatedDF = PandasWrapper.empty_df()
            return self.__interpolatedDF

    def saveGraphOfAngle(self):
        filePath = self.__folderStruct.getRedDotsGraphAngle()
        graphTitle = self.__folderStruct.getVideoFilename()+ " Angle (degrees)"
        xColumn = self.COLNAME_frameNumber
        yColumns = [self.__COLNAME_angle]

        graphPlotter = GraphPlotter(self.getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphOfDistance(self):
        filePath = self.__folderStruct.getRedDotsGraphDistance()
        graphTitle = self.__folderStruct.getVideoFilename()+ " Distance (pixels)"
        xColumn = self.COLNAME_frameNumber
        yColumns = [self.__COLNAME_distance]

        graphPlotter = GraphPlotter(self.getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def getCount(self):
        # type: () -> int
        return len(self.getPandasDF().index)

    def midPoint(self, frameId):
        redDot1 = self.getRedDot1(frameId)
        redDot2 = self.getRedDot2(frameId)
        return redDot1.calculateMidpoint(redDot2)

    def getRedDot1(self, frameId):
        # type: (int) -> Point
        dfResult = self.__rowForFrame(frameId)
        x = dfResult["centerPoint_x_dot1"].iloc[0]
        y = dfResult["centerPoint_y_dot1"].iloc[0]
        return Point(int(x),int(y))

    def getRedDot2(self, frameId):
        # type: (int) -> Point
        dfResult = self.__rowForFrame(frameId)
        x = dfResult["centerPoint_x_dot2"].iloc[0]
        y = dfResult["centerPoint_y_dot2"].iloc[0]
        return Point(int(x),int(y))

    def getDistancePixels(self, frameId):
        # type: (int) -> float
        dfResult = self.__rowForFrame(frameId)
        return dfResult["distance"].iloc[0]

    def scalingFactor(self, referenceFrameID, frameIDToScale):
        # type: (int, int) -> float
        distanceRef = self.getDistancePixels(referenceFrameID)
        distanceToScale = self.getDistancePixels(frameIDToScale)
        scalingFactor = distanceRef / distanceToScale
        return scalingFactor

    def getMMPerPixel(self, frameId):
        # type: (int) -> float
        dfResult = self.__rowForFrame(frameId)
        return dfResult["mm_per_pixel"].iloc[0]

    def __rowForFrame(self, frameId):
        df = self.getPandasDF()
        dfResult = df.loc[df[RedDotsData.COLNAME_frameNumber] == frameId]
        return dfResult

    def saveInterpolatedDFToFile(self, minFrameID=None, maxFrameID=None):
        interpolatedDF = self.__generateIntepolatedDF(minFrameID, maxFrameID)
        filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
        interpolatedDF.to_csv(filepath, sep='\t', index=False)
        self.__interpolatedDF = interpolatedDF

    def __generateIntepolatedDF(self, minVal, maxVal):
        df = self.__add_rows_for_every_frame(minVal, maxVal)
        df = self.__interpolate_values(df)
        self.__calculateDerivedValues(df)

        self.__clearOutliersBasedOnAngle(df)
        df = self.__interpolate_values(df)
        self.__calculateDerivedValues(df)

        self.__clearOutliersBasedOnDistance(df)
        df = self.__interpolate_values(df)
        self.__calculateDerivedValues(df)
        return df

    def __add_rows_for_every_frame(self, minVal, maxVal):
        df = self.forPlotting()
        if minVal is None:
            minVal = df["frameNumber"].min()
        if maxVal is None:
            maxVal = df["frameNumber"].max()

        df = df.set_index("frameNumber")
        everyFrame = pd.DataFrame(numpy.arange(start=minVal, stop=maxVal, step=1), columns=["frameNumber"]).set_index(
            "frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        return df

    def __calculateDerivedValues(self, df):
        self.__recalculate_column_distance(df)
        self.__recalculate_column_angle(df)

    def __recalculate_column_distance(self, df):
        df['distance'] = pow(pow(df["centerPoint_x_dot2"] - df["centerPoint_x_dot1"], 2) + pow(
            df["centerPoint_y_dot2"] - df["centerPoint_y_dot1"], 2), 0.5)  # .astype(int)
        df[self.__COLNAME_mm_per_pixel] = self.__distance_between_reddots_mm / df['distance']

    def __recalculate_column_angle(self, df):
        yLength_df = (df["centerPoint_y_dot1"] - df["centerPoint_y_dot2"])
        xLength_df = (df["centerPoint_x_dot1"] - df["centerPoint_x_dot2"])
        angle_in_radians = numpy.arctan(yLength_df / xLength_df)*(-1)
        df[self.__COLNAME_angle] = angle_in_radians / math.pi * 90

    def __interpolate_values(self, df):
        df = df.interpolate(limit_direction='both')

        df.loc[pd.isna(df["origin_dot1"]), ["origin_dot1"]] = self.VALUE_ORIGIN_interpolate
        df.loc[pd.isna(df["origin_dot2"]), ["origin_dot2"]] = self.VALUE_ORIGIN_interpolate
        return df

    def __clearOutliersBasedOnDistance(self, df):
        column_with_outliers = 'distance'
        upper_99 = numpy.percentile(df[column_with_outliers], 99)
        lower_1 = numpy.percentile(df[column_with_outliers], 1)

        upper_95 = numpy.percentile(df[column_with_outliers], 95)
        lower_5 = numpy.percentile(df[column_with_outliers], 5)

        upper_bound = upper_95 + (upper_95-lower_5)/4
        lower_bound = lower_5 - (upper_95-lower_5)/4

        print("outlier column", column_with_outliers, "Upper bound", upper_bound, "Lower bound", lower_bound, "95th percentile", upper_95, "5th percentile", lower_5, "99th percentile", upper_99, "1st percentile", lower_1)

        self.__clear_outlier_rows(df, column_with_outliers, lower_bound, upper_bound)

    def __clearOutliersBasedOnAngle(self, df):
        column_with_outliers = self.__COLNAME_angle
        upper_99 = numpy.percentile(df[column_with_outliers], 99)
        lower_1 = numpy.percentile(df[column_with_outliers], 1)

        upper_95 = numpy.percentile(df[column_with_outliers], 95)
        lower_5 = numpy.percentile(df[column_with_outliers], 5)

        upper_bound = upper_95 + (upper_95-lower_5)/4
        lower_bound = lower_5 - (upper_95-lower_5)/4

        print("outlier column", column_with_outliers, "Upper bound", upper_bound, "angle lower bound", lower_bound, "95th percentile", upper_95, "5th percentile", lower_5, "99th percentile", upper_99, "1st percentile", lower_1)

        #median_angle
        median_angle = self.__redDotsManual.median_angle()
        if median_angle:
            lower_bound = median_angle -2
            upper_bound = median_angle +2
            print("median_angle", median_angle, "angle Upper bound", upper_bound, "angle lower bound", lower_bound,)

        self.__clear_outlier_rows(df, column_with_outliers, lower_bound, upper_bound)

    def __clear_outlier_rows(self, df, column_with_outliers, lower_bound, upper_bound):
        # clear the values in rows where value of the angle is off bounds
        columns_with_wrong_values = ["centerPoint_x_dot1", "centerPoint_x_dot2", "centerPoint_y_dot1",
                                     "centerPoint_y_dot2", "angle", "distance", "mm_per_pixel"]

        not_manual = (df["origin_dot1"] != self.VALUE_ORIGIN_manual) & (df["origin_dot2"] != self.VALUE_ORIGIN_manual)
        outlier_rows = ((df[column_with_outliers] < lower_bound) | (
                    df[column_with_outliers] > upper_bound)) & not_manual
        df.loc[outlier_rows, columns_with_wrong_values] = numpy.nan

    def __replaceOutlierBetweenTwo_orig(self, df, columnName):
        outlier_threshold = 100
        prevValue = df[columnName].shift(periods=1)
        nextValue = df[columnName].shift(periods=-1)
        diffNextPrev = abs(prevValue - nextValue)
        meanPrevNext = (prevValue + nextValue) / 2
        deviation = abs(df[columnName] - meanPrevNext)
        single_outlier = (deviation > outlier_threshold) & (diffNextPrev < outlier_threshold)
        df.drop(df[single_outlier].index, inplace=True)

    def forPlotting(self):
        dataRedDot1 = self.__combinedOnlyRedDot1()[[self.COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y, "origin"]]
        dataRedDot2 = self.__combinedOnlyRedDot2()[[self.COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y, "origin"]]

        dfToPlot = pd.merge(dataRedDot1, dataRedDot2, on='frameNumber', how='outer', suffixes=('_dot1', '_dot2'))

        return dfToPlot.sort_values(by=['frameNumber'])

    def __combinedDF(self):
        # type: () -> pd.DataFrame
        redDotsManual = RedDotsManualData(self.__folderStruct)
        redDotsRawData = RedDotsRawData.createFromCSVFile(self.__folderStruct)
        return redDotsManual.combine_with_raw_data(redDotsRawData)

    def __combinedOnlyRedDot2(self):
        # type: () -> pd
        dataRedDot2 = self.__combinedDF().loc[self.__combinedDF()['dotName'] == self.__VALUE_redDot2]
        return dataRedDot2

    def __combinedOnlyRedDot1(self):
        # type: () -> pd
        dataRedDot1 = self.__combinedDF().loc[self.__combinedDF()['dotName'] == self.__VALUE_redDot1]
        return dataRedDot1

    def getMiddleFrameIDOfBiggestGap(self):
        # type: () -> int
        if self.getCount() <=0:
            return None

        frameId1, gap1 = self.__find_largest_gap('origin_dot1')
        frameId2, gap2 = self.__find_largest_gap('origin_dot2')
        print ("RedDotsData::getMiddleFrameIDOfBiggestGap", "frameId1", frameId1, "gap1", gap1,"frameId2", frameId2, "gap2", gap2)
        if gap1 > gap2:
            return frameId1, gap1
        else:
            return frameId2, gap2

    def __find_largest_gap(self, whichDot):
        # type: (str) -> int, float

        firstFrame = self.__minFrameID()
        lastFrame = self.__maxFrameID()
        df = self.getPandasDF()

        #masks
        first_or_last_row_mask = (df[self.COLNAME_frameNumber] == firstFrame) | (df[self.COLNAME_frameNumber] == lastFrame)
        non_interpolate_rows_mask = (df[whichDot] != self.VALUE_ORIGIN_interpolate)

        wipDF = df.loc[(non_interpolate_rows_mask | first_or_last_row_mask)].copy()

        wipDF["prevFrameID"] = wipDF[self.COLNAME_frameNumber].shift(periods=-1)
        wipDF["gap"] = wipDF["prevFrameID"] - wipDF[self.COLNAME_frameNumber]
        wipDF["midFrameID"] = wipDF[self.COLNAME_frameNumber] + wipDF["gap"] / 2

        maxGap = wipDF['gap'].max()
        firstLargestGap = wipDF.loc[(wipDF['gap'] == maxGap)]
        asDict = firstLargestGap.to_dict('records')

        frameInTheMiddleOfLargestGap = asDict[0]["midFrameID"]
        gapSize = asDict[0]["gap"]
        return int(frameInTheMiddleOfLargestGap), gapSize

    def __minFrameID(self):
        # type: () -> int
        return self.getPandasDF()[self.COLNAME_frameNumber].min() #[0]

    def __maxFrameID(self):
        # type: () -> int
        return self.getPandasDF()[self.COLNAME_frameNumber].max()

