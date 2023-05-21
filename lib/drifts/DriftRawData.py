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
from lib.infra.DataframeWrapper import DataframeWrapper


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

    def __save_graphs_drifts_raw(self, df_param, frame_id_from: int, fream_id_to: int = 123456):

        df = df_param.copy()

        xColumns_orig = list()
        yColumns_orig = list()
        for num in range(0, 9):
            column_drift_y = "fm_" + str(num) + "_drift_y"
            column_drift_x = "fm_" + str(num) + "_drift_x"
            yColumns_orig.append(column_drift_y)
            xColumns_orig.append(column_drift_x)

            column_result = 'fm_' + str(num) + '_result'
            df.loc[df[column_result] == "FAILED", [column_drift_y, column_drift_x, "driftX", "driftY"]] = numpy.nan


        dframe = DataframeWrapper(df)
        for col_name in yColumns_orig:
            dframe.remove_outliers_quantile(col_name)

        for col_name in xColumns_orig:
            dframe.remove_outliers_quantile(col_name)

        dframe.remove_outliers_quantile("driftX")
        dframe.remove_outliers_quantile("driftY")

        df = dframe.pandas_df()

        #after removing values in rows with result="FAILED", now fill them out with interpolated values
        df = df.interpolate(limit_direction='both')

        df['average_y_orig'] = df[yColumns_orig].mean(axis=1)
        df['average_x_orig'] = df[xColumns_orig].mean(axis=1)

        # --- now Plot graphs and save them to PNG files
        x_axis_column = ["frameNumber"]
        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"
        title_prefix = self.__folderStruct.getVideoFilename()

        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        graph_title = title_prefix + "_FrameMatcher_Drifts_X_raw"
        graph_plotter = GraphPlotter(df_to_plot)
        graph_plotter.saveGraphToFile(x_axis_column, xColumns_orig, graph_title, filepath_prefix + "drift_x_raw.png")

        graph_title = title_prefix + "_FrameMatcher_Drifts_Y_raw"
        graph_plotter = GraphPlotter(df_to_plot)
        graph_plotter.saveGraphToFile(x_axis_column, yColumns_orig, graph_title, filepath_prefix + "drift_y_raw.png")

        graph_title = title_prefix + "_median_drifts_x_y"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(x_axis_column, ["driftY", "driftX", "average_y_orig", "average_x_orig"], graph_title,
                                     filepath_prefix + "drifts_px_raw.png")

        return df

    def __save_graphs_drifts_zoom_compensated(self, df, frame_id_from: int, fream_id_to: int = 123456):

        yColumns_new = list()
        xColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            column_name_y_new = "fm_"+str(feature_matcher_idx)+"_drift_y_new"
            column_name_x_new = "fm_" + str(feature_matcher_idx) + "_drift_x_new"
            yColumns_new.append(column_name_y_new)
            xColumns_new.append(column_name_x_new)

        #get rid of outliers in dr
        dframe = DataframeWrapper(df)
        dframe.remove_outliers_quantile("driftX")
        dframe.remove_outliers_quantile("driftY")
        df = dframe.pandas_df()
        df = df.interpolate(limit_direction='both')

        x_axis_column = ["frameNumber"]
        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"
        title_prefix = self.__folderStruct.getVideoFilename()

        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        graph_title = title_prefix + "_averages_y"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(x_axis_column, ["average_y_new", "driftY"], graph_title,
                                     filepath_prefix + "drift_compare_avg_y.png")

        graph_title = title_prefix + "_averages_x"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(x_axis_column, ["average_x_new", "driftX"], graph_title,
                                     filepath_prefix + "drift_compare_avg_x.png")

        graph_title = title_prefix + "__FrameMatcher_Drifts_new"
        graph_plotter = GraphPlotter(df_to_plot)
        graph_plotter.saveGraphToFile(x_axis_column, xColumns_new, graph_title, filepath_prefix + "drift_new.png")



    def _compensate_for_zoom(self, zoom_factor: pd.DataFrame) -> pd.DataFrame:

        df = self.__df.copy()
        df = pd.merge(df, zoom_factor, on='frameNumber', how='left', suffixes=('_draft', '_reddot'))

        factor = df["scaling_factor"]  # scaling_factor scaling_factor_undistorted
        yColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            column_name_y_raw = "fm_" + num + "_drift_y"

            df.loc[df['fm_' + num + '_result'] == "FAILED", [column_name_y_raw]] = numpy.nan

            drift_y_dezoomed = self.__drift_y_dezoomed(df, num, factor)

            column_name_y_new = ("fm_" + num + "_drift_y_new")
            yColumns_new.append(column_name_y_new)
            df[column_name_y_new] = drift_y_dezoomed



        for feature_matcher_idx in range(0, 9):
            self.__compensate_drift_for_zoom_x(df, feature_matcher_idx)


        xColumns_new = list()
        for feature_matcher_idx in range(0, 9):
            column_name_x_new = "fm_" + str(feature_matcher_idx) + "_drift_x_new"
            xColumns_new.append(column_name_x_new)


        dframe = DataframeWrapper(df)
        for col_name in yColumns_new:
            dframe.remove_outliers_quantile(col_name)

        for col_name in xColumns_new:
            dframe.remove_outliers_quantile(col_name)

        df = dframe.pandas_df()
        df = df.interpolate(limit_direction='both')

        df['average_y_new'] = df[yColumns_new].mean(axis=1)
        df['average_x_new'] = df[xColumns_new].mean(axis=1)

        return df

    # def __compensate_drift_for_zoom_y(self, df, num):
    #     num = str(num)
    #
    #     # Y drifts
    #     column_name_y_raw = "fm_" + num + "_drift_y"
    #     df.loc[df['fm_' + num + '_result'] == "FAILED", [column_name_y_raw]] = numpy.nan
    #     column_name_y_drift_de_zoomed = "fm_" + num + "_drift_y_new"
    #     zoom_factor = df["scaling_factor"] # scaling_factor scaling_factor_undistorted
    #
    #     drift_y_dezoomed = self.__drift_y_dezoomed(df, num, zoom_factor)
    #
    #     df[column_name_y_drift_de_zoomed] = drift_y_dezoomed
    #
    #     # set to NaN values where FeatureMatcher was reset (value in Result column = FAILED)
    #     return df[column_name_y_drift_de_zoomed]

    def __drift_y_dezoomed(self, df, num, zoom_factor):
        center_y = self.__fm_center_y(df, num)
        column_name_y_raw = "fm_" + num + "_drift_y"
        camera = Camera.create()
        drift_y_due_to_zoom = (center_y - camera.frame_height() / 2) * zoom_factor
        drift_y_dezoomed = df[column_name_y_raw] + drift_y_due_to_zoom
        return drift_y_dezoomed

    def __fm_center_y(self, df: pd.DataFrame, num: str) -> pd.DataFrame:
        y_coord_top = df[("fm_" + str(num) + "_top_y")]
        y_coord_bottom = df[("fm_" + str(num) + "_bottom_y")]
        y_coord_center = y_coord_top + (y_coord_bottom - y_coord_top) / 2
        return y_coord_center

    def __compensate_drift_for_zoom_x(self, df, num):
        num = str(num)
        camera = Camera.create()
        frame_center_x_coord = camera.frame_width() / 2

        # X drifts
        column_name_x_top = "fm_" + num + "_top_x"
        column_name_x_bottom = "fm_" + num + "_bottom_x"
        column_name_x_drift_raw = "fm_" + num + "_drift_x"
        column_name_x_drift_de_zoomed = "fm_" + num + "_drift_x_new"

        fm_center_x_coord = df[column_name_x_top] + (df[column_name_x_bottom] - df[column_name_x_top]) / 2
        fm_distance_to_image_center = (fm_center_x_coord - frame_center_x_coord)

        #If the seefloor does not move at all, but there is only zoom in/out than the FrameMatcher will register X-drift equal to "drift_due_to_zoom"
        drift_due_to_zoom = fm_distance_to_image_center * df["scaling_factor"] #scaling_factor scaling_factor_undistorted

        df[column_name_x_drift_de_zoomed] = df[column_name_x_drift_raw] + drift_due_to_zoom

        # set to NaN values where FeatureMatcher was reset (value in Result column = FAILED)
        df.loc[df['fm_' + num + '_result'] == "FAILED", [column_name_x_drift_raw, column_name_x_drift_de_zoomed]] = numpy.nan


    def interpolate(self, manualDrifts: DriftManualData, redDotsData: RedDotsData, driftsDetectionStep: int) -> pd.DataFrame:
        df = self.__df.copy()

        #comment out next 5 lines to skip new logic of compensating each FeatureMatcher
        zoom_factor = redDotsData.scalingFactorColumn(driftsDetectionStep)


        #zoom_factor = redDotsData.scalingFactorColumn_undiestoreted(driftsDetectionStep)

        df_comp = self._compensate_for_zoom(zoom_factor)

        if self.__generate_debug_graphs:
            self.__save_graphs_drifts_raw(self.__df, 20400, 21000)
            self.__save_graphs_drifts_zoom_compensated(df_comp, 20400, 21000)
            redDotsData._save_graph_zoom_factor(driftsDetectionStep, 20400, 21000)

        df = pd.merge(df, df_comp[['average_y_new', "average_x_new", "frameNumber"]], on='frameNumber', how='left', suffixes=('_draft', '_reddot'))
        df["driftY"] = df['average_y_new']
        df["driftX"] = df['average_x_new']

        df = self._replaceInvalidValuesWithNaN(df, driftsDetectionStep)

        #TODO: dividiing drift by driftsDetectionStep is not flexible.
        # What if detectDrift step is not 2, but 3 or if it is mixed?
        df["driftX"] = df["driftX"] / driftsDetectionStep
        df["driftY"] = df["driftY"] / driftsDetectionStep

        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY]]
        df = df.interpolate(limit_direction='both')

        df = self.__replace_with_NaN_if_very_diff_to_neighbors(df, "driftY", driftsDetectionStep)
        df = self.__interpolateToHaveEveryFrame(df)

        # since drifts were created using undistorted image, we need to increase drifts for raw/distored images
        camera = Camera.create()
        distortion_coeff = camera.distortion_at_center()
        df["driftX"] = df["driftX"] / distortion_coeff
        df["driftY"] = df["driftY"] / distortion_coeff

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