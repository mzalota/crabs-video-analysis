import math

import numpy
import pandas as pd

from lib.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsRawData import RedDotsRawData


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
            #self.__df = pd.read_csv(manual_filepath, delimiter="\t", na_values="(null)")
        else:
            self.__df = pd.DataFrame(columns=column_names)
            self.__saveManualDFToFile()

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
        #self.__driftData[self.__COLNAME_frameNumber][0]

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
        self.__df = self.__df.append(rowRedDot1, ignore_index=True)
        self.__df = self.__df.append(rowRedDot2, ignore_index=True)
        self.__saveManualDFToFile()

    def __saveManualDFToFile(self):
        filepath = self.__folderStruct.getRedDotsManualFilepath()
        self.__df.to_csv(filepath, sep='\t', index=False)


    def combinedDF(self, redDotsRawData):
        # type: () -> pd.DataFrame

        manualDF = self.getPandasDF().copy()

        #redDotsRawData = RedDotsRawData.createFromCSVFile(self.__folderStruct)
        rawDF = redDotsRawData.getPandasDF().copy()

        rawDF['origin'] = "raw"
        manualDF['origin'] = "manual"

        if manualDF.count()[0] > 0:
            combinedDF = self.__joinWithoutDuplicates(rawDF, manualDF)
        else:
            combinedDF = rawDF

        combinedDF.reset_index(drop=True)
        combinedDF.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)

        return combinedDF


    def __joinWithoutDuplicates(self, rawDF, manualDF):
        # remove rows from rawDF that appear in manualDF, so that JOIN (concat) does not create duplicate rows
        framesAppearInRawAndManual = rawDF["frameNumber"].isin(manualDF["frameNumber"])
        rawDFWithoutRowsInManualDF = rawDF[framesAppearInRawAndManual == False]
        combinedDF = pd.concat([rawDFWithoutRowsInManualDF, manualDF])
        return combinedDF


    def __dotsJoinedOnOneLine(self):
        dataRedDot1 = self.__onlyRedDot1()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]
        dataRedDot2 = self.__onlyRedDot2()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]

        dfToPlot = pd.merge(dataRedDot1, dataRedDot2, on='frameNumber', how='outer', suffixes=('_dot1', '_dot2'))

        return dfToPlot.sort_values(by=['frameNumber'])

    def __onlyRedDot2(self):
        # type: () -> pd
        dataRedDot2 = self.getPandasDF().loc[self.getPandasDF()['dotName'] == self.__VALUE_redDot2]
        return dataRedDot2

    def __onlyRedDot1(self):
        # type: () -> pd
        dataRedDot1 = self.getPandasDF().loc[self.getPandasDF()['dotName'] == self.__VALUE_redDot1]
        return dataRedDot1

    def __recalculate_column_angle(self):
        df = self.__dotsJoinedOnOneLine()

        yLength_df = (df["centerPoint_y_dot1"] - df["centerPoint_y_dot2"])
        xLength_df = (df["centerPoint_x_dot1"] - df["centerPoint_x_dot2"])
        df["angle"] = numpy.arctan(yLength_df / xLength_df) / math.pi * 90

        return df

    def median_angle(self):
        df = self.__recalculate_column_angle()
        median = df["angle"].median()
        if pd.isna(median):
            return None
        return median