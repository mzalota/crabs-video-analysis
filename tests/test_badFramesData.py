from unittest import TestCase

import pandas as pd
from lib.data.BadFramesData import BadFramesData


class TestBadFramesData(TestCase):

    def test_isBadFrame_emptyDF(self):
        # Setup
        badframesData = BadFramesData.createFromDataFrame(None, None)
        # Exercise
        # Assert
        self.assertFalse(badframesData.is_bad_frame(50))
        self.assertEqual(55, badframesData.firstGoodFrameAfter(55))
        self.assertEqual(45, badframesData.firstGoodFrameBefore(45))

    def test_isBadFrame(self):
        # Setup
        badframes_df = pd.DataFrame()
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(99), BadFramesData.COLNAME_endFrameNumber: 101}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(44), BadFramesData.COLNAME_endFrameNumber: 46}, ignore_index=True)

        #single BadFrame
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(222), BadFramesData.COLNAME_endFrameNumber: 222}, ignore_index=True)

        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        # Exercise
        # Assert

        # --- first BadFrame range
        self.assertFalse(badframesData.is_bad_frame(42))
        self.assertFalse(badframesData.is_bad_frame(43))

        self.assertTrue(badframesData.is_bad_frame(44))
        self.assertTrue(badframesData.is_bad_frame(45))
        self.assertTrue(badframesData.is_bad_frame(46))

        self.assertFalse(badframesData.is_bad_frame(47))
        self.assertFalse(badframesData.is_bad_frame(48))
        self.assertFalse(badframesData.is_bad_frame(49))

        #--- second BadFrame range
        self.assertFalse(badframesData.is_bad_frame(97))
        self.assertFalse(badframesData.is_bad_frame(98))

        self.assertTrue(badframesData.is_bad_frame(99))
        self.assertTrue(badframesData.is_bad_frame(100))
        self.assertTrue(badframesData.is_bad_frame(101))

        self.assertFalse(badframesData.is_bad_frame(102))
        self.assertFalse(badframesData.is_bad_frame(103))

        #--- third BadFrame range
        self.assertFalse(badframesData.is_bad_frame(220))
        self.assertFalse(badframesData.is_bad_frame(221))
        self.assertTrue(badframesData.is_bad_frame(222))
        self.assertFalse(badframesData.is_bad_frame(223))
        self.assertFalse(badframesData.is_bad_frame(224))

    def test_isBadFrame_overlapingEntries(self):
        # Setup
        badframes_df = pd.DataFrame()

        #two partially overlapping bad frame ranges
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(10), BadFramesData.COLNAME_endFrameNumber: 26}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(24), BadFramesData.COLNAME_endFrameNumber: 28}, ignore_index=True)

        #bad frame range that is fully inside the first bad frame range
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(10), BadFramesData.COLNAME_endFrameNumber: 16}, ignore_index=True)

        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        # Exercise

        # Assert

        # --- check values inside and outsidefully enclosed range
        self.assertTrue(badframesData.is_bad_frame(12))
        self.assertTrue(badframesData.is_bad_frame(13))
        self.assertTrue(badframesData.is_bad_frame(14))
        self.assertTrue(badframesData.is_bad_frame(15))
        self.assertTrue(badframesData.is_bad_frame(16))
        self.assertTrue(badframesData.is_bad_frame(17))

        # --- check values inside overlap of the partially overlapping range
        self.assertTrue(badframesData.is_bad_frame(23))
        self.assertTrue(badframesData.is_bad_frame(24))
        self.assertTrue(badframesData.is_bad_frame(25))
        self.assertTrue(badframesData.is_bad_frame(26))
        self.assertTrue(badframesData.is_bad_frame(27))
        self.assertTrue(badframesData.is_bad_frame(28))

        self.assertFalse(badframesData.is_bad_frame(29))
        self.assertFalse(badframesData.is_bad_frame(30))

        self.assertFalse(badframesData.is_bad_frame(9))
        self.assertFalse(badframesData.is_bad_frame(8))

    def test_firstGoodFrameBefore(self):
        # Setup
        badframes_df = pd.DataFrame()
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(99), BadFramesData.COLNAME_endFrameNumber: 101}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(44), BadFramesData.COLNAME_endFrameNumber: 46}, ignore_index=True)

        #single BadFrame
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(222), BadFramesData.COLNAME_endFrameNumber: 222}, ignore_index=True)

        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        # Exercise

        # Assert

        # --- first BadFrame range
        self.assertEqual(badframesData.firstGoodFrameBefore(42),42)
        self.assertEqual(badframesData.firstGoodFrameBefore(43),43)
        self.assertEqual(badframesData.firstGoodFrameBefore(44),43)
        self.assertEqual(badframesData.firstGoodFrameBefore(46),43)
        self.assertEqual(badframesData.firstGoodFrameBefore(47),47)

        self.assertEqual(badframesData.firstGoodFrameBefore(98), 98)
        self.assertEqual(badframesData.firstGoodFrameBefore(99), 98)
        self.assertEqual(badframesData.firstGoodFrameBefore(100), 98)
        self.assertEqual(badframesData.firstGoodFrameBefore(101), 98)
        self.assertEqual(badframesData.firstGoodFrameBefore(102), 102)
        self.assertEqual(badframesData.firstGoodFrameBefore(103), 103)

        self.assertEqual(badframesData.firstGoodFrameBefore(221), 221)
        self.assertEqual(badframesData.firstGoodFrameBefore(222), 221)
        self.assertEqual(badframesData.firstGoodFrameBefore(223), 223)


    def test_firstGoodFrame_BeforeAndAfter_overlapingEntries(self):
        # Setup
        badframes_df = pd.DataFrame()

        # two partially overlapping bad frame ranges
        badframes_df = badframes_df.append(
            {BadFramesData.COLNAME_startfFrameNumber: int(10), BadFramesData.COLNAME_endFrameNumber: 26}, ignore_index=True)
        badframes_df = badframes_df.append(
            {BadFramesData.COLNAME_startfFrameNumber: int(24), BadFramesData.COLNAME_endFrameNumber: 30}, ignore_index=True)

        # bad frame range that is fully inside the first bad frame range
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber: int(23), BadFramesData.COLNAME_endFrameNumber: 27}, ignore_index=True)

        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        # Exercise

        # Assert

        # --- check values inside and outsidefully enclosed range
        self.assertEqual(9,badframesData.firstGoodFrameBefore(12))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(22))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(23))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(24))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(25))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(26))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(27))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(28))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(29))
        self.assertEqual(9,badframesData.firstGoodFrameBefore(30))
        self.assertEqual(31,badframesData.firstGoodFrameBefore(31))
        self.assertEqual(32,badframesData.firstGoodFrameBefore(32))

        self.assertEqual(-5, badframesData.firstGoodFrameAfter(-5))
        self.assertEqual(8, badframesData.firstGoodFrameAfter(8))
        self.assertEqual(9, badframesData.firstGoodFrameAfter(9))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(10))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(22))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(23))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(24))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(25))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(26))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(27))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(28))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(29))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(30))
        self.assertEqual(31, badframesData.firstGoodFrameAfter(31))
        self.assertEqual(32, badframesData.firstGoodFrameAfter(32))


    def test_firstBadFrame_AfterAndBefore_nonOverlaptingRanges(self):
        # Setup
        badframes_df = pd.DataFrame()
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(99), BadFramesData.COLNAME_endFrameNumber: 101}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(44), BadFramesData.COLNAME_endFrameNumber: 46}, ignore_index=True)

        #single BadFrame
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(222), BadFramesData.COLNAME_endFrameNumber: 222}, ignore_index=True)

        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        # Exercise

        # Assert

        # --- first BadFrame range
        self.assertEqual(44, badframesData.firstBadFrameAfter(41))
        self.assertEqual(44, badframesData.firstBadFrameAfter(42))
        self.assertEqual(44, badframesData.firstBadFrameAfter(43))
        self.assertEqual(44, badframesData.firstBadFrameAfter(44)) #<-- 44 is bad frame
        self.assertEqual(45, badframesData.firstBadFrameAfter(45)) #<-- 45 is bad frame
        self.assertEqual(46, badframesData.firstBadFrameAfter(46)) #<-- 46 is bad frame
        self.assertEqual(99, badframesData.firstBadFrameAfter(47))
        self.assertEqual(99, badframesData.firstBadFrameAfter(98))
        self.assertEqual(99, badframesData.firstBadFrameAfter(99)) #<-- 99 is bad frame
        self.assertEqual(100, badframesData.firstBadFrameAfter(100)) #<-- 100 is bad frame
        self.assertEqual(101, badframesData.firstBadFrameAfter(101)) #<-- 101 is bad frame
        self.assertEqual(222, badframesData.firstBadFrameAfter(102))
        self.assertEqual(222, badframesData.firstBadFrameAfter(103))
        self.assertEqual(222, badframesData.firstBadFrameAfter(220))
        self.assertEqual(222, badframesData.firstBadFrameAfter(221))
        self.assertEqual(222, badframesData.firstBadFrameAfter(222)) #<-- 222 is bad frame
        self.assertEqual(223, badframesData.firstBadFrameAfter(223))

        self.assertEqual(41, badframesData.firstBadFrameBefore(41))
        self.assertEqual(42, badframesData.firstBadFrameBefore(42))
        self.assertEqual(43, badframesData.firstBadFrameBefore(43))
        self.assertEqual(44, badframesData.firstBadFrameBefore(44)) #<-- 44 is bad frame
        self.assertEqual(45, badframesData.firstBadFrameBefore(45)) #<-- 45 is bad frame
        self.assertEqual(46, badframesData.firstBadFrameBefore(46)) #<-- 46 is bad frame
        self.assertEqual(46, badframesData.firstBadFrameBefore(47))
        self.assertEqual(46, badframesData.firstBadFrameBefore(48))
        self.assertEqual(46, badframesData.firstBadFrameBefore(49))
        self.assertEqual(46, badframesData.firstBadFrameBefore(97))
        self.assertEqual(46, badframesData.firstBadFrameBefore(98))
        self.assertEqual(99, badframesData.firstBadFrameBefore(99)) #<-- 99 is bad frame
        self.assertEqual(100, badframesData.firstBadFrameBefore(100)) #<-- 100 is bad frame
        self.assertEqual(101, badframesData.firstBadFrameBefore(101)) #<-- 101 is bad frame
        self.assertEqual(101, badframesData.firstBadFrameBefore(102))
        self.assertEqual(101, badframesData.firstBadFrameBefore(103))
        self.assertEqual(101, badframesData.firstBadFrameBefore(220))
        self.assertEqual(101, badframesData.firstBadFrameBefore(221))
        self.assertEqual(222, badframesData.firstBadFrameBefore(222)) #<-- 222 is bad frame
        self.assertEqual(222, badframesData.firstBadFrameBefore(223))
        self.assertEqual(222, badframesData.firstBadFrameBefore(224))


    def test_firstBadFrame_BeforeAndAfter_overlapingEntries(self):
        # Setup
        badframes_df = pd.DataFrame()

        # two partially overlapping bad frame ranges
        badframes_df = badframes_df.append(
            {BadFramesData.COLNAME_startfFrameNumber: int(10), BadFramesData.COLNAME_endFrameNumber: 26}, ignore_index=True)
        badframes_df = badframes_df.append(
            {BadFramesData.COLNAME_startfFrameNumber: int(24), BadFramesData.COLNAME_endFrameNumber: 30}, ignore_index=True)

        # bad frame range that is fully inside the first bad frame range
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber: int(23), BadFramesData.COLNAME_endFrameNumber: 27}, ignore_index=True)

        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        # Exercise

        # Assert

        # --- check values inside and outsidefully enclosed range
        self.assertEqual(8,badframesData.firstBadFrameBefore(8))
        self.assertEqual(9,badframesData.firstBadFrameBefore(9))
        self.assertEqual(10,badframesData.firstBadFrameBefore(10))
        self.assertEqual(11,badframesData.firstBadFrameBefore(11))
        self.assertEqual(12,badframesData.firstBadFrameBefore(12))
        self.assertEqual(13,badframesData.firstBadFrameBefore(13))
        self.assertEqual(14,badframesData.firstBadFrameBefore(14))
        self.assertEqual(15,badframesData.firstBadFrameBefore(15))
        self.assertEqual(16,badframesData.firstBadFrameBefore(16))
        self.assertEqual(17,badframesData.firstBadFrameBefore(17))
        self.assertEqual(18,badframesData.firstBadFrameBefore(18))
        self.assertEqual(19,badframesData.firstBadFrameBefore(19))
        self.assertEqual(20,badframesData.firstBadFrameBefore(20))
        self.assertEqual(21,badframesData.firstBadFrameBefore(21))
        self.assertEqual(22,badframesData.firstBadFrameBefore(22))
        self.assertEqual(23,badframesData.firstBadFrameBefore(23))
        self.assertEqual(24,badframesData.firstBadFrameBefore(24))
        self.assertEqual(25,badframesData.firstBadFrameBefore(25))
        self.assertEqual(26,badframesData.firstBadFrameBefore(26))
        self.assertEqual(27,badframesData.firstBadFrameBefore(27))
        self.assertEqual(28,badframesData.firstBadFrameBefore(28))
        self.assertEqual(29,badframesData.firstBadFrameBefore(29))
        self.assertEqual(30,badframesData.firstBadFrameBefore(30))
        self.assertEqual(30,badframesData.firstBadFrameBefore(31)) #<-- special case
        self.assertEqual(30,badframesData.firstBadFrameBefore(32)) #<-- special case

        self.assertEqual(10,badframesData.firstBadFrameAfter(8)) #<-- special case
        self.assertEqual(10,badframesData.firstBadFrameAfter(9)) #<-- special case
        self.assertEqual(10,badframesData.firstBadFrameAfter(10))
        self.assertEqual(11,badframesData.firstBadFrameAfter(11))
        self.assertEqual(12,badframesData.firstBadFrameAfter(12))
        self.assertEqual(13,badframesData.firstBadFrameAfter(13))
        self.assertEqual(14,badframesData.firstBadFrameAfter(14))
        self.assertEqual(15,badframesData.firstBadFrameAfter(15))
        self.assertEqual(16,badframesData.firstBadFrameAfter(16))
        self.assertEqual(17,badframesData.firstBadFrameAfter(17))
        self.assertEqual(18,badframesData.firstBadFrameAfter(18))
        self.assertEqual(19,badframesData.firstBadFrameAfter(19))
        self.assertEqual(20,badframesData.firstBadFrameAfter(20))
        self.assertEqual(21,badframesData.firstBadFrameAfter(21))
        self.assertEqual(22,badframesData.firstBadFrameAfter(22))
        self.assertEqual(23,badframesData.firstBadFrameAfter(23))
        self.assertEqual(24,badframesData.firstBadFrameAfter(24))
        self.assertEqual(25,badframesData.firstBadFrameAfter(25))
        self.assertEqual(26,badframesData.firstBadFrameAfter(26))
        self.assertEqual(27,badframesData.firstBadFrameAfter(27))
        self.assertEqual(28,badframesData.firstBadFrameAfter(28))
        self.assertEqual(29,badframesData.firstBadFrameAfter(29))
        self.assertEqual(30,badframesData.firstBadFrameAfter(30))
        self.assertEqual(31,badframesData.firstBadFrameAfter(31))
        self.assertEqual(32,badframesData.firstBadFrameAfter(32))