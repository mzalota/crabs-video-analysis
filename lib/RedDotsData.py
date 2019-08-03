import math
import pandas as pd

from lib.common import Vector


class RedDotsData:
    #__driftData = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_dotName = "dotName"
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"
    __COLNAME_topLeft_y = "topLeft_y"
    __COLNAME_bottot_x = "topLeft_x"
    __COLNAME_topLefmRight_x = "bottomRight_x"
    __COLNAME_bottomRight_y = "bottomRight_x"
    __COLNAME_diagonal = "diagonal"

    __VALUE_redDot1 = "redDot1"
    __VALUE_redDot2 = "redDot2"

    @staticmethod
    def createFromFile(filepath):
        # type: (String) -> RedDotsData
        dfRaw = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
        #dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum
        return RedDotsData.createFromPandasDataFrame(dfRaw)

    @staticmethod
    def createFromPandasDataFrame(df):
        # type: (pd) -> RedDotsData
        newObj = RedDotsData()
        newObj.__driftData = df
        return newObj

    def sort(self):
        self.__driftData.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)

    def replaceOutlierBetweenTwo(self):
        dataRedDot2 = self.onlyRedDot2()
        self.__replaceOutlierBetweenTwo(dataRedDot2, "centerPoint_x")
        self.__replaceOutlierBetweenTwo(dataRedDot2, "centerPoint_y")

        dataRedDot1 = self.onlyRedDot1()
        self.__replaceOutlierBetweenTwo(dataRedDot1, "centerPoint_x")
        self.__replaceOutlierBetweenTwo(dataRedDot1, "centerPoint_y")

        self.__driftData = pd.concat([dataRedDot1, dataRedDot2], ignore_index=True)

        #return dataRedDot2

    def onlyRedDot2(self):
        # type: () -> pd
        dataRedDot2 = self.__driftData.loc[self.__driftData['dotName'] == self.__VALUE_redDot2]
        return dataRedDot2

    def onlyRedDot1(self):
        # type: () -> pd
        return self.__driftData.loc[self.__driftData['dotName'] == self.__VALUE_redDot1]

    def __replaceOutlierBetweenTwo(self, df, columnName):
        outlier_threshold = 100
        prevValue = df[columnName].shift(periods=1)
        nextValue = df[columnName].shift(periods=-1)
        diffNextPrev = abs(prevValue - nextValue)
        meanPrevNext = (prevValue + nextValue) / 2
        deviation = abs(df[columnName] - meanPrevNext)
        single_outlier = (deviation > outlier_threshold) & (diffNextPrev < outlier_threshold)
        df.drop(df[single_outlier].index, inplace=True)

    def getMiddleOfBiggestGap(self):

        redDots1 = self.onlyRedDot1().reset_index()
        idxOfMaxGap1 = self.__indexOfBiggestGap(redDots1)
        print ("idxOfMaxGap1", idxOfMaxGap1)
        gapStartFrameID1 = redDots1.loc[idxOfMaxGap1, :][self.__COLNAME_frameNumber]
        gapEndFrameID1 = redDots1.loc[idxOfMaxGap1 + 1, :][self.__COLNAME_frameNumber]
        gapSize1 = gapEndFrameID1 - gapStartFrameID1

        redDots2 = self.onlyRedDot2().reset_index()
        idxOfMaxGap2 = self.__indexOfBiggestGap(redDots2)
        print ("idxOfMaxGap2", idxOfMaxGap2)
        gapStartFrameID2 = redDots2.loc[idxOfMaxGap2, :][self.__COLNAME_frameNumber]
        gapEndFrameID2 = redDots2.loc[idxOfMaxGap2 + 1, :][self.__COLNAME_frameNumber]
        gapSize2 = gapEndFrameID2 - gapStartFrameID2

        print ("gaps and frames", gapSize1, gapSize2, gapStartFrameID1, gapStartFrameID2)
        if gapSize2 > gapSize1:
            gapMiddleFrameID = gapEndFrameID2 - int(gapSize2/ 2)
        else:
            gapMiddleFrameID = gapEndFrameID1 - int(gapSize1/ 2)

        return gapMiddleFrameID

    def __indexOfBiggestGap(self, newDF):
        nextFrameID = newDF[self.__COLNAME_frameNumber].shift(periods=-1)
        gaps = abs(newDF[self.__COLNAME_frameNumber] - nextFrameID)
        value = max(gaps)
        print ("largest gap size", value)

        #idx = pd.Index(gaps)
        #idxOfMaxGap = idx.get_loc(value)

        #idxOfMaxGap = gaps.index[int(value)].tolist()
        idxOfMaxGap = gaps.idxmax()
        return idxOfMaxGap

    def getCount(self):
        return len(self.__driftData.index)

    def __getXDrift(self, index):
        return self.__driftData[self.__COLNAME_driftX][index]

    def __getYDrift(self, index):
        return self.__driftData[self.__COLNAME_driftY][index]

    def __getFrameID(self, index):
        return self.__driftData[self.__COLNAME_frameNumber][index]

    def minFrameID(self):
        return self.__driftData[self.__COLNAME_frameNumber][0]

    def getIndex(self, frameID):
        foundFrame = self.__driftData.loc[self.__driftData[self.__COLNAME_frameNumber] == frameID]
        if len(foundFrame.index)==1:
            return foundFrame.index[0]
        else:
            return None

    def maxFrameID(self):
        return self.__driftData[self.__COLNAME_frameNumber].max()

    def minFrameID(self):
        return self.__driftData[self.__COLNAME_frameNumber].min()

    def saveToFile(self, filepath):
        self.__driftData.to_csv(filepath, sep='\t', index=False)

    def addManualDots(self, frameID, box):
        #self.__driftData[self.__COLNAME_frameNumber][0]

        rowRedDot1 = {}
        rowRedDot1[self.__COLNAME_frameNumber]=frameID
        rowRedDot1[self.__COLNAME_dotName]=self.__VALUE_redDot1
        rowRedDot1[self.__COLNAME_centerPoint_x] = box.topLeft.x
        rowRedDot1[self.__COLNAME_centerPoint_y] = box.topLeft.y

        rowRedDot2 = {}
        rowRedDot2[self.__COLNAME_frameNumber]=frameID
        rowRedDot2[self.__COLNAME_dotName]=self.__VALUE_redDot2
        rowRedDot2[self.__COLNAME_centerPoint_x] = box.bottomRight.x
        rowRedDot2[self.__COLNAME_centerPoint_y] = box.bottomRight.y

        # Pass the rowRedDot1 elements as key value pairs to append() function
        self.__driftData = self.__driftData.append(rowRedDot1, ignore_index=True)
        self.__driftData = self.__driftData.append(rowRedDot2, ignore_index=True)

    def forPlotting(self):
        dataRedDot1 = self.onlyRedDot1()[[self.__COLNAME_frameNumber,self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]
        dataRedDot2 = self.onlyRedDot2()[[self.__COLNAME_frameNumber,self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]

        dfToPlot = pd.merge(dataRedDot1, dataRedDot2, on='frameNumber', how='outer', suffixes=('_dot1', '_dot2'))
        return dfToPlot.sort_values(by=['frameNumber'])