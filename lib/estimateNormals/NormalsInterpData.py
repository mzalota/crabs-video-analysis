import pandas as pd

from lib.infra.FolderStructure import FolderStructure
from lib.infra.Logger import Logger
from lib.data.PandasWrapper import PandasWrapper

class NormalsInterpData(PandasWrapper):

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> NormalsInterpData
        self.__folderStruct = folderStruct
        self.__logger = None

    @staticmethod
    def createFromCSVFile(folderStruct):
        # type: (FolderStructure) -> NormalsInterpData

        filepath = folderStruct.getRawNormalsFilepath()
        if not folderStruct.fileExists(filepath):
            return NormalsInterpData.createNewAndReplaceExistingCSVFile(folderStruct)

        newObj = NormalsInterpData(folderStruct)
        # dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum
        newObj.__df = PandasWrapper.readDataFrameFromCSV(filepath)
        return newObj

    @staticmethod
    def createNewAndReplaceExistingCSVFile(folderStruct):
        # type: (FolderStructure) -> NormalsInterpData
        column_names = NormalsInterpData.headerRow()
        newObj = NormalsInterpData(folderStruct)
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

    def __getLogger(self):
        if not self.__logger:
            self.__logger = Logger.openInAppendMode(self.__folderStruct.getInterpolatedNormalsFilepath())

        return self.__logger

    def addNormal(self, frame_id, planeNormal):
         # type: (int, np.ndarray) -> None
        self.__addNormalComponentEntryToLogger(frame_id, planeNormal)       

    def __addNormalComponentEntryToLogger(self, frame_id, planeNormal):
        # type: (int, np.ndarray) -> None
        if planeNormal is not None:
            row = list(planeNormal)
        else:
            row = ['','','']
        row.insert(0, frame_id)
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