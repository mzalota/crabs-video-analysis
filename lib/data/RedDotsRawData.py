import pandas as pd

from lib.data.PandasWrapper import PandasWrapper


class RedDotsRawData(PandasWrapper):
    # __df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_dotName = "dotName"
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"
    __COLNAME_topLeft_y = "topLeft_y"
    __COLNAME_topLeft_x = "topLeft_x"
    __COLNAME_bottomRight_x = "bottomRight_x"
    __COLNAME_bottomRight_y = "bottomRight_x"
    __COLNAME_diagonal = "diagonal"

    __VALUE_redDot1 = "redDot1"
    __VALUE_redDot2 = "redDot2"

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> RedDotsRawData
        self.__folderStruct = folderStruct
        filepath = folderStruct.getRedDotsRawFilepath()
        self.__df = PandasWrapper.readDataFrameFromCSV(filepath)
        # dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum

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

    @staticmethod
    def headerRow():
        headerRow = []
        headerRow.append("frameNumber")
        headerRow.append("dotName")
        headerRow.append("centerPoint_x")
        headerRow.append("centerPoint_y")
        headerRow.append("topLeft_x")
        headerRow.append("topLeft_y")
        headerRow.append("bottomRight_x")
        headerRow.append("bottomRight_y")
        headerRow.append("diagonal")
        return headerRow