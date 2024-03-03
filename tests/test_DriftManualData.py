from unittest import TestCase

from lib.drifts_interpolate.DriftRawData import DriftRawData
from lib.infra.FolderStructure import FolderStructure
from lib.model.Point import Point
from lib.drifts_detect.DriftManualData import DriftManualData
import pandas as pd

from lib.infra.DataframeWrapper import DataframeWrapper


class TestDriftManualData(TestCase):
    def test_doIt(self):
        folderStruct = FolderStructure("dirName", "V987")

        df = pd.DataFrame()
        data = {'frameNumber1': int(100),
                "locationX1": 200,
                "locationY1": 400,
                'frameNumber2': int(105),
                "locationX2": 205,
                "locationY2": 500,
                }
        # df = df.append(data, ignore_index=True)
        df = DataframeWrapper.append_to_df(df, data)

        ddm = DriftManualData._createFromDataFrame(df, folderStruct)

        # Exercise
        result = ddm._list_of_corrections()

        # Assert
        self.assertEqual(1, len(result))
        dfDrifts = result[0]

        self.assertEqual(5, len(dfDrifts.index))

        self.assertEqual(101, dfDrifts.iloc[0]["frameNumber"])
        self.assertEqual(102, dfDrifts.iloc[1]["frameNumber"])
        self.assertEqual(103, dfDrifts.iloc[2]["frameNumber"])
        self.assertEqual(104, dfDrifts.iloc[3]["frameNumber"])
        self.assertEqual(105, dfDrifts.iloc[4]["frameNumber"])

        self.assertAlmostEqual(float(20), dfDrifts.iloc[0]["driftY"], 5)
        self.assertAlmostEqual(float(20), dfDrifts.iloc[1]["driftY"], 5)
        self.assertAlmostEqual(float(20), dfDrifts.iloc[2]["driftY"], 5)
        self.assertAlmostEqual(float(20), dfDrifts.iloc[3]["driftY"], 5)
        self.assertAlmostEqual(float(20), dfDrifts.iloc[4]["driftY"], 5)

        self.assertAlmostEqual(float(1), dfDrifts.iloc[0]["driftX"], 5)
        self.assertAlmostEqual(float(1), dfDrifts.iloc[1]["driftX"], 5)
        self.assertAlmostEqual(float(1), dfDrifts.iloc[2]["driftX"], 5)
        self.assertAlmostEqual(float(1), dfDrifts.iloc[3]["driftX"], 5)
        self.assertAlmostEqual(float(1), dfDrifts.iloc[4]["driftX"], 5)

    def test_doIt_2(self):
        folderStruct = FolderStructure("dirName", "V987")

        df = pd.DataFrame()
        data = {'frameNumber1': int(7015),
                "locationX1": 1044,
                "locationY1": 444,
                'frameNumber2': int(7050),
                "locationX2": 1063,
                "locationY2": 594,
                }
        df = DataframeWrapper.append_to_df(df, data)

        ddm = DriftManualData._createFromDataFrame(df, folderStruct)

        # Exercise
        result = ddm._list_of_corrections()

        # Assert
        self.assertEqual(1, len(result))
        dfDrifts = result[0]

        self.assertEqual(35, len(dfDrifts.index))

        self.assertEqual(7016, dfDrifts.iloc[0]["frameNumber"])
        self.assertEqual(7017, dfDrifts.iloc[1]["frameNumber"])
        self.assertEqual(7018, dfDrifts.iloc[2]["frameNumber"])
        self.assertEqual(7049, dfDrifts.iloc[33]["frameNumber"])
        self.assertEqual(7050, dfDrifts.iloc[34]["frameNumber"])

        self.assertAlmostEqual(float(4.285714), dfDrifts.iloc[0]["driftY"], 5)
        self.assertAlmostEqual(float(4.285714), dfDrifts.iloc[15]["driftY"], 5)
        self.assertAlmostEqual(float(4.285714), dfDrifts.iloc[34]["driftY"], 5)

        self.assertAlmostEqual(float(0.542857), dfDrifts.iloc[0]["driftX"], 5)
        self.assertAlmostEqual(float(0.542857), dfDrifts.iloc[15]["driftX"], 5)
        self.assertAlmostEqual(float(0.542857), dfDrifts.iloc[34]["driftX"], 5)

    def test_add_manual_drift(self):
        folderStruct = FolderStructure("dirName", "V987")
        ddm = DriftManualData._createBrandNew(folderStruct)

        # Exercise
        ddm.add_manual_drift(100, Point(125, 175), 200, Point(225, 375))

        # Assert
        dfDict = ddm._getRecords()
        self.assertEqual(1, len(dfDict))
        self.assertEqual("100", dfDict[0][DriftManualData.COLNAME_frameNumber_1])
        self.assertEqual("200", dfDict[0][DriftManualData.COLNAME_frameNumber_2])
        self.assertEqual(125, int(dfDict[0][DriftManualData.COLNAME_locationX_1]))
        self.assertEqual(175, int(dfDict[0][DriftManualData.COLNAME_locationY_1]))
        self.assertEqual(225, int(dfDict[0][DriftManualData.COLNAME_locationX_2]))
        self.assertEqual(375, int(dfDict[0][DriftManualData.COLNAME_locationY_2]))

    def test_overwrite_values_one_manual_row(self):
        folderStruct = FolderStructure("dirName", "V987")

        dfRaw = pd.DataFrame()
        data = list()
        data.append({'frameNumber': 100, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 101, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 102, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 103, "driftX": 2, "driftY": 7})
        # dfRaw = DataframeWrapper.append_to_df(dfRaw, data)
        dfRaw = pd.concat([dfRaw, pd.DataFrame(data)])

        ddm = DriftManualData._createBrandNew(folderStruct)
        ddm.add_manual_drift("101", Point(100, 200), "102", Point(103, 211))  # xDrift = 3, yDrift = 11

        # Exercise
        resultDF = ddm._overwrite_values_internal(dfRaw)

        # Assert
        dfDict = resultDF.to_dict('records')
        self.assertEqual(4, len(dfDict))
        self.assertEqual(100, dfDict[0]["frameNumber"])
        self.assertEqual(2, dfDict[0]["driftX"])
        self.assertEqual(7, dfDict[0]["driftY"])

        self.assertEqual(101, dfDict[1]["frameNumber"])
        self.assertEqual(2, dfDict[1]["driftX"])
        self.assertEqual(7, dfDict[1]["driftY"])

        self.assertEqual(102, dfDict[2]["frameNumber"])
        self.assertEqual(3, dfDict[2]["driftX"])
        self.assertEqual(11, dfDict[2]["driftY"])

        self.assertEqual(103, dfDict[3]["frameNumber"])
        self.assertEqual(2, dfDict[3]["driftX"])
        self.assertEqual(7, dfDict[3]["driftY"])

    def test_overwrite_values_two_overlapping_manual_rows(self):
        folderStruct = FolderStructure("dirName", "V987")

        dfRaw = pd.DataFrame()
        data = list()
        data.append({'frameNumber': 100, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 101, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 102, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 103, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 104, "driftX": 2, "driftY": 7})
        data.append({'frameNumber': 105, "driftX": 2, "driftY": 7})
        dfRaw = pd.concat([dfRaw, pd.DataFrame(data)])

        ddm = DriftManualData._createBrandNew(folderStruct)
        ddm.add_manual_drift("101", Point(100, 200), "103", Point(106, 222))  # xDrift = 3, yDrift = 11
        ddm.add_manual_drift("102", Point(400, 800), "104", Point(410, 826))  # xDrift = 5, yDrift = 13

        # Exercise
        resultDF = ddm._overwrite_values_internal(dfRaw)

        # Assert
        dfDict = resultDF.to_dict('records')
        self.assertEqual(6, len(dfDict))

        self.assertEqual(100, dfDict[0]["frameNumber"])
        self.assertEqual(2, dfDict[0]["driftX"])
        self.assertEqual(7, dfDict[0]["driftY"])

        self.assertEqual(101, dfDict[1]["frameNumber"])
        self.assertEqual(2, dfDict[1]["driftX"])
        self.assertEqual(7, dfDict[1]["driftY"])

        self.assertEqual(102, dfDict[2]["frameNumber"])
        self.assertEqual(3, dfDict[2]["driftX"])
        self.assertEqual(11, dfDict[2]["driftY"])

        # second manual row overwrites values of the first row.
        self.assertEqual(103, dfDict[3]["frameNumber"])
        self.assertEqual(5, dfDict[3]["driftX"])
        self.assertEqual(13, dfDict[3]["driftY"])

        self.assertEqual(104, dfDict[4]["frameNumber"])
        self.assertEqual(5, dfDict[4]["driftX"])
        self.assertEqual(13, dfDict[4]["driftY"])

        self.assertEqual(105, dfDict[5]["frameNumber"])
        self.assertEqual(2, dfDict[5]["driftX"])
        self.assertEqual(7, dfDict[5]["driftY"])
