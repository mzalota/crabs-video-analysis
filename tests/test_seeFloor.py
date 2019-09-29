from unittest import TestCase
import pandas as pd

from lib.BadFramesData import BadFramesData
from lib.DriftData import DriftData
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

        #--- good frames are 96,97,98 and 102,103. startFrame is 95, endFrame is 107

        seeFloor = SeeFloor(driftData, badframesData, None)

        # Exercise


        # Assert
        self.assertEqual(96, seeFloor.jumpToSeefloorSlice(95,1))
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(96,1))
        self.assertEqual(98, seeFloor.jumpToSeefloorSlice(97,1))
        self.assertEqual(102, seeFloor.jumpToSeefloorSlice(98,1))
