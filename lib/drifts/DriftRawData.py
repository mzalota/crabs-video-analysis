import numpy
import pandas as pd
#import statistics as statistics

from lib.FolderStructure import FolderStructure
from lib.data.GraphPlotter import GraphPlotter
from lib.drifts.DriftManualData import DriftManualData

from lib.data.PandasWrapper import PandasWrapper


class DriftRawData(PandasWrapper):
    #__df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> DriftRawData
        self.__folderStruct = folderStruct
        filepath = folderStruct.getRawDriftsFilepath()
        self.__df = PandasWrapper.readDataFrameFromCSV(filepath)

    def getPandasDF(self):
        # type: () -> pd
        return self.__df

    def getCount(self):
        # type: () -> int
        return len(self.__df.index)

    def compensate_for_zoom(self, redDotsData):
        # type: (RedDotsData) -> void
        factor = redDotsData.scalingFactorColumn()

        # toDo sum previous driftsDetectionStep values to come up with more correct scaling factor and not hard coding 3.
        prev = factor["scaling_factor"].shift(periods=-1)
        prev_prev = factor["scaling_factor"].shift(periods=-2)
        factor["scaling_factor3"] =factor["scaling_factor"]+prev+prev_prev

        # just for debugging
        self.__plot_scaling_factor(factor)

        df = self.__df.copy()
        df = pd.merge(df, factor, on='frameNumber', how='left', suffixes=('_draft', '_reddot'))

        for i in range(0, 9):
            self.__generate_new_drift(df, df, i)

        yColumns_orig = ["fm_0_drift_y", "fm_1_drift_y", "fm_2_drift_y", "fm_3_drift_y", "fm_4_drift_y", "fm_5_drift_y",
                         "fm_6_drift_y", "fm_7_drift_y", "fm_8_drift_y"]
        yColumns_new = ["fm_0_drift_y_new", "fm_1_drift_y_new", "fm_2_drift_y_new", "fm_3_drift_y_new", "fm_4_drift_y_new", "fm_5_drift_y_new",
                    "fm_6_drift_y_new", "fm_7_drift_y_new", "fm_8_drift_y_new"]

        df['average_new'] = df[yColumns_new].mean(axis=1)
        df['average_orig'] = df[yColumns_orig].mean(axis=1)
        df['median_new'] = df[yColumns_new].median(axis=1)
        df['median_orig'] = df[yColumns_orig].median(axis=1)

        df.to_csv(self.__folderStruct.getGraphRedDotsAngle() + "merged.csv", sep='\t', index=False)

        self.__plot_graphs_for_debugging(df, yColumns_new, yColumns_orig)

        return df

    def __plot_graphs_for_debugging(self, df, yColumns_new, yColumns_orig):
        graphTitle = self.__folderStruct.getVideoFilename() + "_Maxim_ScalingFactor_orig"
        xColumns = ["frameNumber"]
        graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
        graphPlotter.saveGraphToFile(xColumns, yColumns_orig, graphTitle,
                                     self.__folderStruct.getGraphRedDotsDistance() + "_drift_orig.png")
        graphTitle = self.__folderStruct.getVideoFilename() + "_Maxim_ScalingFactor_new"
        xColumns = ["frameNumber"]
        graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
        graphPlotter.saveGraphToFile(xColumns, yColumns_new, graphTitle,
                                     self.__folderStruct.getGraphRedDotsDistance() + "_drift_new.png")
        graphTitle = self.__folderStruct.getVideoFilename() + "_Maxim_averages"
        xColumns = ["frameNumber"]
        graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
        graphPlotter.saveGraphToFile(xColumns, ["average_new", "average_orig", "median_new", "median_orig"], graphTitle,
                                     self.__folderStruct.getGraphRedDotsDistance() + "_drift_compare_avg.png")

    def __plot_scaling_factor(self, factor):
        filePath = self.__folderStruct.getGraphRedDotsAngle() + "_scalingFactor.png"
        graphTitle = self.__folderStruct.getVideoFilename() + "_Maxim_ScalingFactor_1"
        xColumns = ["frameNumber"]
        yColumns = ["scaling_factor", "scaling_factor3"]
        factor.to_csv(self.__folderStruct.getGraphRedDotsAngle() + "aaa.csv", sep='\t', index=False)
        graphPlotter = GraphPlotter(factor)
        graphPlotter.saveGraphToFile(xColumns, yColumns, graphTitle, filePath)

    def __generate_new_drift(self, df, dfToPlot, num):
        num = str(num)
        df["compensation"] = (df["fm_" + num + "_bottom_y"] - 1024) * df["scaling_factor3"]
        df["fm_" + num + "_drift_y_new"] = df["fm_" + num + "_drift_y"] + df["compensation"]

        # set to NaN values where FeatureMatcher was reset (value in Result column = FAILED
        df.loc[df['fm_' + num + '_result'] == "FAILED", ['fm_' + num + '_drift_y', 'fm_' + num + '_drift_y_new']] = numpy.nan

    def interpolate(self, manualDrifts, redDotsData, driftsDetectionStep):
        # type: (DriftManualData, int) -> pd.DataFrame
        df = self.__df.copy()

        #comment out next 3 lines to skip new logic
        df_comp = self.compensate_for_zoom(redDotsData)
        df = pd.merge(df, df_comp[['average_new', "frameNumber"]], on='frameNumber', how='left', suffixes=('_draft', '_reddot'))
        df["driftY"] = df['average_new']

        df = self._replaceInvalidValuesWithNaN(df, driftsDetectionStep)

        #TODO: dividiing drift by driftsDetectionStep is not flexible.
        # What if detectDrift step is not 2, but 3 or if it is mixed?
        df["driftX"] = df["driftX"] / driftsDetectionStep
        df["driftY"] = df["driftY"] / driftsDetectionStep
        df["average_new"] = df["average_new"] / driftsDetectionStep

        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY, 'average_new']] #, 'average_new'
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