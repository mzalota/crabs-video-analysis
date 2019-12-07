from lib.data.PandasWrapper import PandasWrapper


class RedDotsRawData(PandasWrapper):
    # __df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_frameNumber = 'frameNumber'

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> RedDotsRawData
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
