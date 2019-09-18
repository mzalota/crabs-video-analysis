import pandas as pd
from datetime import datetime
from lib.FolderStructure import FolderStructure


class BadFramesData:
    __COLNAME_startfFrameNumber = "startfFrameNumber"
    __COLNAME_endFrameNumber = 'endFrameNumber'
    __COLNAME_createdOn = "createdOn"

    # __df
    # __folderStruct

    def __init__(self, folderStruct, df):
        # type: (FolderStructure, pd) -> object
        self.__folderStruct = folderStruct
        if df is None:
            df = self.__create_empty_df()
        self.__df = df

    @staticmethod
    def createFromDataFrame(folderStruct, df):
        # type: (pd.DataFrame) -> BadFramesData
        return BadFramesData(folderStruct, df)

    @staticmethod
    def createFromFile(folderStruct):
        # type: (FolderStructure) -> BadFramesData

        filepath_badframes = folderStruct.getBadFramesFilepath()
        if folderStruct.fileExists(filepath_badframes):
            df = pd.read_csv(filepath_badframes, delimiter="\t", na_values="(null)")
        else:
            df = BadFramesData.__create_empty_df()

        newObj = BadFramesData(folderStruct, df)
        return newObj

    def __create_empty_df(self):
        # type: () -> pd
        column_names = [self.__COLNAME_startfFrameNumber,
                        self.__COLNAME_endFrameNumber,
                        self.__COLNAME_createdOn]
        return pd.DataFrame(columns=column_names)

    def add_badframes(self, start_frame_id, end_frame_id):
        row_to_append = dict()
        row_to_append[self.__COLNAME_startfFrameNumber] = start_frame_id
        row_to_append[self.__COLNAME_endFrameNumber] = end_frame_id
        row_to_append[self.__COLNAME_createdOn] = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        self.__df = self.__df.append(row_to_append, ignore_index=True)
        return row_to_append

    def save_to_file(self):
        filepath_badframes = self.__folderStruct.getBadFramesFilepath()
        self.__df.to_csv(filepath_badframes, sep='\t', index=False)

    def getCount(self):
        return len(self.__df.index)

    def getPandasDF(self):
        return self.__df
