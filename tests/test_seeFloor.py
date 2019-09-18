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

        seeFloor = SeeFloor(driftData, None, None)

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
        badframesData = BadFramesData.createFromDataFrame(None, badframes_df)

        seeFloor = SeeFloor(driftData, badframesData, None)

        # Exercise
        maxFrameID = seeFloor.maxFrameID()
        minFrameID = seeFloor.minFrameID()

        # Assert
        self.assertEqual(minFrameID, 95)
        self.assertEqual(maxFrameID, 97)