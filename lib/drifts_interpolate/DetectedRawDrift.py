from __future__ import annotations
from typing import Dict, List, Any

import numpy as np
from scipy.stats import stats

from lib.infra.DataframeWrapper import DataframeWrapper
from lib.model.Box import Box
from lib.model.Point import Point
from lib.model.Vector import Vector
from lib.seefloor.VerticalSpeed import VerticalSpeed


class DetectedRawDrift:

    def __init__(self, from_dict, verticalSpeed: VerticalSpeed):
        self.__init_dict = from_dict
        self.__verticalSpeed = verticalSpeed

    @staticmethod
    def createFromDict(from_dict: Dict, verticalSpeed: VerticalSpeed) -> DetectedRawDrift:
        new_obj = DetectedRawDrift(from_dict, verticalSpeed)
        new_obj._calculate_drifts()
        return new_obj

    @staticmethod
    def createListFromDataFrame(inputDFW: DataframeWrapper, verticalSpeed: VerticalSpeed) -> List[DetectedRawDrift]:
        records_list_all = inputDFW.as_records_list()
        raw_drift_objs = [DetectedRawDrift.createFromDict(k, verticalSpeed) for k in records_list_all]
        return raw_drift_objs

    def to_dict(self) -> Dict:
        result = dict()
        for k, v in self.__init_dict.items():
            if k.endswith("_drift_x_new") or k.endswith("_drift_y_new"):
                result[k] = v
            # if k == "frameNumber":
            #     result[k] = v

        return result

    def skip_row(self) -> bool:
        if self.__init_dict["outlier"] == "DETECTED_DRIFTS":
            return False
        else:
            return True

    def _calculate_drifts(self):
        non_null_values_x = list()
        non_null_values_y = list()

        for feature_matcher_idx in range(0, 9):
            if not self.__is_detected(feature_matcher_idx):
                continue

            feature_location = self.center_point_at(feature_matcher_idx)
            drift_vector = self.drift_vector_at(feature_matcher_idx)

            zoom_factor_new = self.__verticalSpeed.zoom_compensation(self.frame_id() - 1, self.frame_id())
            diff_due_to_zoom = VerticalSpeed.zoom_correction(feature_location, zoom_factor_new)

            result = drift_vector.minus(diff_due_to_zoom)

            non_null_values_x.append(result.x)
            non_null_values_y.append(result.y)

            self.__init_dict["fm_" + str(feature_matcher_idx) + "_drift_x_new"] = result.x
            self.__init_dict["fm_" + str(feature_matcher_idx) + "_drift_y_new"] = result.y

        return non_null_values_x, non_null_values_y

    def drift_x(self) -> float | None:
        values_x, values_y = self._calculate_drifts()
        if len(values_x) == 0 :
            return None

        avg_x = np.mean(values_x)
        return avg_x

    def drift_y(self) -> float | None:
        values_x, values_y = self._calculate_drifts()
        if len(values_y) == 0:
            return None

        avg_y = np.mean(values_y)
        return avg_y

    def outliers_x(self):
        if self.skip_row():
            return "INVALID"

        values_x, values_y = self._calculate_drifts()
        response = DetectedRawDrift._has_outlier_stderr(values_x)
        return response

    def outliers_y(self):
        if self.skip_row():
            return "INVALID"

        values_x, values_y = self._calculate_drifts()
        response = DetectedRawDrift._has_outlier_stderr(values_y)
        return response

    @staticmethod
    def _has_outlier_stderr(ls: List) -> bool:
        if len(ls) < 3:
            return "OK"

        min_loc = ls.index(min(ls))
        max_loc = ls.index(max(ls))
        std_err = stats.sem(ls, axis=None, ddof=0)
        # print("lst     ", std_err, stdev, len(ls), min_loc, max_loc,ls)

        lst_no_min = ls[:min_loc] + ls[min_loc + 1:]
        new_std = np.std(lst_no_min)
        std_err_min = stats.sem(lst_no_min, axis=None, ddof=0)
        # print("lst_no_min", std_err_min, new_std, (stdev/new_std), len(lst_no_min), max(lst_no_min) - min(lst_no_min), lst_no_min)
        if std_err > 8 and std_err_min < 4:
            # removing this one value has reduced standard error by more than twice.
            return "MIN_OUTLIER"

        lst_no_max = ls[:max_loc] + ls[max_loc + 1:]
        new_std = np.std(lst_no_max)
        std_err_max = stats.sem(lst_no_max, axis=None, ddof=0)
        # print("lst_no_max", std_err_max, new_std, (stdev/new_std), len(lst_no_max), max(lst_no_max) - min(lst_no_max), lst_no_max)
        if std_err > 8 and std_err_max < 4:
            # removing this one value has reduced standard error by more than twice.
            return "MAX_OUTLIER"

        return "OK"

    def _zoom_factor(self) -> float:
        return self.__init_dict["scaling_factor"]

    def drift_x_at(self, num: int) -> float:
        return self.__init_dict["fm_" + str(num) + "_drift_x"]

    def __is_detected(self, num: int) -> bool:
        if self.__init_dict['fm_' + str(num) + '_result'] == "DETECTED":
            return True
        else:
            return False

    def frame_id(self) -> int:
        return int(self.__init_dict["frameNumber"])

    def center_point_at(self, num: int) -> Point:
        x_top = self.__init_dict["fm_" + str(num) + "_top_x"]
        y_top = self.__init_dict["fm_" + str(num) + "_top_y"]
        top_left = Point(x_top, y_top)

        x_bottom = self.__init_dict["fm_" + str(num) + "_bottom_x"]
        y_bottom = self.__init_dict["fm_" + str(num) + "_bottom_y"]
        bottom_right = Point(x_bottom, y_bottom)

        return Box(top_left, bottom_right).centerPoint()

    def drift_vector_at(self, num: int) -> Vector:
        x_drift = self.__init_dict["fm_" + str(num) + "_drift_x"]
        y_drift = self.__init_dict["fm_" + str(num) + "_drift_y"]
        return Vector(x_drift, y_drift)
