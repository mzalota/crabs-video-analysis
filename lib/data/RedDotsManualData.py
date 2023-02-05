import math

import numpy as np
import pandas as pd

from lib.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsRawData import RedDotsRawData
from lib.infra.DataframeWrapper import DataframeWrapper


class RedDotsManualData(PandasWrapper):
    # __df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_dotName = "dotName"
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"

    __VALUE_redDot1 = "redDot1"
    __VALUE_redDot2 = "redDot2"

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> RedDotsManualData
        self.__folderStruct = folderStruct
        self.__initializeManualDF(folderStruct)

    def __initializeManualDF(self, folderStruct):
        column_names = [self.__COLNAME_frameNumber, self.__COLNAME_dotName, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]

        manual_filepath = folderStruct.getRedDotsManualFilepath()
        if folderStruct.fileExists(manual_filepath):
            self.__df = self.readDataFrameFromCSV(manual_filepath)
        else:
            self.__df = pd.DataFrame(columns=column_names)
            self.__saveManualDFToFile(manual_filepath)

    def getCount(self):
        # type: () -> int
        return len(self.__df.index)

    def getPandasDF(self):
        # type: () -> pd.DataFrame
        return self.__df

    def __minFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].max() #[0]

    def __maxFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].max()

    def addManualDots(self, frameID, box):
        rowRedDot1 = {}
        rowRedDot1[self.__COLNAME_frameNumber]=frameID
        rowRedDot1[self.__COLNAME_dotName]=self.__VALUE_redDot1
        rowRedDot1[self.__COLNAME_centerPoint_x] = box.topLeft.x
        rowRedDot1[self.__COLNAME_centerPoint_y] = box.topLeft.y

        rowRedDot2 = {}
        rowRedDot2[self.__COLNAME_frameNumber]=frameID
        rowRedDot2[self.__COLNAME_dotName]=self.__VALUE_redDot2
        rowRedDot2[self.__COLNAME_centerPoint_x] = box.bottomRight.x
        rowRedDot2[self.__COLNAME_centerPoint_y] = box.bottomRight.y

        # Pass the rowRedDot1 elements as key value pairs to append() function
        # self.__df = self.__df.append(rowRedDot1, ignore_index=True)
        # self.__df = self.__df.append(rowRedDot2, ignore_index=True)

        self.__df = DataframeWrapper.append_to_df(self.__df, rowRedDot1)
        self.__df = DataframeWrapper.append_to_df(self.__df, rowRedDot2)

        manual_filepath = self.__folderStruct.getRedDotsManualFilepath()
        self.__saveManualDFToFile(manual_filepath)

    def __saveManualDFToFile(self, filepath):
        # type: (str) -> None
        self.__df.to_csv(filepath, sep='\t', index=False)

    def combine_with_raw_data(self, redDotsRawData):
        # type: (RedDotsRawData) -> pd.DataFrame

        manualDF = self.getPandasDF().copy()
        rawDF = redDotsRawData.getPandasDF().copy()

        rawDF['origin'] = "raw"
        manualDF['origin'] = "manual"

        combinedDF = self.__joinWithoutDuplicates(rawDF, manualDF)

        combinedDF.reset_index(drop=True)
        combinedDF.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)

        return combinedDF

    def __joinWithoutDuplicates(self, rawDF, manualDF):
        if manualDF.count()[0] <= 0:
            return rawDF

        if rawDF.count()[0] <= 0:
            return manualDF

        # remove rows from rawDF that appear in manualDF, so that JOIN (concat) does not create duplicate rows
        framesAppearInRawAndManual = rawDF["frameNumber"].isin(manualDF["frameNumber"])
        rawDFWithoutRowsInManualDF = rawDF[framesAppearInRawAndManual == False]
        combinedDF = pd.concat([rawDFWithoutRowsInManualDF, manualDF])
        return combinedDF

    def median_angle(self):
        angle_series = self.__recalculate_column_angle()
        median = angle_series.median()
        if pd.isna(median):
            return None
        return median

    def __recalculate_column_angle(self):
        # type: () -> pd.Series
        df = self.__dotsJoinedOnOneLine()
        yLength_df = (df["centerPoint_y_dot1"] - df["centerPoint_y_dot2"])
        xLength_df = (df["centerPoint_x_dot1"] - df["centerPoint_x_dot2"])
        angle_in_radians = np.arctan(yLength_df / xLength_df)*(-1)
        return (angle_in_radians / math.pi * 90)

    def __dotsJoinedOnOneLine(self):
        # type: () -> pd.DataFrame
        dataRedDot1 = self.__onlyRedDot1()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]
        dataRedDot2 = self.__onlyRedDot2()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]

        dfToPlot = pd.merge(dataRedDot1, dataRedDot2, on=self.__COLNAME_frameNumber, how='outer', suffixes=('_dot1', '_dot2'))

        return dfToPlot.sort_values(by=[self.__COLNAME_frameNumber])

    def __onlyRedDot1(self):
        # type: () -> pd.DataFrame
        return self.getPandasDF().loc[self.getPandasDF()[self.__COLNAME_dotName] == self.__VALUE_redDot1]

    def __onlyRedDot2(self):
        # type: () -> pd.DataFrame
        return self.getPandasDF().loc[self.getPandasDF()[self.__COLNAME_dotName] == self.__VALUE_redDot2]
