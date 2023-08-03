import math

import pandas as pd
import numpy

from lib.Camera import Camera
from lib.data.FourierSmoothing import FourierSmoothing
from lib.infra.Configurations import Configurations
from lib.FolderStructure import FolderStructure
from lib.VideoStream import VideoStream
from lib.data.GraphPlotter import GraphPlotter
from lib.data.PandasWrapper import PandasWrapper
from lib.common import Point
from lib.data.RedDotsManualData import RedDotsManualData
from lib.data.RedDotsRawData import RedDotsRawData
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.model.RedDots import RedDots


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
    __COLNAME_seconds = 'seconds'
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"
    __COLNAME_mm_per_pixel = "mm_per_pixel"
    __COLNAME_angle = "angle"
    __COLNAME_distance = "distance"

    def __init__(self, folderStruct, redDotsManual):
        # type: (FolderStructure, RedDotsManualData) -> RedDotsData
        self.__folderStruct = folderStruct
        self.__redDotsManual = redDotsManual
        self.__df_as_dict = None

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
            #TODO: Interpolation does not work for early frames where video was bad. It still shows steps of 5

            # attribute self.__interpolatedDF have not been initialized yet
            print("RedDotsData in getPandasDF. creating __interpolatedDF")
            filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
            print("getRedDotsInterpolatedFilepath: "+filepath)
            if self.__folderStruct.fileExists(filepath):
                self.__interpolatedDF = self.readDataFrameFromCSV(filepath)
            else:
                self.__interpolatedDF = PandasWrapper.empty_df()
            return self.__interpolatedDF

    def scalingFactorColumn(self, driftsDetectionStep: int = 1) -> pd.DataFrame:
        df = self.getPandasDF()

        df['distance_smooth'] = self.__smooth_distance_value(df, self.__COLNAME_distance)
        result = self.__calculate_scaling_factor(df["distance_smooth"], driftsDetectionStep)
        df["scaling_factor"] = result

        if Configurations(self.__folderStruct).is_debug():
            result = self.__calculate_scaling_factor(df[self.__COLNAME_distance], driftsDetectionStep)
            # result = self.__calculate_scaling_factor(df["distance_px_undistort"], driftsDetectionStep)
            df["scaling_factor_not_smooth"] = result
            self._save_graph_zoom_factor(df, ["scaling_factor", "scaling_factor_not_smooth"], 3000,4000)

        return df[[self.COLNAME_frameNumber, "scaling_factor"]]

    def __calculate_scaling_factor(self, column, driftsDetectionStep):
        dist_diff = column - column.shift(periods=-1)
        scaling_factor_single_step = dist_diff / column
        result = scaling_factor_single_step + 0
        for increment in range(1, driftsDetectionStep):
            prev = scaling_factor_single_step.shift(periods=-increment)
            result = result + prev
        return result

    def __smooth_distance_value(self, df, distance_column_name):

        distance_column = df[distance_column_name]
        shifted1 = FourierSmoothing().smooth_curve(distance_column, "distance_raw", 1)
        shifted2 = FourierSmoothing().smooth_curve(distance_column, "distance_raw", 0.4)
        shifted3 = FourierSmoothing().smooth_curve(distance_column, "distance_raw", 0.7)

        newDF =  df[["frameNumber", distance_column_name]].copy()
        newDF['distance_shift1'] = shifted1
        newDF['distance_shift2'] = shifted2
        newDF['distance_shift3'] = shifted3

        if Configurations(self.__folderStruct).is_debug():
            columns_y = [distance_column_name, "distance_shift1", "distance_shift2", "distance_shift3"]
            self.__save_graphs_smooth_distance(newDF, distance_column_name, columns_y, 2000, 3000)

        #TODO: Access which smoothing setting (which value of lowband pass: 1.0, 0.7 or 0.4 or other) is best by looking at variance of fm_N_drift_x_new

        return shifted2


    def __save_graphs_smooth_distance(self, df, distance_column_name, columns_y, frame_id_from: int = 0, fream_id_to: int = 123456):
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"+distance_column_name+"_"
        title_prefix = self.__folderStruct.getVideoFilename()

        graph_title = title_prefix + "_Distance_Fourier_"+distance_column_name
        GraphPlotter(df_to_plot).saveGraphToFile(["frameNumber"], columns_y, graph_title, filepath_prefix+"fourier.png")

    def _save_graph_zoom_factor(self, df, columns_y, frame_id_from: int = 0, fream_id_to: int = 123456):

        x_axis_column = ["frameNumber"]
        filepath_prefix = self.__folderStruct.getSubDirpath() + "graph_debug_"
        title_prefix = self.__folderStruct.getVideoFilename()

        graph_title = title_prefix + "_scaling_factor"
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < fream_id_to)]

        plotter = GraphPlotter(df_to_plot)
        plotter.saveGraphToFile(x_axis_column, columns_y, graph_title,
                                filepath_prefix + "zoom_factor.png")

    def saveGraphs(self, frame_id_from: int = 0, frame_id_to: int = 123456):
        df = self.getPandasDF()
        df_to_plot = df.loc[(df['frameNumber'] > frame_id_from) & (df['frameNumber'] < frame_id_to)]
        xColumns = [self.COLNAME_frameNumber, self.__COLNAME_seconds]

        filePath = self.__folderStruct.getGraphRedDotsAngle()
        graphTitle = self.__folderStruct.getVideoFilename()+ " Red Dots Angle (degrees)"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(xColumns, [self.__COLNAME_angle], graphTitle, filePath)

        filePath = self.__folderStruct.getGraphRedDotsDistance()
        graphTitle = self.__folderStruct.getVideoFilename()+ " Red Dots Distance (pixels)"
        graphPlotter = GraphPlotter(df_to_plot)
        graphPlotter.saveGraphToFile(xColumns, [self.__COLNAME_distance], graphTitle, filePath)

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

    def get_camera_height_mm(self, frame_id: int):

        red_dot1 = self.getRedDot1(frame_id)
        red_dot2 = self.getRedDot2(frame_id)
        dots = RedDots(frame_id, red_dot1, red_dot2)

        camera = Camera.create()
        depth_z_axis_to_seefloor_on_image = camera.distance_to_object(dots.distance(),
                                                                      self.red_dots_separation_mm())
        return depth_z_axis_to_seefloor_on_image

    def zoom_instantaneous(self, frame_id):
        # type: (int) -> float
        if frame_id <= self.__minFrameID():
            return 0
        return self.scalingFactor(frame_id-1, frame_id)

    def scalingFactor(self, frameIDOrigin, frameIDTarget):
        # type: (int, int) -> float
        distanceRef = self.getDistancePixels(frameIDOrigin)
        distanceToScale = self.getDistancePixels(frameIDTarget)
        scalingFactor = distanceRef / distanceToScale
        return scalingFactor


    def getMMPerPixel(self, frameId):
        # type: (int) -> float
        self.__initialize_dict()
        result = self.__df_as_dict[frameId]["mm_per_pixel"]

        #old slower way to fetch record
        # dfResult = self.__rowForFrame(frameId)
        # result2 = dfResult["mm_per_pixel"].iloc[0]
        # print("getMMPerPixel results: "+str(result)+ " _ "+str(result2))

        return result

    def __initialize_dict(self):
        if self.__df_as_dict is not None:
            return

        list_of_rows = DataframeWrapper(self.getPandasDF()).to_list()
        records_by_frame_id = dict()
        for row in list_of_rows:
            frame_id_of_row = row[self.COLNAME_frameNumber]
            records_by_frame_id[frame_id_of_row] = row

        self.__df_as_dict = records_by_frame_id

    def mm_per_pixel_undistorted(self, frameId : int) -> float:
        # type: (int) -> float
        # self.getRedDot1()
        distance_between_dots_px = self.distance_px_undistorted(frameId)
        return self.red_dots_separation_mm()/distance_between_dots_px

    def distance_px_undistorted(self, frame_id: int) -> int:
        camera = Camera.create()
        red_dot1_undistorted = camera.undistort_point(self.getRedDot1(frame_id))
        red_dot2_undistorted = camera.undistort_point(self.getRedDot2(frame_id))
        distance_between_dots_px = red_dot1_undistorted.distanceTo(red_dot2_undistorted)
        return distance_between_dots_px

    def __rowForFrame(self, frameId):
        df = self.getPandasDF()
        dfResult = df.loc[df[RedDotsData.COLNAME_frameNumber] == frameId]
        return dfResult

    def saveInterpolatedDFToFile(self, minFrameID=None, maxFrameID=None):
        interpolatedDF = self.__generateIntepolatedDF(minFrameID, maxFrameID)
        filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
        interpolatedDF.to_csv(filepath, sep='\t', index=False)
        self.__interpolatedDF = interpolatedDF
        self.__df_as_dict = None # clear the cache of the DF. it will be need to be regenerated next time

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
        df = self.__recalculate_distance_undistorted(df)
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

    def __calculateDerivedValues(self, df: pd.DataFrame):
        self.__recalculate_column_distance(df)
        self.__recalculate_column_angle(df)
        df[self.__COLNAME_seconds] = df[self.COLNAME_frameNumber]/VideoStream.FRAMES_PER_SECOND


    def __recalculate_column_distance(self, df: pd.DataFrame):
        df[self.__COLNAME_distance] = pow(pow(df["centerPoint_x_dot2"] - df["centerPoint_x_dot1"], 2) + pow(df["centerPoint_y_dot2"] - df["centerPoint_y_dot1"], 2), 0.5)  # .astype(int)
        df[self.__COLNAME_mm_per_pixel] = self.red_dots_separation_mm() / df[self.__COLNAME_distance]

    def __recalculate_distance_undistorted(self, df: pd.DataFrame):
        points = DataframeWrapper(df).as_records_dict("frameNumber")
        camera = Camera.create()
        result_dict = list()
        for frame_id in points:
            point_x_dot_1 = points[frame_id]["centerPoint_x_dot1"]
            point_y_dot_1 = points[frame_id]["centerPoint_y_dot1"]
            point_x_dot_2 = points[frame_id]["centerPoint_x_dot2"]
            point_y_dot_2 = points[frame_id]["centerPoint_y_dot2"]

            point_1 = Point(point_x_dot_1, point_y_dot_1)
            point_2 = Point(point_x_dot_2, point_y_dot_2)
            distance_raw = point_1.distanceTo(point_2)

            point_1_undistorted = camera.undistort_point(point_1)
            point_2_undistorted = camera.undistort_point(point_2)
            distance_undistorted = point_1_undistorted.distanceTo(point_2_undistorted)

            result_dict.append((frame_id, distance_undistorted, distance_raw))

        df_new_column = pd.DataFrame.from_records(result_dict,
                                                  columns=['frameNumber', 'distance_px_undistort', "distance_px"])

        df = pd.merge(df, df_new_column, on='frameNumber', how='left', suffixes=('_dot1', '_dot2'))
        return df

    def red_dots_separation_mm(self):
        configs = Configurations(self.__folderStruct)
        return configs.get_distance_between_red_dots()

    def __recalculate_column_angle(self, df):
        yLength_df = (df["centerPoint_y_dot1"] - df["centerPoint_y_dot2"])
        xLength_df = (df["centerPoint_x_dot1"] - df["centerPoint_x_dot2"])
        angle_in_radians = numpy.arctan(yLength_df / xLength_df)*(-1)
        df[self.__COLNAME_angle] = angle_in_radians / math.pi * 90

    def __interpolate_values(self, df) -> pd.DataFrame:
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
            return None, None

        frameId1, gap1 = self.__find_largest_gap('origin_dot1')
        frameId2, gap2 = self.__find_largest_gap('origin_dot2')
        print ("RedDotsData::getMiddleFrameIDOfBiggestGap", "frameId1", frameId1, "gap1", gap1,"frameId2", frameId2, "gap2", gap2)
        if gap1 > gap2:
            return frameId1, gap1
        else:
            return frameId2, gap2

    def __find_largest_gap(self, whichDot):
        # type: (str) -> (int, float)

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

