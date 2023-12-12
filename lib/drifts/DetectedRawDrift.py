import math
from typing import Dict, List

import numpy as np
from scipy.stats import stats

from lib.imageProcessing.Camera import Camera
from lib.model.Box import Box
from lib.model.Point import Point
from lib.model.Vector import Vector


class DetectedRawDrift:

    def __init__(self, from_dict):
        self.__init_dict = from_dict

    @staticmethod
    def createFromDict(from_dict: Dict):
        return DetectedRawDrift(from_dict)
    def skip_row(self) -> bool:
        if self.__init_dict["outlier"] == "DETECTED_DRIFTS":
            return False
        else:
            return True

    def calculate_drifts(self):

        camera = Camera.create()
        drifts_raw = list()
        distortion_coeff = list()
        distortion_vector = list()
        center_points_undist = list()
        center_points = list()
        non_null_values_x = list()
        non_null_values_y = list()
        for feature_matcher_idx in range(0, 9):
            if not self.is_detected(feature_matcher_idx):
                continue

            center_points.append(str(self.center_point_at(feature_matcher_idx)))
            center_points_undist.append(str(self.undistorted_center_point(feature_matcher_idx)))

            distortion_vector.append(str(camera.distortion_at_point_vector(self.center_point_at(feature_matcher_idx))))
            drift = self.undistorted_drifts_at(feature_matcher_idx)
            distortion_coeff.append(str(drift))
            drifts_raw.append(str(self.drift_vector_at(feature_matcher_idx)))

            val = drift.x
            # val = self.drift_x_at(feature_matcher_idx)
            if math.isnan(val):
                continue

            # if val < -100 or val > 200:
            #     continue
            non_null_values_x.append(val)

            val = drift.y
            # val = self.drift_x_at(feature_matcher_idx)
            if math.isnan(val):
                continue
            non_null_values_y.append(val)

        # print (self.frame_id(), " center_points", center_points)
        # print (self.frame_id(), " center_points_undist", center_points_undist)
        # print (self.frame_id(), " distortion_vector", distortion_vector)
        # print (self.frame_id(), " distortion_coeff", distortion_coeff)
        # print (self.frame_id(), " drifts_raw", drifts_raw)
        return non_null_values_x, non_null_values_y

    def drift_vector(self):
        values_x, values_y = self.calculate_drifts()
        avg_x = np.mean(values_x)
        avg_y = np.mean(values_y)
        return Vector(avg_x,avg_y)


    def outliers_x(self):
        if self.skip_row():
            return "INVALID"

        values_x, values_y = self.calculate_drifts()
        drift_vec = self.drift_vector()
        response = DetectedRawDrift._has_outlier_stderr(values_x)
        if self.frame_id()>500 and self.frame_id() <1200:
            print (self.frame_id(), response, str(drift_vec), " values_x", values_x)
            # print (self.frame_id(), " non_null_values_y", non_null_values_y)

        return response

    def outliers_y(self):
        if self.skip_row():
            return "INVALID"

        values_x, values_y = self.calculate_drifts()
        response = DetectedRawDrift._has_outlier_stderr(values_y)
        return response

    @staticmethod
    def _has_outlier_stderr(ls: List) -> bool:
        if len(ls)<3:
            return "OK"

        stdev = np.std(ls)
        min_loc = ls.index(min(ls))
        max_loc = ls.index(max(ls))
        std_err = stats.sem(ls, axis=None, ddof=0)
        # print("lst     ", std_err, stdev, len(ls), min_loc, max_loc,ls)

        lst_no_min = ls[:min_loc] + ls[min_loc + 1:]
        new_std = np.std(lst_no_min)
        std_err_min = stats.sem(lst_no_min, axis=None, ddof=0)
        # print("lst_no_min", std_err_min, new_std, (stdev/new_std), len(lst_no_min), max(lst_no_min) - min(lst_no_min), lst_no_min)
        if std_err > 8 and std_err_min <4:
            # removing this one value has reduced standard error by more than twice.
            return "MIN_OUTLIER"

        lst_no_max = ls[:max_loc] + ls[max_loc + 1:]
        new_std = np.std(lst_no_max)
        std_err_max = stats.sem(lst_no_max, axis=None, ddof=0)
        # print("lst_no_max", std_err_max, new_std, (stdev/new_std), len(lst_no_max), max(lst_no_max) - min(lst_no_max), lst_no_max)
        if std_err > 8 and std_err_max < 4:
            #removing this one value has reduced standard error by more than twice.
            return "MAX_OUTLIER"

        return "OK"

    def drift_x_at(self, num: int) -> float:
        return self.__init_dict["fm_" + str(num) + "_drift_x"]

    def is_detected(self, num: int) -> bool:
        if self.__init_dict['fm_' + str(num) + '_result'] == "DETECTED":
            return True
        else:
            return False
    def frame_id(self) -> int:
        return int(self.__init_dict["frameNumber"])

    def undistorted_center_point(self, num: int) -> Point:
        camera = Camera.create()
        return camera.undistort_point(self.center_point_at(num))

    def undistorted_drifts_at(self, num: int) -> Vector:
        drift_vector = self.drift_vector_at(num)

        camera = Camera.create()
        distortion = camera.distortion_at_point_vector(self.center_point_at(num))

        return Vector(drift_vector.x*distortion.x, drift_vector.y*distortion.y)

    def center_point_at(self, num: int) -> Point:
        x_top = self.__init_dict["fm_" + str(num) + "_top_x"]
        y_top = self.__init_dict["fm_" + str(num) + "_top_y"]
        top_left = Point(x_top,y_top)

        x_bottom = self.__init_dict["fm_" + str(num) + "_bottom_x"]
        y_bottom = self.__init_dict["fm_" + str(num) + "_bottom_y"]
        bottom_right = Point(x_bottom,y_bottom)

        return Box(top_left, bottom_right).centerPoint()

    def drift_vector_at(self, num: int) -> Vector:
        x_drift = self.__init_dict["fm_" + str(num) + "_drift_x"]
        y_drift = self.__init_dict["fm_" + str(num) + "_drift_y"]
        return  Vector(x_drift, y_drift)

