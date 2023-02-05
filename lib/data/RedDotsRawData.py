import pandas as pd

from lib.FolderStructure import FolderStructure
from lib.infra.Logger import Logger
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
        self.__logger = None

    @staticmethod
    def createFromCSVFile(folderStruct):
        # type: (FolderStructure) -> RedDotsRawData

        filepath = folderStruct.getRedDotsRawFilepath()
        if not folderStruct.fileExists(filepath):
            return RedDotsRawData.createNewAndReplaceExistingCSVFile(folderStruct)

        newObj = RedDotsRawData(folderStruct)
        # dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum
        newObj.__df = PandasWrapper.readDataFrameFromCSV(filepath)
        return newObj

    @staticmethod
    def createNewAndReplaceExistingCSVFile(folderStruct):
        # type: (FolderStructure) -> RedDotsRawData
        column_names = RedDotsRawData.headerRow()
        newObj = RedDotsRawData(folderStruct)
        newObj.__df = pd.DataFrame(columns=column_names)
        newObj.__saveDFToFile()
        return newObj

    def __saveDFToFile(self):
        filepath = self.__folderStruct.getRedDotsRawFilepath()
        self.__df.to_csv(filepath, sep='\t', index=False)

    def getCount(self):
        # type: () -> int
        return len(self.__df.index)

    def getPandasDF(self):
        # type: () -> pd.DataFrame
        return self.__df

    # def minFrameID(self):
    #     # type: () -> int
    #     return self.__df[self.__COLNAME_frameNumber].max() #[0]
    #
    # def maxFrameID(self):
    #     # type: () -> int
    #     return self.__df[self.__COLNAME_frameNumber].max()

    def __getLogger(self):
        if not self.__logger:
            self.__logger = Logger.openInAppendMode(self.__folderStruct.getRedDotsRawFilepath())

        return self.__logger


    def addRedDot1(self, frame_id, redDot1):
        # type: (int, RedDot) -> None
        self.__addRedDotEntryToLogger(frame_id, "redDot1", redDot1)

    def addRedDot2(self, frame_id, redDot2):
        # type: (int, RedDot) -> None
        self.__addRedDotEntryToLogger(frame_id, "redDot2", redDot2)

    def __addRedDotEntryToLogger(self, frame_id, dotName, redDot):
        # type: (int, RedDot, Logger) -> None
        row = redDot.infoAboutDot()
        row.insert(0, frame_id)
        row.insert(1, dotName)
        self.__getLogger().writeToFile(row)
        print(row)

    def closeOpenFiles(self):
        if self.__logger:
            self.__logger.closeFile()

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