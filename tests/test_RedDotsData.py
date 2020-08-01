from unittest import TestCase


import pandas as pd
from mock import MagicMock

from lib.data.RedDotsData import RedDotsData


class TestRedDotsData(TestCase):
    def test_getMiddleFrameIDOfBiggestGap_allRedDotsFileAreEmpty(self):
        df = pd.DataFrame()

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        #Exercise
        result = rdData.getMiddleFrameIDOfBiggestGap()

        #Assert
        self.assertIsNone(result)

    def test_getMiddleFrameIDOfBiggestGap_dot2HasOneGaps_middleFrameIsReturned(self):
        df = pd.DataFrame()

        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        result = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(12, result)

    def test_getMiddleFrameIDOfBiggestGap_dot2HasTwoGaps_middleFrameOfSecondLargerGapIsReturned(self):
        df = pd.DataFrame()
        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        #Exercise
        result = rdData.getMiddleFrameIDOfBiggestGap()

        #Assert
        self.assertEqual(13, result)


    def test_getMiddleFrameIDOfBiggestGap_dot2LargestGapInTheBegining_middleFrameOfStartingGapIsReturned(self):
        df = pd.DataFrame()

        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate) # largest gap here
        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)


        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        result = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(11, result)

    def test_getMiddleFrameIDOfBiggestGap_dot2LargestGapIsAtTheEnd_middleFrameOfEndingGapIsReturned(self):
        df = pd.DataFrame()

        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)

        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        result = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(13, result)

    def add_value_to_df(self, df, frame, origin1, origin2):
        df = df.append({'frameNumber': int(frame), "origin_dot1": origin1, "origin_dot2": origin2}, ignore_index=True)
        return df

    def test_getMiddleFrameIDOfBiggestGap_dot2HasLargerGapThenDot1_middleFrameOfDot2EndingGapIsReturned(self):
        df = pd.DataFrame()

        df = df.append({'frameNumber': int(10), "origin_dot1": RedDotsData.VALUE_ORIGIN_raw}, ignore_index=True)

        df = df.append({'frameNumber': int(11), "origin_dot1": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)

        df = df.append({'frameNumber': int(12), "origin_dot1": RedDotsData.VALUE_ORIGIN_raw}, ignore_index=True)

        df = df.append({'frameNumber': int(13), "origin_dot1": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)
        df = df.append({'frameNumber': int(14), "origin_dot1": RedDotsData.VALUE_ORIGIN_raw}, ignore_index=True)

        df = df.append({'frameNumber': int(15), "origin_dot1": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)

        df = df.append({'frameNumber': int(16), "origin_dot1": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)


        df = df.append({'frameNumber': int(10), "origin_dot2": RedDotsData.VALUE_ORIGIN_raw}, ignore_index=True)
        df = df.append({'frameNumber': int(11), "origin_dot2": RedDotsData.VALUE_ORIGIN_raw}, ignore_index=True)

        df = df.append({'frameNumber': int(12), "origin_dot2": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)

        df = df.append({'frameNumber': int(13), "origin_dot2": RedDotsData.VALUE_ORIGIN_raw}, ignore_index=True)

        df = df.append({'frameNumber': int(14), "origin_dot2": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)
        df = df.append({'frameNumber': int(15), "origin_dot2": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)
        df = df.append({'frameNumber': int(16), "origin_dot2": RedDotsData.VALUE_ORIGIN_interpolate}, ignore_index=True)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        result = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(14, result)

    def test_getMiddleFrameIDOfBiggestGap_originsOfDot2AreRawAndManual_middleFrameOfSecondGapIsReturned(self):
        df = pd.DataFrame()

        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)

        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_manual)

        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)

        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        result = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(13, result)
