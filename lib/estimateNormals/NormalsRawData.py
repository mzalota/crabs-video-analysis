import pandas as pd

from lib.infra.FolderStructure import FolderStructure
from lib.infra.Logger import Logger
from lib.data.PandasWrapper import PandasWrapper

class NormalsRawData(PandasWrapper):

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> NormalsRawData
        self.__folderStruct = folderStruct
        self.__logger = None

    @staticmethod
    def createFromCSVFile(folderStruct):
        # type: (FolderStructure) -> RedDotsRawData

        filepath = folderStruct.getRawNormalsFilepath()
        if not folderStruct.fileExists(filepath):
            return NormalsRawData.createNewAndReplaceExistingCSVFile(folderStruct)

        newObj = NormalsRawData(folderStruct)
        # dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum
        newObj.__df = PandasWrapper.readDataFrameFromCSV(filepath)
        return newObj

    @staticmethod
    def createNewAndReplaceExistingCSVFile(folderStruct):
        # type: (FolderStructure) -> NormalsRawData
        column_names = NormalsRawData.headerRow()
        newObj = NormalsRawData(folderStruct)
        newObj.__df = pd.DataFrame(columns=column_names)
        newObj.__saveDFToFile()
        return newObj

    def __saveDFToFile(self):
        filepath = self.__folderStruct.getRawNormalsFilepath()
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
            self.__logger = Logger.openInAppendMode(self.__folderStruct.getRawNormalsFilepath())

        return self.__logger

    def addXcomponent(self, frame_id, xComponent):
         # type: (int, NormalComponent) -> None
        self.__addRedDotEntryToLogger(frame_id, "redDot1", redDot1)       

    def addRedDot1(self, frame_id, redDot1):
        # type: (int, RedNormalComponentDot) -> None
        self.__addRedDotEntryToLogger(frame_id, "redDot1", redDot1)

    def addRedDot2(self, NormalComponent, redDot2):
        # type: (int, RedDot) -> None
        self.__addRedDotEntryToLogger(frame_id, "redDot2", redDot2)

    def __addNormalComponentEntryToLogger(self, frame_id, normalComponent):
        # type: (int, NormalComponent, Logger) -> None
        row = normalComponent.infoAboutDot()
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
        headerRow.append("xComponent")
        headerRow.append("yComponent")
        headerRow.append("zComponent")

        return headerRow