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
    def to_dict(self):
        return self.__df.to_dict("records")

