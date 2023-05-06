from typing import List

import pandas as pd

class DataframeWrapper:

    def __init__(self, df):
        # type: (pd.DataFrame) -> DataframeWrapper
        self.__df = df

    def save_file_csv(self, filepath):
        # type: (str) -> None
        self.__df.to_csv(filepath, sep='\t', index=False)

    def drop_first_row(self):
        self.__df = self.__df[1:] #.reset_index(drop=True)

    @staticmethod
    def append_to_df(df, row_to_append):
        # type: (pd.DataFrame, Dict) -> pd.DataFrame
        return pd.concat([df, pd.DataFrame([row_to_append])])

    # example of the output of this to_dict() function
    # [{'crabLocationX': 221, 'crabLocationY': 368, 'frameNumber': 10026},
    # {'crabLocationX': 865, 'crabLocationY': 304, 'frameNumber': 10243},
    # {'crabLocationX': 101, 'crabLocationY': 420, 'frameNumber': 10530}]
    def to_dict(self) -> List:
        return self.__df.to_dict("records")

    def as_records_dict(self, frame_id_column_name: str):
        list_of_rows = self.to_dict()
        records_by_frame_id = dict()
        for row in list_of_rows:
            frame_id_of_row = row[frame_id_column_name]
            records_by_frame_id[frame_id_of_row] = row

        return records_by_frame_id
