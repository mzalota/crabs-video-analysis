from unittest import TestCase

from lib.DriftData import DriftData
from lib.VelocityDetector import VelocityDetector
from lib.common import Vector
import pandas as pd

class TestDriftData(TestCase):

    def test_yPixelsBetweenFrames_firstParemeterIsLessThanFirstFrame_returnsNone(self):
        # Setup
        df = pd.DataFrame()
        #df = pd.DataFrame(columns=['frameNumber', 'driftY'])

        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(50,99)

        # Assert
        self.assertEqual(result, None)

    def test_yPixelsBetweenFrames_firstParemeterIsLargerThanLastFrameID_returnsNone(self):
        # Setup
        df = pd.DataFrame()
        #df = pd.DataFrame(columns=['frameNumber', 'driftY'])

        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(107,99)

        # Assert
        self.assertEqual(result, None)

    def test_yPixelsBetweenFrames_secondParemeterIsLargerThanLastFrameID_returnsNone(self):
        # Setup
        df = pd.DataFrame()
        #df = pd.DataFrame(columns=['frameNumber', 'driftY'])

        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(99, 105)

        # Assert
        self.assertEqual(result, None)

    def test_yPixelsBetweenFrames_secondParemeterIsLessThanFirstFrameID_returnsNone(self):
        # Setup
        df = pd.DataFrame()
        #df = pd.DataFrame(columns=['frameNumber', 'driftY'])

        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(50,60)

        # Assert
        self.assertEqual(result, None)

    def test_yPixelsBetweenFrames_secondParemeterIsLessThanFirstFrame_returnsNone(self):
        # Setup
        df = pd.DataFrame()

        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(100,50)

        # Assert
        self.assertEqual(result, None)

    def test_yPixelsBetweenFrames_sameFrameInDataFrame_zeroPixels(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(102), 'driftY': 16, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(100,100)

        # Assert
        self.assertEqual(result, 0)

    def test_yPixelsBetweenFrames_bothFrameIDsInDataFrame_pixelsIsDrift(self):
        # Setup
        df = pd.DataFrame()

        df = df.append({'frameNumber': int(98), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 7, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(102), 'driftY': 11, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(100,102)

        # Assert
        self.assertEqual(result, 11)

    def test_yPixelsBetweenFrames_bothFrameIDsInDataFrameSeveralEntreesApart_pixelsIsSumOfDrifts(self):
        # Setup
        df = pd.DataFrame()

        df = df.append({'frameNumber': int(98), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 7, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(102), 'driftY': 11, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(104), 'driftY': 13, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(106), 'driftY': 17, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(100,106)

        # Assert
        self.assertEqual(result, (11+13+17))

    def test_yPixelsBetweenFrames_frameIDsinReverseOrder_negativePixels(self):
        # Setup
        df = pd.DataFrame()

        df = df.append({'frameNumber': int(98), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 7, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(102), 'driftY': 11, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(104), 'driftY': 13, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(106), 'driftY': 17, 'driftX': 0}, ignore_index=True)

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(106,100)

        # Assert
        self.assertEqual(result, -(11+13+17))

    def test_yPixelsBetweenFrames_sameFrameIDbetweenDataFrameEntries_zeroPixels(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(98), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(102), 'driftY': 16, 'driftX': 0}, ignore_index=True)
        #df.count()

        # Exercise
        driftData = DriftData(df)
        result = driftData.yPixelsBetweenFrames(101,101)

        # Assert
        self.assertEqual(result, 0)


    def test_yPixelsBetweenFrames_smallStepToFrameIDinDataFrame_proRatedPixels(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(95), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 15, 'driftX': 0}, ignore_index=True) #drift-per-frame = 3
        df = df.append({'frameNumber': int(105), 'driftY': 25, 'driftX': 0}, ignore_index=True) #drift-per-frame = 5
        #df.count()

        # Exercise
        driftData = DriftData(df)
        resultTwoFramesStep = driftData.yPixelsBetweenFrames(98,100)
        resultThreeFramesStep = driftData.yPixelsBetweenFrames(97,100)

        oneFrameStep = driftData.yPixelsBetweenFrames(104,105)
        fourFramesStep = driftData.yPixelsBetweenFrames(101,105)
        # Assert
        self.assertEqual(resultTwoFramesStep, (3*2))
        self.assertEqual(resultThreeFramesStep, (3*3))
        self.assertEqual(oneFrameStep, (5*1))
        self.assertEqual(fourFramesStep, (5*4))


    def test_yPixelsBetweenFrames_smallStepFromFrameIDinDataFrame_proRatedPixels(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(95), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 15, 'driftX': 0}, ignore_index=True) #drift-per-frame = 3
        df = df.append({'frameNumber': int(105), 'driftY': 25, 'driftX': 0}, ignore_index=True) #drift-per-frame = 5
        #df.count()

        # Exercise
        driftData = DriftData(df)
        resultTwoFramesStep = driftData.yPixelsBetweenFrames(95,97)
        resultThreeFramesStep = driftData.yPixelsBetweenFrames(95,98)

        oneFrameStep = driftData.yPixelsBetweenFrames(100,101)
        fourFramesStep = driftData.yPixelsBetweenFrames(100,104)
        # Assert
        self.assertEqual(resultTwoFramesStep, (3*2))
        self.assertEqual(resultThreeFramesStep, (3*3))
        self.assertEqual(oneFrameStep, (5*1))
        self.assertEqual(fourFramesStep, (5*4))

    def test_yPixelsBetweenFrames_complexStep_proRatedAndYDrift(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(95), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 15, 'driftX': 0}, ignore_index=True) #drift-per-frame = 3
        df = df.append({'frameNumber': int(105), 'driftY': 25, 'driftX': 0}, ignore_index=True) #drift-per-frame = 5
        df = df.append({'frameNumber': int(110), 'driftY': 35, 'driftX': 0}, ignore_index=True) #drift-per-frame = 2
        #df.count()

        # Exercise
        driftData = DriftData(df)
        resultTwoFramesStep = driftData.yPixelsBetweenFrames(97,107)

        # Assert
        self.assertEqual(resultTwoFramesStep, (3*3+25+7*2))


    def test_yPixelsBetweenFrames_stepsInDataFrameAreUnequal_proRatedAndYDrift(self):
        # Setup
        df = pd.DataFrame()
        df = df.append({'frameNumber': int(97), 'driftY': 0, 'driftX': 0}, ignore_index=True)
        df = df.append({'frameNumber': int(100), 'driftY': 15, 'driftX': 0}, ignore_index=True) #drift-per-frame = 5
        df = df.append({'frameNumber': int(107), 'driftY': 21, 'driftX': 0}, ignore_index=True) #drift-per-frame = 3
        df = df.append({'frameNumber': int(110), 'driftY': 6, 'driftX': 0}, ignore_index=True) #drift-per-frame = 2
        #df.count()

        # Exercise
        driftData = DriftData(df)
        resultTwoFramesStep = driftData.yPixelsBetweenFrames(98,108)

        # Assert
        self.assertEqual(resultTwoFramesStep, (2*5+21+1*2))

