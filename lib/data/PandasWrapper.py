from lib.MyTimer import MyTimer
import pandas as pd

class PandasWrapper:
    @staticmethod
    def readDataFrameFromCSV(filepath, column_names = None):
        if column_names is not None:
            dfRaw = pd.read_csv(filepath, delimiter="\t", na_values="(null)", names=column_names)
        else:
            dfRaw = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
        return dfRaw