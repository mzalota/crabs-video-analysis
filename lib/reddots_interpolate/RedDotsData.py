import math

import pandas as pd
import numpy

from lib.data.FourierSmoothing import FourierSmoothing
from lib.imageProcessing.Camera import Camera
from lib.seefloor.VerticalSpeed import VerticalSpeed
from lib.infra.Configurations import Configurations
from lib.infra.FolderStructure import FolderStructure
from lib.VideoStream import VideoStream
from lib.infra.GraphPlotter import GraphPlotter
from lib.data.PandasWrapper import PandasWrapper
from lib.model.Point import Point
from lib.reddots.RedDotsManualData import RedDotsManualData
from lib.reddots.RedDotsRawData import RedDotsRawData
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

    def getPandasDF(self)->pd.DataFrame:
        try:
            return self.__interpolatedDF
        except AttributeError:
            #TODO: Interpolation does not work for early frames where video was bad. It still shows steps of 5

            video_stream = VideoStream.instance(self.__folderStruct.getVideoFilepath())
            first_frame_id = video_stream.get_id_of_first_frame(1)
            last_frame_id = video_stream.num_of_frames()
            self.saveInterpolatedDFToFile(first_frame_id, last_frame_id)
            return self.__interpolatedDF


    def verticalSpeed(self) -> VerticalSpeed:
        newDF = self.getPandasDF()[["frameNumber", self.__COLNAME_distance]].copy()

        low_band_pass_cutoff = 0.4  # 0.4  cuttoff gitter noise (high fequencies) - making curve "smooth"
        fourier = FourierSmoothing()
        fourier.saveGraphFFT(newDF["distance"], "distance", self.__folderStruct)

        smoothed_data = fourier.smooth_array(newDF["distance"].to_numpy(), low_band_pass_cutoff)
        newDF['distance_smooth'] = smoothed_data

        verticalSpeedCalculator = VerticalSpeed(newDF)

        # TODO: refactor this a bit (move saving of the graphs to saveGraphs() function, etc.)
        if Configurations(self.__folderStruct).is_debug():
            verticalSpeedCalculator.save_graph_smooth_distances(newDF, "distance", self.__folderStruct, 500, 2500)

        if Configurations(self.__folderStruct).is_debug():
            result = verticalSpeedCalculator.calculate_scaling_factor_from_distance_between_reddots(newDF["distance"])
            newDF["scaling_factor_not_smooth"] = result
            y = ["scaling_factor", "scaling_factor_not_smooth"]
            df_to_plot = newDF.loc[(newDF['frameNumber'] > 500) & (newDF['frameNumber'] < 2500)]

            graph_plotter = GraphPlotter.createNew(df_to_plot, self.__folderStruct)
            graph_plotter.generate_graph("debug_scale_factor", y)

        return verticalSpeedCalculator

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

    #TODO: doublecheck that this logic is still correct. We probably need recursive-continuous step-by-step for every frame scaling.
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
        return result

    def __initialize_dict(self):
        if self.__df_as_dict is not None:
            return

        list_of_rows = DataframeWrapper(self.getPandasDF()).as_records_list()
        records_by_frame_id = dict()
        for row in list_of_rows:
            frame_id_of_row = row[self.COLNAME_frameNumber]
            records_by_frame_id[frame_id_of_row] = row

        self.__df_as_dict = records_by_frame_id

    def mm_per_pixel_undistorted(self, frameId : int) -> float:
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
        if Configurations(self.__folderStruct).is_debug():
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

    def __interpolate_values(self, df: pd.DataFrame) -> pd.DataFrame:

        df = DataframeWrapper(df).interpolate_nan_values_everywhere().pandas_df()

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

