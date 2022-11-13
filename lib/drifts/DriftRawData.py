import numpy
import pandas as pd
#import statistics as statistics

from lib.FolderStructure import FolderStructure
from lib.data.DriftManualData import DriftManualData

from lib.data.PandasWrapper import PandasWrapper


class DriftRawData(PandasWrapper):
    #__df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> DriftRawData
        filepath = folderStruct.getRawDriftsFilepath()
        self.__df = PandasWrapper.readDataFrameFromCSV(filepath)

    def getPandasDF(self):
        # type: () -> pd
        return self.__df

    def getCount(self):
        # type: () -> int
        return len(self.__df.index)

    def interpolate(self, manualDrifts, driftsDetectionStep):
        # type: (DriftManualData, int) -> pd.DataFrame

        df = self._replaceInvalidValuesWithNaN(self.__df.copy(), driftsDetectionStep)

        #TODO: dividiing drift by driftsDetectionStep is not flexible.
        # What if detectDrift step is not 2, but 3 or if it is mixed?
        df["driftX"] = df["driftX"] / driftsDetectionStep
        df["driftY"] = df["driftY"] / driftsDetectionStep

        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY]]
        df = df.interpolate(limit_direction='both')

        df = self.__replace_with_NaN_if_very_diff_to_neighbors(df, "driftY", driftsDetectionStep)

        df = self.__interpolateToHaveEveryFrame(df)

        df = manualDrifts.overwrite_values(df)

        df = df.interpolate(limit_direction='both')

        #set drifts in the first row to zero.
        self.setValuesInFirstRowToZeros(df)

        return df

    def setValuesInFirstRowToZeros(self, df):
        df.loc[0, self.__COLNAME_driftX] = 0
        df.loc[0, self.__COLNAME_driftY] = 0

    def _replaceInvalidValuesWithNaN(self, df, step_size):
        # type: (pd.DataFrame) -> pd.DataFrame
        df.loc[df['driftY'] == -999, ['driftY', 'driftX']] = numpy.nan
        df.loc[df['driftX'] == -888, ['driftX', 'driftY']] = numpy.nan

        df.loc[df['driftX'] < -10*step_size, ['driftX', 'driftY']] = numpy.nan #-20
        df.loc[df['driftX'] > 10*step_size, ['driftX', 'driftY']] = numpy.nan  #30

        df.loc[df['driftY'] < -10*step_size, ['driftX', 'driftY']] = numpy.nan #-20
        df.loc[df['driftY'] > 100*step_size/2, ['driftX', 'driftY']] = numpy.nan  #130

        return df

    def __interpolateToHaveEveryFrame(self, df):
        # type: (pd.DataFrame) -> pd.DataFrame
        minFrameID = self.minFrameID()
        maxFrameID = self.maxFrameID()
        df = df.set_index("frameNumber")
        arrayOfFrameIDs = numpy.arange(start=minFrameID, stop=maxFrameID, step=1)
        everyFrame = pd.DataFrame(arrayOfFrameIDs, columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        return df

    def minFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].min()

    def maxFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].max()

    def __replace_with_NaN_if_very_diff_to_neighbors(self, data, colName, step_size):
        targetOfAnalysis = data[colName]
        prevPrev = targetOfAnalysis.shift(periods=2)
        nextNext = targetOfAnalysis.shift(periods=-2)
        prev = targetOfAnalysis.shift(periods=1)
        next = targetOfAnalysis.shift(periods=-1)

        newDF =  pd.concat([prevPrev, prev, targetOfAnalysis, next, nextNext], axis=1)
        median = newDF.median(axis=1)
        diff_to_median = abs(targetOfAnalysis - median)
        is_outlier = diff_to_median > (10)

        data["median"] = median
        data["diff_to_median"] = diff_to_median
        data["isOutlier"] = is_outlier
        #
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.max_rows', None)
        # pd.set_option('expand_frame_repr', False)
        # print(data.head(1300))

        # whipe out
        data.loc[is_outlier, ['driftX', 'driftY']] = numpy.nan

        return data