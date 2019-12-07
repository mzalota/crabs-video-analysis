import pandas as pd

from lib.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper

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