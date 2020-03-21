import math

import pandas as pd
import numpy

from lib.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper
from lib.common import Point
from lib.data.RedDotsManualData import RedDotsManualData

class RedDotsData(PandasWrapper):
    #__rawDF = None
    #__manualDF = None
    #__interpolatedDF = None

    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_mm_per_pixel = "mm_per_pixel"
    __COLNAME_angle = "angle"

    __distance_between_reddots_mm = 300

    def __init__(self, folderStruct):
        self.__folderStruct = folderStruct

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> RedDotsData
        newObj = RedDotsData(folderStruct)
        return newObj

    def getPandasDF(self):
        # type: () -> pd

        try:
            return self.__interpolatedDF
        except AttributeError:
            # attribute self.__interpolatedDF have not been initialized yet
            filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
            self.__interpolatedDF = self.readDataFrameFromCSV(filepath)
            return self.__interpolatedDF

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
        redDotsManual = RedDotsManualData(self.__folderStruct)

        df = self.__add_rows_for_every_frame(redDotsManual, minVal, maxVal)
        df = self.__interpolate_values(df)
        self.__calculateDerivedValues(df)

        self.__clearOutlierRows(df, self.__COLNAME_angle)
        df = self.__interpolate_values(df)
        self.__calculateDerivedValues(df)

        self.__clearOutlierRows(df, 'distance')
        df = self.__interpolate_values(df)
        self.__calculateDerivedValues(df)
        return df

    def __add_rows_for_every_frame(self, redDotsManual, minVal, maxVal):
        df = redDotsManual.forPlotting()
        df = df.set_index("frameNumber")
        everyFrame = pd.DataFrame(numpy.arange(start=minVal, stop=maxVal, step=1), columns=["frameNumber"]).set_index(
            "frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        return df

    def __calculateDerivedValues(self, df):
        df['distance'] = pow(pow(df["centerPoint_x_dot2"] - df["centerPoint_x_dot1"], 2) + pow(df["centerPoint_y_dot2"] - df["centerPoint_y_dot1"], 2), 0.5) #.astype(int)
        df[self.__COLNAME_mm_per_pixel] = self.__distance_between_reddots_mm / df['distance']

        yLength_df = (df["centerPoint_y_dot1"] - df["centerPoint_y_dot2"])
        xLength_df = (df["centerPoint_x_dot1"] - df["centerPoint_x_dot2"])
        df[self.__COLNAME_angle] = numpy.arctan(yLength_df / xLength_df) / math.pi * 90

    def __interpolate_values(self, df):
        df = df.interpolate(limit_direction='both')
        df.loc[pd.isna(df["origin_dot1"]), ["origin_dot1"]] = "interpolate"
        df.loc[pd.isna(df["origin_dot2"]), ["origin_dot2"]] = "interpolate"
        return df

    def __clearOutlierRows(self, df, column_with_outliers):
        upper_99 = numpy.percentile(df[column_with_outliers], 99)
        lower_1 = numpy.percentile(df[column_with_outliers], 1)

        upper_95 = numpy.percentile(df[column_with_outliers], 95)
        lower_5 = numpy.percentile(df[column_with_outliers], 5)

        upper_bound = upper_95 + (upper_95-lower_5)/4
        lower_bound = lower_5 - (upper_95-lower_5)/4

        print("outlier column", column_with_outliers, "Upper bound", upper_bound, "angle lower bound", lower_bound, "95th percentile", upper_95, "5th percentile", lower_5, "99th percentile", upper_99, "1st percentile", lower_1)

        # clear the values in rows where value of the angle is off bounds
        columns_with_wrong_values = ["centerPoint_x_dot1", "centerPoint_x_dot2", "centerPoint_y_dot1", "centerPoint_y_dot2", "angle", "distance", "mm_per_pixel"]

        not_manual = (df["origin_dot1"] != "manual") & (df["origin_dot2"] != "manual")
        outlier_rows = ((df[column_with_outliers] < lower_bound) | (df[column_with_outliers] > upper_bound)) & not_manual
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
