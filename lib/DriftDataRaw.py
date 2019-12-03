import numpy
import pandas as pd

from lib.PandasWrapper import PandasWrapper
from lib.FolderStructure import FolderStructure

from lib.PandasWrapper import PandasWrapper


class DriftDataRaw(PandasWrapper):
    #__df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_driftX = 'driftX'
    __COLNAME_driftY = 'driftY'

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> pd.DataFrame
        filepath = folderStruct.getRawDriftsFilepath()
        self.__df = PandasWrapper.readDataFrameFromCSV(filepath)

    def getCount(self):
        # type: () -> int
        return len(self.__df.index)

    def interpolate(self):
        # type: () -> pd.DataFrame

        df = self._replaceInvalidValuesWithNaN(self.__df.copy())

        df = self.__interpolateToHaveEveryFrame(df)

        #TODO: dividiing drift by 2 is not flexible. What if detectDrift step is not 2, but 3 or if it is mixed?
        df["driftX"] = df["driftX"] / 2
        df = df[[self.__COLNAME_frameNumber, self.__COLNAME_driftX, self.__COLNAME_driftY]]
        df["driftY"] = df["driftY"] / 2

        #set drifts in the first row to zero.
        self.setValuesInFirstRowToZeros(df)
        return df

    def setValuesInFirstRowToZeros(self, df):
        df.loc[0, self.__COLNAME_driftX] = 0
        df.loc[0, self.__COLNAME_driftY] = 0

    def _replaceInvalidValuesWithNaN(self, df):
        # type: (pd.DataFrame) -> pd.DataFrame
        df.loc[df['driftY'] == -999, ['driftY', 'driftX']] = numpy.nan
        df.loc[df['driftX'] == -888, ['driftX', 'driftY']] = numpy.nan

        df.loc[df['driftX'] < -20, ['driftX', 'driftY']] = numpy.nan
        df.loc[df['driftX'] > 30, ['driftX', 'driftY']] = numpy.nan

        df.loc[df['driftY'] < -20, ['driftX', 'driftY']] = numpy.nan
        df.loc[df['driftY'] > 130, ['driftX', 'driftY']] = numpy.nan  #80
        return df

    def __interpolateToHaveEveryFrame(self, df):
        # type: (pd.DataFrame) -> pd.DataFrame
        minFrameID = self.minFrameID()
        maxFrameID = self.maxFrameID()
        df = df.set_index("frameNumber")
        arrayOfFrameIDs = numpy.arange(start=minFrameID, stop=maxFrameID, step=1)
        everyFrame = pd.DataFrame(arrayOfFrameIDs, columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        df = df.interpolate(limit_direction='both')
        return df

    def minFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].min()

    def maxFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].max()