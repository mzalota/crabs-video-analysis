from __future__ import annotations

import numpy
import pandas as pd

from lib.data.PandasWrapper import PandasWrapper
from lib.infra.DataframeWrapper import DataframeWrapper
from lib.infra.FolderStructure import FolderStructure
from lib.seefloor.VerticalSpeed import VerticalSpeed


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


    def generate_clean_drifts(self,drifts_interpolator, verticalSpeed: VerticalSpeed, driftsDetectionStep: int) -> None:
        df = drifts_interpolator.generate_clean_drifts2(self, driftsDetectionStep, verticalSpeed)
        self.__df = df

    def pandas_df(self):
        return self.__df

    def min_frame_id(self) -> int:
        return self.__df[self.__COLNAME_frameNumber].min()

    def max_frame_id(self) -> int:
        return self.__df[self.__COLNAME_frameNumber].max()

    def _replaceInvalidValuesWithNaN(self, df):
        # type: (pd.DataFrame) -> pd.DataFrame
        df.loc[df['driftY'] == -999, ['driftY', 'driftX']] = numpy.nan
        df.loc[df['driftX'] == -888, ['driftX', 'driftY']] = numpy.nan
        return df

    def raw_drifts_with_nans(self):
        df = self.pandas_df().copy()
        df = self._replaceInvalidValuesWithNaN(df)
        return df

    def remove_values_in_failed_records(self, df):
        for feature_matcher_idx in range(0, 9):
            num = str(feature_matcher_idx)
            column_name_y_drift_raw = "fm_" + num + "_drift_y"
            column_name_x_drift_raw = "fm_" + num + "_drift_x"
            df.loc[df['fm_' + num + '_result'] != "DETECTED", [column_name_y_drift_raw, column_name_x_drift_raw]] = numpy.nan
            df = DataframeWrapper(df).interpolate_nan_values_everywhere().pandas_df()
        return df

