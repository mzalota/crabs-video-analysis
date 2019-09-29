from unittest import TestCase
import pandas as pd

from lib.BadFramesData import BadFramesData
from lib.DriftData import DriftData
from lib.FramesStitcher import FramesStitcher
from lib.SeeFloor import SeeFloor


class TestSeeFloor(TestCase):

    def test_maxFrameID_noBadFrames(self):
        # Setup
        df = pd.DataFrame()

        df = df.append({'frameNumber': int(95), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        driftData = DriftData(df)


        badframesData = BadFramesData(None,None)
        seeFloor = SeeFloor(driftData, badframesData, None)

        # Exercise
        maxFrameID = seeFloor.maxFrameID()
        minFrameID = seeFloor.minFrameID()

        # Assert
        self.assertEqual(minFrameID, 95)
        self.assertEqual(maxFrameID, 100)

    def test_maxFrameID_badFramesAtTheEnd(self):
        # Setup
        drifts_df = pd.DataFrame()
        drifts_df = drifts_df.append({'frameNumber': int(95), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        driftData = DriftData(drifts_df)

        badframes_df = pd.DataFrame()
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(99), BadFramesData.COLNAME_endFrameNumber: 101}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(92), BadFramesData.COLNAME_endFrameNumber: 95}, ignore_index=True)
        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        seeFloor = SeeFloor(driftData, badframesData, None)

        # Exercise
        minFrameID = seeFloor.minFrameID()
        maxFrameID = seeFloor.maxFrameID()

        # Assert
        self.assertEqual(minFrameID, 96)
        self.assertEqual(maxFrameID, 98)

    def test_jumpToSeefloorSlice(self):
        # Setup
        drifts_df = pd.DataFrame()
        drifts_df = drifts_df.append({'frameNumber': int(93), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(95), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(102), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(104), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(107), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        driftData = DriftData(drifts_df)

        badframes_df = pd.DataFrame()
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(99), BadFramesData.COLNAME_endFrameNumber: 101}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(104), BadFramesData.COLNAME_endFrameNumber: 108}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(92), BadFramesData.COLNAME_endFrameNumber: 95}, ignore_index=True)
        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        #--- good frames are 96,97,98 and 102,103. startFrame is 93, endFrame is 107

        seeFloor = SeeFloor(driftData, badframesData, None)

        # Exercise


        # Assert
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(-333,1)) # if parameter is out of bounds show first/last frame
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(91,1))
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(92,1))
        self.assertEqual(96, seeFloor.jumpToSeefloorSlice(93,1))
        self.assertEqual(96, seeFloor.jumpToSeefloorSlice(94,1))
        self.assertEqual(96, seeFloor.jumpToSeefloorSlice(95,1))
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(96,1))
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(97,1))
        self.assertEqual(102, seeFloor.jumpToSeefloorSlice(98,1))
        self.assertEqual(102, seeFloor.jumpToSeefloorSlice(99,1))
        self.assertEqual(102, seeFloor.jumpToSeefloorSlice(100,1))
        self.assertEqual(102, seeFloor.jumpToSeefloorSlice(101,1))
        self.assertEqual(103, seeFloor.jumpToSeefloorSlice(102,1))
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(103,1))
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(104,1))
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(105,1))
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(106,1))
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(107,1))
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(108,1))
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(2222,1)) # if parameter is out of bounds show first/last frame
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(109, 1))



        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(-333,-1)) # if parameter is out of bounds show first/last frame
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(91,-1)) #<-- out-of-bound frame
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(92,-1)) #<-- out-of-bound frame
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(93,-1)) #<-- 93 is bad frame - its FIRST frame
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(94,-1)) #<-- 94 is bad frame
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(95,-1)) #<-- 95 is bad frame
        self.assertEqual(93, seeFloor.jumpToSeefloorSlice(96,-1))
        self.assertEqual(96, seeFloor.jumpToSeefloorSlice(97,-1))
        self.assertEqual(96, seeFloor.jumpToSeefloorSlice(98,-1))
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(99,-1)) #<-- 99 is bad frame
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(100,-1)) #<-- 100 is bad frame
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(101,-1)) #<-- 101 is bad frame
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(102,-1))
        self.assertEqual(102, seeFloor.jumpToSeefloorSlice(103,-1))
        self.assertEqual(103, seeFloor.jumpToSeefloorSlice(104,-1)) #<-- 104 is bad frame
        self.assertEqual(103, seeFloor.jumpToSeefloorSlice(105,-1)) #<-- 105 is bad frame
        self.assertEqual(103, seeFloor.jumpToSeefloorSlice(106,-1)) #<-- 106 is bad frame
        self.assertEqual(103, seeFloor.jumpToSeefloorSlice(107,-1)) #<-- 107 is bad frame - its LAST frame
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(108,-1)) #<-- out-of-bound frame
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(2222,-1)) #<-- out-of-bound frame
        self.assertEqual(107, seeFloor.jumpToSeefloorSlice(109, -1)) #<-- out-of-bound frame


    def test_jumpToSeefloorSlice_multiSlice(self):
        # Setup
        pixels_in_frame = FramesStitcher.FRAME_HEIGHT
        pixels_in_half_frame = int(pixels_in_frame/2)

        drifts_df = pd.DataFrame()
        drifts_df = drifts_df.append({'frameNumber': int(100), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(200), 'driftY': pixels_in_half_frame, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(300), 'driftY': pixels_in_half_frame, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(400), 'driftY': pixels_in_half_frame, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(500), 'driftY': pixels_in_half_frame, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(600), 'driftY': pixels_in_half_frame, 'driftX': 0}, ignore_index=True)
        drifts_df = drifts_df.append({'frameNumber': int(700), 'driftY': pixels_in_half_frame, 'driftX': 0}, ignore_index=True)
        driftData = DriftData(drifts_df)

        badframes_df = pd.DataFrame()
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(90), BadFramesData.COLNAME_endFrameNumber: 149}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(575), BadFramesData.COLNAME_endFrameNumber: 624}, ignore_index=True)
        badframes_df = badframes_df.append({BadFramesData.COLNAME_startfFrameNumber : int(690), BadFramesData.COLNAME_endFrameNumber: 790}, ignore_index=True)
        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        #--- good frames are 150-574 and 625-689. startFrame is 100, endFrame is 700

        seeFloor = SeeFloor(driftData, badframesData, None)

        # Exercise
        # Assert
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(10,1)) # if parameter is out of bounds show first/last frame
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(99,1))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(100,1))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(101,1))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(149,1))
        self.assertEqual(350, seeFloor.jumpToSeefloorSlice(150,1))
        self.assertEqual(352, seeFloor.jumpToSeefloorSlice(151,1)) #<>>>
        self.assertEqual(353, seeFloor.jumpToSeefloorSlice(152,1)) #<>>>
        self.assertEqual(375, seeFloor.jumpToSeefloorSlice(175,1))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(572,1))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(573,1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(574,1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(575,1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(623,1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(624,1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(625,1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(626,1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(627,1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(687,1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(688,1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(689,1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(690,1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(691,1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(699,1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(700,1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(701,1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(702,1))

        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(10, 2))  # if parameter is out of bounds show first/last frame
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(99, 2))

        # step 1 is to jump over bad block, step 2 is to jump 200 frames
        self.assertEqual(350, seeFloor.jumpToSeefloorSlice(100, 2))
        self.assertEqual(350, seeFloor.jumpToSeefloorSlice(101, 2))
        self.assertEqual(350, seeFloor.jumpToSeefloorSlice(149, 2))

        # normal 2 jumps without any bad blocks in the middle
        self.assertEqual(550, seeFloor.jumpToSeefloorSlice(150, 2))
        self.assertEqual(553, seeFloor.jumpToSeefloorSlice(151, 2))
        self.assertEqual(554, seeFloor.jumpToSeefloorSlice(152, 2))
        self.assertEqual(555, seeFloor.jumpToSeefloorSlice(153, 2))
        self.assertEqual(555, seeFloor.jumpToSeefloorSlice(154, 2))  #<-- ?? why diff input but same output. Who is rounding where?
        self.assertEqual(555, seeFloor.jumpToSeefloorSlice(155, 2))  #<-- ?? why diff input but same output. Who is rounding where?
        self.assertEqual(558, seeFloor.jumpToSeefloorSlice(156, 2))
        self.assertEqual(559, seeFloor.jumpToSeefloorSlice(157, 2))
        self.assertEqual(560, seeFloor.jumpToSeefloorSlice(158, 2))
        self.assertEqual(560, seeFloor.jumpToSeefloorSlice(159, 2)) #<-- ?? why diff input but same output. Who is rounding where?
        self.assertEqual(560, seeFloor.jumpToSeefloorSlice(160, 2)) #<-- ?? why diff input but same output. Who is rounding where?

        # jump #1 is 200 frames, then second jump is shorter to the last good frame before bad block

        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(172,2))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(173,2))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(174,2)) #<-- ??
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(175,2)) #<-- ??
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(176,2))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(177,2))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(178,2))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(179,2))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(180, 2))

        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(180,3))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(180,4))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(180,5))
        #self.assertEqual(35444, seeFloor.jumpToSeefloorSlice(150,1))


        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(10,-1)) # if parameter is out of bounds show first/last frame
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(99,-1))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(100,-1))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(101,-1))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(149,-1))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(150,-1))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(151,-1))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(175,-1))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(348,-1))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(349,-1))
        self.assertEqual(151, seeFloor.jumpToSeefloorSlice(350,-1))
        self.assertEqual(152, seeFloor.jumpToSeefloorSlice(351,-1))
        self.assertEqual(374, seeFloor.jumpToSeefloorSlice(573,-1))
        self.assertEqual(375, seeFloor.jumpToSeefloorSlice(574,-1)) #<--- ??
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(575,-1))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(576,-1))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(623,-1))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(624,-1))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(625,-1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(626,-1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(627,-1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(687,-1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(688,-1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(689,-1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(690,-1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(691,-1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(699,-1))
        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(700,-1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(701,-1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(702,-1))

        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(10, -2))  # if parameter is out of bounds show first/last frame
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(99, -2))

        # step 1 is to jump over bad block, step 2 is to jump 200 frames
        self.assertEqual(375, seeFloor.jumpToSeefloorSlice(600, -2))
        self.assertEqual(375, seeFloor.jumpToSeefloorSlice(575, -2))

        #TODO: why 176 and not 175? where did extra 1 come from
        self.assertEqual(176, seeFloor.jumpToSeefloorSlice(574, -2)) #<--- why 176 and not 175? where did extra 1 come from
        self.assertEqual(175, seeFloor.jumpToSeefloorSlice(573, -2))

        #TODO:fix test cases below
        # normal 2 jumps without any bad blocks in the middle
        self.assertEqual(152, seeFloor.jumpToSeefloorSlice(550, -2))
        self.assertEqual(151, seeFloor.jumpToSeefloorSlice(549, -2))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(548, -2))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(547, -2))
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(546, -2))  #<-- ?? why diff input but same output. Who is rounding where?
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(545, -2))  #<-- ?? why diff input but same output. Who is rounding where?
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(351, -2))  #<-- ?? why diff input but same output. Who is rounding where?
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(350, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(349, -2)) #<-- ?? why diff input but same output. Who is rounding where?
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(348, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(348, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(152, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(151, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(150, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(149, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(148, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(147, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(103, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(102, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(101, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(100, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(99, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(98, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(92, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(91, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(90, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(89, -2))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(88, -2))

        # jump #1 is 200 frames, then second jump is shorter to the last good frame before bad block

        self.assertEqual(689, seeFloor.jumpToSeefloorSlice(700, -1))
        self.assertEqual(625, seeFloor.jumpToSeefloorSlice(700, -2))
        self.assertEqual(574, seeFloor.jumpToSeefloorSlice(700, -3))
        self.assertEqual(375, seeFloor.jumpToSeefloorSlice(700, -4))
        self.assertEqual(176, seeFloor.jumpToSeefloorSlice(700, -5)) #<-- ?? why not 175?
        self.assertEqual(150, seeFloor.jumpToSeefloorSlice(700, -6))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(700, -7))
        self.assertEqual(100, seeFloor.jumpToSeefloorSlice(700, -8))

        self.assertEqual(176, seeFloor.jumpToSeefloorSlice(699,-5))
        self.assertEqual(176, seeFloor.jumpToSeefloorSlice(698,-5))

        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(701, -1))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(701, -2))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(701, -3))
        self.assertEqual(700, seeFloor.jumpToSeefloorSlice(702, -3))