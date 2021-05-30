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

    @staticmethod
    def empty_df():
        return pd.DataFrame()

    def __propertyInitialized(self, propertyStr):
        print ("__propertyInitialized")
        try:
            getattr(self, propertyStr)
            print ("__propertyInitialized in try")
        except AttributeError:
            print ("__propertyInitialized in AttributeError")
            return False
        else:
            print ("__propertyInitialized in else")
            return True