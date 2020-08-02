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
        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)# Largest gap here
        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        frame,gap = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(12, frame)
        self.assertEqual(5, gap)

    def test_getMiddleFrameIDOfBiggestGap_dot2HasTwoGaps_middleFrameOfSecondLargerGapIsReturned(self):
        df = pd.DataFrame()
        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate) # Largest gap here
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        #Exercise
        frame,gap = rdData.getMiddleFrameIDOfBiggestGap()

        #Assert
        self.assertEqual(13, frame)
        self.assertEqual(3, gap)


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
        frame,gap  = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(11, frame)
        self.assertEqual(3, gap)

    def test_getMiddleFrameIDOfBiggestGap_dot2LargestGapIsAtTheEnd_middleFrameOfEndingGapIsReturned(self):
        df = pd.DataFrame()

        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)

        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate) #Largest gap here
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        frame,gap = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(13, frame)
        self.assertEqual(3, gap)

    def add_value_to_df(self, df, frame, origin1, origin2):
        df = df.append({'frameNumber': int(frame), "origin_dot1": origin1, "origin_dot2": origin2}, ignore_index=True)
        return df

    def test_getMiddleFrameIDOfBiggestGap_dot2HasLargerGapThenDot1_middleFrameOfDot2EndingGapIsReturned(self):
        df = pd.DataFrame()

        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw,         RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_interpolate, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw,         RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_interpolate, RedDotsData.VALUE_ORIGIN_raw)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw,         RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_interpolate, RedDotsData.VALUE_ORIGIN_interpolate) #Largest Gap in Dot 2 here
        df = self.add_value_to_df(df, 16, RedDotsData.VALUE_ORIGIN_interpolate, RedDotsData.VALUE_ORIGIN_interpolate)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        frame,gap  = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(14, frame)
        self.assertEqual(3, gap)

    def test_getMiddleFrameIDOfBiggestGap_originsOfDot2AreRawAndManual_middleFrameOfSecondGapIsReturned(self):
        df = pd.DataFrame()

        df = self.add_value_to_df(df, 10, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        df = self.add_value_to_df(df, 11, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)

        df = self.add_value_to_df(df, 12, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_manual)

        df = self.add_value_to_df(df, 13, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate)
        df = self.add_value_to_df(df, 14, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_interpolate) #Largest Gap here

        df = self.add_value_to_df(df, 15, RedDotsData.VALUE_ORIGIN_raw, RedDotsData.VALUE_ORIGIN_raw)

        rdData = RedDotsData.createWithRedDotsManualData(None, None)
        rdData.getPandasDF = MagicMock(return_value=df)

        # Exercise
        frame,gap = rdData.getMiddleFrameIDOfBiggestGap()

        # Assert
        self.assertEqual(13, frame)
        self.assertEqual(3, gap)
