import numpy
import pandas as pd

# import statistics as statistics
from lib.Camera import Camera
from lib.FolderStructure import FolderStructure
from lib.data.GraphPlotter import GraphPlotter
from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsData import RedDotsData
from lib.drifts.DriftManualData import DriftManualData
from lib.infra.Configurations import Configurations


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

        configs = Configurations(folderStruct)
        self.__generate_debug_graphs = configs.is_debug()

        print(" value of var is XXXXX __generate_debug_graphs", self.__generate_debug_graphs)

    def getPandasDF(self):
        # type: () -> pd
        return self.__df

    def getCount(self):
        # type: () -> int
        return len(self.__df.index)

    def _compensate_for_zoom(self, redDotsData, factor):
        # type: (RedDotsData, pd.DataFrame) -> void

        df = self.__df.copy()
        df = pd.merge(df, factor, on='frameNumber', how='left', suffixes=('_draft', '_reddot'))

        for feature_matcher_idx in range(0, 9):
            self.__generate_new_drift(df, feature_matcher_idx)

        yColumns_new = list()
        yColumns_orig = list()
        xColumns_new = list()
        xColumns_orig = list()
        for feature_matcher_idx in range(0, 9):
            column_name_y_new = "fm_"+str(feature_matcher_idx)+"_drift_y_new"
            yColumns_new.append(column_name_y_new)
            df = self.__clear_out_outliers(df, column_name_y_new)

            column_name_y_orig = "fm_" + str(feature_matcher_idx) + "_drift_y"
            yColumns_orig.append(column_name_y_orig)
            df = self.__clear_out_outliers(df, column_name_y_orig)

            column_name_x_new = "fm_" + str(feature_matcher_idx) + "_drift_x_new"
            xColumns_new.append(column_name_x_new)
            df = self.__clear_out_outliers(df, column_name_x_new)

            column_name_x_orig = "fm_" + str(feature_matcher_idx) + "_drift_x"
            xColumns_orig.append(column_name_x_orig)
            df = self.__clear_out_outliers(df, column_name_x_orig)

        df = df.interpolate(limit_direction='both')

        df['average_new'] = df[yColumns_new].mean(axis=1)
        df['average_orig'] = df[yColumns_orig].mean(axis=1)
        df['median_new'] = df[yColumns_new].median(axis=1)
        df['median_orig'] = df[yColumns_orig].median(axis=1)

        df['average_x_new'] = df[xColumns_new].mean(axis=1)
        df['average_x_orig'] = df[xColumns_orig].mean(axis=1)
        df['median_x_new'] = df[xColumns_new].median(axis=1)
        df['median_x_orig'] = df[xColumns_orig].median(axis=1)

        if self.__generate_debug_graphs:
            self.__plot_scaling_factor(factor)

            filepath_prefix=self.__folderStruct.getSubDirpath() + "graph_"

            graphTitle = self.__folderStruct.getVideoFilename() + "_averages_y"
            xColumns = ["frameNumber"]
            graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
            graphPlotter.saveGraphToFile(xColumns, ["average_new", "average_orig", "median_new", "median_orig"], graphTitle,
                                         filepath_prefix + "drift_compare_avg_y.png")

            graphTitle = self.__folderStruct.getVideoFilename() + "_averages_x"
            xColumns = ["frameNumber"]
            graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
            graphPlotter.saveGraphToFile(xColumns, ["average_x_new", "average_x_orig", "median_x_new", "median_x_orig"], graphTitle,
                                         filepath_prefix + "drift_compare_avg_x.png")

            graphTitle = self.__folderStruct.getVideoFilename() + "_averages_x_new"
            xColumns = ["frameNumber"]
            graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
            graphPlotter.saveGraphToFile(xColumns, ["average_x_new"], graphTitle,
                                         filepath_prefix + "drift_compare_avg_x_new.png")


            graphTitle = self.__folderStruct.getVideoFilename() + "_averages_x_orig"
            xColumns = ["frameNumber"]
            graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
            graphPlotter.saveGraphToFile(xColumns, ["average_x_orig"], graphTitle,
                                         filepath_prefix + "drift_compare_avg_x_orig.png")

            graphTitle = self.__folderStruct.getVideoFilename() + "_median_x_new"
            xColumns = ["frameNumber"]
            graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
            graphPlotter.saveGraphToFile(xColumns, [ "median_x_new", "average_x_new"], graphTitle,
                                         filepath_prefix + "drift_compare_median_x_new.png")


            graphTitle = self.__folderStruct.getVideoFilename() + "_median_x_orig"
            xColumns = ["frameNumber"]
            graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 1000) & (df['frameNumber'] < 3000)])
            graphPlotter.saveGraphToFile(xColumns, [ "median_x_orig", "average_x_orig"], graphTitle,
                                         filepath_prefix + "drift_compare_median_x_orig.png")

            #df.to_csv(self.__folderStruct.getGraphRedDotsAngle() + "merged.csv", sep='\t', index=False)

            self.__plot_graphs_for_debugging(df, xColumns_new, xColumns_orig)

        return df

    def __clear_out_outliers(self, df, column_name, quantile : float = 0.99):
        outlier_up_value = df[column_name].quantile(quantile)
        # print("column " + column_name +", 99th quantile: " + str(outlier_up_value))
        df.loc[df[column_name] > outlier_up_value, [column_name]] = numpy.nan

        outlier_down_value = df[column_name].quantile(1- quantile)
        # print("column " + column_name +", 01th quantile: " + str(outlier_down_value))
        df.loc[df[column_name] < outlier_down_value, [column_name]] = numpy.nan
        return df

    def __plot_graphs_for_debugging(self, df, yColumns_new, yColumns_orig):
        x_axis_column = ["frameNumber"]
        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_"

        graphTitle = self.__folderStruct.getVideoFilename() + "_FrameMatcher_Drifts_orig"
        graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 2000) & (df['frameNumber'] < 3000)])
        graphPlotter.saveGraphToFile(x_axis_column, yColumns_orig, graphTitle, filepath_prefix + "drift_orig.png")

        graphTitle = self.__folderStruct.getVideoFilename() + "__FrameMatcher_Drifts_new"
        graphPlotter = GraphPlotter(df.loc[(df['frameNumber'] > 2000) & (df['frameNumber'] < 3000)])
        graphPlotter.saveGraphToFile(x_axis_column, yColumns_new, graphTitle, filepath_prefix + "drift_new.png")

    def __plot_scaling_factor(self, factor):
        filePath = self.__folderStruct.getSubDirpath() + "graph_scalingFactor.png"
        graphTitle = self.__folderStruct.getVideoFilename() + "_ScalingFactor_1"
        xColumns = ["frameNumber"]
        yColumns = ["scaling_factor"]
        #factor.to_csv(self.__folderStruct.getGraphRedDotsAngle() + "aaa.csv", sep='\t', index=False)
        graphPlotter = GraphPlotter(factor)
        graphPlotter.saveGraphToFile(xColumns, yColumns, graphTitle, filePath)

    def __generate_new_drift(self, df, num):
        num = str(num)

        column_name_y_bottom = "fm_" + num + "_bottom_y"
        column_name_y_orig = "fm_" + num + "_drift_y"
        column_name_y_new = "fm_" + num + "_drift_y_new"

        camera = Camera.create()

        df["compensation"] = (df[column_name_y_bottom] - int(camera.frame_height() /2)) * df["scaling_factor"]
        df[column_name_y_new] = df[column_name_y_orig] + df["compensation"]

        # set to NaN values where FeatureMatcher was reset (value in Result column = FAILED
        df.loc[df['fm_' + num + '_result'] == "FAILED", ['fm_' + num + '_drift_y', 'fm_' + num + '_drift_y_new']] = numpy.nan

        #X drifts
        column_name_x_bottom = "fm_" + num + "_bottom_x"
        column_name_x_bottom = "fm_" + num + "_bottom_y"
        column_name_x_orig = "fm_" + num + "_drift_x"
        column_name_x_new = "fm_" + num + "_drift_x_new"

        df["compensation"] = (df[column_name_x_bottom] - int(camera.frame_width()/2)) * df["scaling_factor"]
        df[column_name_x_new] = df[column_name_x_orig] + df["compensation"]

        # set to NaN values where FeatureMatcher was reset (value in Result column = FAILED
        df.loc[df['fm_' + num + '_result'] == "FAILED", [column_name_y_orig, column_name_y_new, column_name_x_orig, column_name_x_new]] = numpy.nan

    def interpolate(self, manualDrifts: DriftManualData, redDotsData: RedDotsData, driftsDetectionStep: int) -> pd.DataFrame:
        df = self.__df.copy()

        #comment out next 5 lines to skip new logic of compensating each FeatureMatcher
        factor = redDotsData.scalingFactorColumn(driftsDetectionStep)

        df_comp = self._compensate_for_zoom(redDotsData, factor)
        df = pd.merge(df, df_comp[['average_new', "average_x_new", "frameNumber"]], on='frameNumber', how='left', suffixes=('_draft', '_reddot'))
        df["driftY"] = df['average_new']
        df["driftX"] = df['average_x_new']


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