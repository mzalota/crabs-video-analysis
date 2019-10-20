import pandas as pd
from datetime import datetime
from lib.FolderStructure import FolderStructure


class BadFramesData:
    COLNAME_startfFrameNumber = "startfFrameNumber"
    COLNAME_endFrameNumber = 'endFrameNumber'
    COLNAME_createdOn = "createdOn"

    # __df
    # __folderStruct

    def __init__(self, folderStruct, df):
        # type: (FolderStructure, pd) -> object
        self.__folderStruct = folderStruct
        if df is None:
            df = BadFramesData.__create_empty_df()
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

    @staticmethod
    def __create_empty_df():
        # type: () -> pd
        column_names = [BadFramesData.COLNAME_startfFrameNumber,
                        BadFramesData.COLNAME_endFrameNumber,
                        BadFramesData.COLNAME_createdOn]
        return pd.DataFrame(columns=column_names)

    def add_badframes(self, start_frame_id, end_frame_id):
        row_to_append = dict()
        row_to_append[self.COLNAME_startfFrameNumber] = start_frame_id
        row_to_append[self.COLNAME_endFrameNumber] = end_frame_id
        row_to_append[self.COLNAME_createdOn] = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        self.__df = self.__df.append(row_to_append, ignore_index=True)
        return row_to_append

    def save_to_file(self):
        filepath_badframes = self.__folderStruct.getBadFramesFilepath()
        self.__df.to_csv(filepath_badframes, sep='\t', index=False)

    def getCount(self):
        return len(self.__df.index)

    def getPandasDF(self):
        return self.__df

    def is_bad_frame(self, frame_id):
        result_df = self.__rows_containing(frame_id)
        if len(result_df.index) <= 0:
            return False
        else:
            return True

    def __rows_containing(self, frame_id):
        result_df = self.__df.loc[(self.__df[self.COLNAME_startfFrameNumber] <= frame_id) & (
                    self.__df[self.COLNAME_endFrameNumber] >= frame_id)]
        return result_df

    def firstGoodFrameBefore(self, frame_id):
        if not self.is_bad_frame(frame_id):
            return frame_id

        smaller_bad_frame = self.__get_bad_frame_below(frame_id)

        #maybe "smaller_bad_frame" is a good frame. If not then search for frames below smaller_bad_frame to find the first good one.
        frame_below = smaller_bad_frame-1

        # hopefully frame below "smaller_bad_frame" is a good frame. But we are not sure because entries in badframes.csv could be overlapping and nested
        # Call firstGoodFrameBefore recursively till we are sure to find a good frame
        return self.firstGoodFrameBefore(frame_below)

    def firstGoodFrameAfter(self, frame_id):
        if not self.is_bad_frame(frame_id):
            return frame_id

        larger_bad_frame = self.__get_bad_frame_above(frame_id)

        frame_above = larger_bad_frame + 1
        # hopefully frame above "larger_bad_frame" is a good frame. but we are not sure because entries in badframes.csv could be overlapping and nested
        # Call firstGoodFrameAfter recursively till we are sure to find a good frame
        return self.firstGoodFrameAfter(frame_above)

    def __get_bad_frame_below(self, frame_id):
        result_df = self.__rows_containing(frame_id)
        if len(result_df.index)<=0:
            # frame_id is a good one. It cannot be found in any of the ranges in badframes.csv
            return None

        # possibly more than one row in badframes.csv contains frame_id.
        # Select row with minimum value in startFrameNumer column and return that value
        return int(result_df[self.COLNAME_startfFrameNumber].min())

    def __get_bad_frame_above(self, frame_id):
        result_df = self.__rows_containing(frame_id)
        if len(result_df.index) <= 0:
            # frame_id is a good one. It cannot be found in any of the ranges in badframes.csv
            return None

        #possibly more than one row in badframes.csv contains frame_id.
        # Select row with maximum value in endFrameNumber column and return that value
        return int(result_df[self.COLNAME_endFrameNumber].max())

    def firstBadFrameAfter(self, frame_id):
        if self.is_bad_frame(frame_id):
            return frame_id
        result_df = self.__df.loc[(self.__df[self.COLNAME_startfFrameNumber] > frame_id)]
        if len(result_df.index) <= 0:
            # frame_id is a good one. It cannot be found in any of the ranges in badframes.csv
            return frame_id
        return int(result_df[self.COLNAME_startfFrameNumber].min())


    def firstBadFrameBefore(self, frame_id):
        if self.is_bad_frame(frame_id):
            return frame_id
        result_df = self.__df.loc[(self.__df[self.COLNAME_endFrameNumber] < frame_id)]
        if len(result_df.index) <= 0:
            # frame_id is a good one. It cannot be found in any of the ranges in badframes.csv
            return frame_id
        return int(result_df[self.COLNAME_endFrameNumber].max())