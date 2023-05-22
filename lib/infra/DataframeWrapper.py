from typing import List, Dict

import numpy
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

    def pandas_df(self) -> pd.DataFrame:
        return self.__df

    @staticmethod
    def append_to_df(df, row_to_append):
        # type: (pd.DataFrame, Dict) -> pd.DataFrame
        return pd.concat([df, pd.DataFrame([row_to_append])])

    # example of the output of this to_dict() function
    # [{'crabLocationX': 221, 'crabLocationY': 368, 'frameNumber': 10026},
    # {'crabLocationX': 865, 'crabLocationY': 304, 'frameNumber': 10243},
    # {'crabLocationX': 101, 'crabLocationY': 420, 'frameNumber': 10530}]
    def to_list(self) -> List:
        return self.__df.to_dict("records")

    def to_dict(self) -> List:
        return self.__df.to_dict("records")

    def as_records_dict(self, frame_id_column_name: str) -> Dict:
        list_of_rows = self.to_list()
        records_by_frame_id = dict()
        for row in list_of_rows:
            frame_id_of_row = row[frame_id_column_name]
            records_by_frame_id[frame_id_of_row] = row

        return records_by_frame_id

    def remove_outliers_quantile(self, column_name: str, quantile: float = 0.99):
        outlier_up_value = self.__df[column_name].quantile(quantile)
        self.__df.loc[self.__df[column_name] > outlier_up_value, [column_name]] = numpy.nan

        outlier_down_value = self.__df[column_name].quantile(1 - quantile)
        self.__df.loc[self.__df[column_name] < outlier_down_value, [column_name]] = numpy.nan

    def df_print_head(self, num_of_rows=200):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('expand_frame_repr', False)
        print(self.__df.head(num_of_rows))