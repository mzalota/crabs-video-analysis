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