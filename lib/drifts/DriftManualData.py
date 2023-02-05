import numpy
import pandas as pd
from datetime import datetime
from lib.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper
from lib.infra.DataframeWrapper import DataframeWrapper


class DriftManualData(PandasWrapper):

    COLNAME_frameNumber_1 = 'frameNumber1'
    COLNAME_locationX_1 = "locationX1"
    COLNAME_locationY_1 = "locationY1"
    COLNAME_frameNumber_2 = 'frameNumber2'
    COLNAME_locationX_2 = "locationX2"
    COLNAME_locationY_2 = "locationY2"
    COLNAME_createdOn = "createdOn"

    def __init__(self, df, folderStruct):
        # type: (pd.DataFrame, FolderStructure) -> DriftManualData
        self.__folderStruct = folderStruct
        self.__df = df

    @staticmethod
    def createFromDataFrame(df, folderStruct):
        newObj = DriftManualData(df, folderStruct)
        return newObj

    @staticmethod
    def createBrandNew(folderStruct):
        df = pd.DataFrame(columns=DriftManualData.column_names())
        newObj = DriftManualData(df, folderStruct)
        return newObj

    @staticmethod
    def createFromFile(folderStruct):
        filepath = folderStruct.getDriftsManualFilepath()
        if folderStruct.fileExists(filepath):
            df = PandasWrapper.readDataFrameFromCSV(filepath, DriftManualData.column_names())
            df = df[1:]  # .reset_index(drop=True)
        else:
            df = pd.DataFrame(columns=DriftManualData.column_names())

        newObj = DriftManualData(df, folderStruct)
        return newObj

    @staticmethod
    def column_names():
        column_names = [
                        DriftManualData.COLNAME_frameNumber_1,
                        DriftManualData.COLNAME_locationX_1,
                        DriftManualData.COLNAME_locationY_1,
                        DriftManualData.COLNAME_frameNumber_2,
                        DriftManualData.COLNAME_locationX_2,
                        DriftManualData.COLNAME_locationY_2,
                        DriftManualData.COLNAME_createdOn
                        ]
        return column_names

    def add_manual_drift(self, frame_number1, point1, frame_number2, point2):
        # type: (int, Point, int, Point) -> None


        if frame_number1 < frame_number2:
            row_to_append = {
                         self.COLNAME_frameNumber_1: str(int(frame_number1)),
                         self.COLNAME_locationX_1: point1.x,
                         self.COLNAME_locationY_1: point1.y,
                         self.COLNAME_frameNumber_2: str(int(frame_number2)),
                         self.COLNAME_locationX_2: point2.x,
                         self.COLNAME_locationY_2: point2.y,
                         self.COLNAME_createdOn: datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                         }
        else:
            row_to_append = {
                         self.COLNAME_frameNumber_1: str(int(frame_number2)),
                         self.COLNAME_locationX_1: point2.x,
                         self.COLNAME_locationY_1: point2.y,
                         self.COLNAME_frameNumber_2: str(int(frame_number1)),
                         self.COLNAME_locationX_2: point1.x,
                         self.COLNAME_locationY_2: point1.y,
                         self.COLNAME_createdOn: datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                         }

        # self.__df = self.__df.append(row_to_append, ignore_index=True)
        self.__df = DataframeWrapper.append_to_df(self.__df, row_to_append)
        #self.saveToFile()

        return row_to_append

    def saveToFile(self):
        self.__df.to_csv(self.__folderStruct.getDriftsManualFilepath(), sep='\t', index=False)

    def getCount(self):
        return len(self.__df.index)

    def getPandasDF(self):
        # type: () -> pd.DataFrame
        return self.__df

    def save_to_file(self):
        filepath = self.__folderStruct.getDriftsManualFilepath()
        self.__df.to_csv(filepath, sep='\t', index=False)

    def doIt(self):
        corrections = list()
        tmp = self.__df.to_dict('records')
        for rec in tmp:
            startLocationX = int(rec["locationX1"])
            endLocationX = int(rec["locationX2"])
            startLocationY = int(rec["locationY1"])
            endLocationY = int(rec["locationY2"])

            startFrameID = int(rec["frameNumber1"])+1
            endFrameID = int(rec["frameNumber2"])+1
            numOfFrames = endFrameID-startFrameID
            if numOfFrames == 0:
                continue

            arrayOfFrameIDs = numpy.arange(start=startFrameID, stop=endFrameID, step=1)
            newDF = pd.DataFrame(arrayOfFrameIDs, columns=["frameNumber"])
            driftX = (endLocationX - startLocationX) / float(numOfFrames)
            newDF["driftX"] = driftX

            driftY = (endLocationY - startLocationY) / float(numOfFrames)
            newDF["driftY"] = driftY
            corrections.append(newDF)

        return corrections

    def overwrite_values(self, df):
        # type: (pd.DataFrame) -> pd.DataFrame
        df = df.set_index("frameNumber")
        multipleCorrectionDFs = self.doIt()
        for correctionsDF in multipleCorrectionDFs:
            correctionsDF = correctionsDF.set_index("frameNumber")
            df = correctionsDF.combine_first(df)

        return df.reset_index()


    def minFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].min()

    def maxFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].max()