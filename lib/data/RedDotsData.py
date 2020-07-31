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

    __VALUE_redDot1 = "redDot1"
    __VALUE_redDot2 = "redDot2"


    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"
    __COLNAME_mm_per_pixel = "mm_per_pixel"
    __COLNAME_angle = "angle"
    __COLNAME_distance = "distance"

    __distance_between_reddots_mm = 300

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> RedDotsData
        self.__folderStruct = folderStruct
        self.__redDotsManual = RedDotsManualData(folderStruct)

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> RedDotsData
        newObj = RedDotsData(folderStruct)
        return newObj

    def addManualDots(self, frameID, box):
        self.__redDotsManual.addManualDots(frameID,box)

    def getPandasDF(self):
        # type: () -> pd
        try:
            return self.__interpolatedDF
        except AttributeError:
            # attribute self.__interpolatedDF have not been initialized yet
            filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
            self.__interpolatedDF = self.readDataFrameFromCSV(filepath)
            return self.__interpolatedDF

    def saveGraphOfAngle(self):
        filePath = self.__folderStruct.getRedDotsGraphAngle()
        graphTitle = self.__folderStruct.getVideoFilename()+ " Angle (degrees)"
        xColumn = self.__COLNAME_frameNumber
        yColumns = [self.__COLNAME_angle]

        graphPlotter = GraphPlotter(self.getPandasDF())
        graphPlotter.saveGraphToFile(xColumn, yColumns, graphTitle, filePath)

    def saveGraphOfDistance(self):
        filePath = self.__folderStruct.getRedDotsGraphDistance()
        graphTitle = self.__folderStruct.getVideoFilename()+ " Distance (pixels)"
        xColumn = self.__COLNAME_frameNumber
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
        dfResult = df.loc[df[RedDotsData.__COLNAME_frameNumber] == frameId]
        return dfResult

    def saveInterpolatedDFToFile(self, minFrameID=None, maxFrameID=None):
        interpolatedDF = self.__generateIntepolatedDF(minFrameID, maxFrameID)
        filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
        interpolatedDF.to_csv(filepath, sep='\t', index=False)

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
        df[self.__COLNAME_angle] = numpy.arctan(yLength_df / xLength_df) / math.pi * 90

    def __interpolate_values(self, df):
        df = df.interpolate(limit_direction='both')
        df.loc[pd.isna(df["origin_dot1"]), ["origin_dot1"]] = "interpolate"
        df.loc[pd.isna(df["origin_dot2"]), ["origin_dot2"]] = "interpolate"
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
        not_manual = (df["origin_dot1"] != "manual") & (df["origin_dot2"] != "manual")
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
        dataRedDot1 = self.combinedOnlyRedDot1()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y, "origin"]]
        dataRedDot2 = self.combinedOnlyRedDot2()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y, "origin"]]

        dfToPlot = pd.merge(dataRedDot1, dataRedDot2, on='frameNumber', how='outer', suffixes=('_dot1', '_dot2'))

        return dfToPlot.sort_values(by=['frameNumber'])

    def combinedDF(self):
        # type: () -> pd.DataFrame
        redDotsManual = RedDotsManualData(self.__folderStruct)
        redDotsRawData = RedDotsRawData.createFromCSVFile(self.__folderStruct)
        return redDotsManual.combinedDF(redDotsRawData)

    def combinedOnlyRedDot2(self):
        # type: () -> pd
        dataRedDot2 = self.combinedDF().loc[self.combinedDF()['dotName'] == self.__VALUE_redDot2]
        return dataRedDot2

    def combinedOnlyRedDot1(self):
        # type: () -> pd
        dataRedDot1 = self.combinedDF().loc[self.combinedDF()['dotName'] == self.__VALUE_redDot1]
        return dataRedDot1

    def getMiddleOfBiggestGap(self):
        # type: () -> int

        redDots1 = self.combinedOnlyRedDot1().reset_index()
        redDots2 = self.combinedOnlyRedDot2().reset_index()

        num_of_red_dots1 = len(redDots1.index)
        num_of_red_dots2 = len(redDots2.index)
        if num_of_red_dots1 <1 or num_of_red_dots2 <1:
            return self.combinedDF()[self.__COLNAME_frameNumber].min()

        if num_of_red_dots1 <2 or num_of_red_dots2 <2:
            return self.combinedDF()[self.__COLNAME_frameNumber].max()

        idxOfMaxGap1 = self.__indexOfBiggestGap(redDots1)
        gapStartFrameID1 = redDots1.loc[idxOfMaxGap1, :][self.__COLNAME_frameNumber]
        gapEndFrameID1 = redDots1.loc[idxOfMaxGap1 + 1, :][self.__COLNAME_frameNumber]
        gapSize1 = gapEndFrameID1 - gapStartFrameID1

        idxOfMaxGap2 = self.__indexOfBiggestGap(redDots2)
        gapStartFrameID2 = redDots2.loc[idxOfMaxGap2, :][self.__COLNAME_frameNumber]
        gapEndFrameID2 = redDots2.loc[idxOfMaxGap2 + 1, :][self.__COLNAME_frameNumber]
        gapSize2 = gapEndFrameID2 - gapStartFrameID2

        if gapSize2 > gapSize1:
            gapMiddleFrameID = gapEndFrameID2 - int(gapSize2/ 2)
        else:
            gapMiddleFrameID = gapEndFrameID1 - int(gapSize1/ 2)

        print ("next gapMiddleFrameID", gapMiddleFrameID, "gap1", gapSize1, "gap2", gapSize2, "gapStartFrameID1", gapStartFrameID1, "gapStartFrameID2", gapStartFrameID2, idxOfMaxGap1, idxOfMaxGap2)

        return gapMiddleFrameID

    def __indexOfBiggestGap(self, newDF):
        # type: (pd.DataFrame) -> int
        df = newDF.copy()

        df["nextFrameID"] = df["frameNumber"].shift(periods=-1)
        df["gap"] = df["nextFrameID"] - df["frameNumber"]
        maxGap = df["gap"].max()
        idxOfMaxGap = df.loc[df['gap'] == maxGap][:1].index[0]

        return idxOfMaxGap