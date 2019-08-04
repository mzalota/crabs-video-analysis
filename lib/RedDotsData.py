import pandas as pd
import numpy

from lib.DriftData import DriftData
from lib.FolderStructure import FolderStructure


class RedDotsData:
    #__rawDF = None
    #__manualDF = None

    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_dotName = "dotName"
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"
    __COLNAME_topLeft_y = "topLeft_y"
    __COLNAME_topLeft_x = "topLeft_x"
    __COLNAME_bottomRight_x = "bottomRight_x"
    __COLNAME_bottomRight_y = "bottomRight_x"
    __COLNAME_diagonal = "diagonal"

    __COLNAME_mm_per_pixel = "mm_per_pixel"

    __VALUE_redDot1 = "redDot1"
    __VALUE_redDot2 = "redDot2"

    __distance_between_reddots_mm = 300

    def __init__(self, folderStruct):
        self.__folderStruct = folderStruct

        filepath = folderStruct.getRedDotsRawFilepath()
        dfRaw = pd.read_csv(filepath, delimiter="\t", na_values="(null)")

        self.initializeManualDF(folderStruct)

        # dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum

        self.setRawDataFrame(dfRaw)

    def initializeManualDF(self, folderStruct):
        column_names = [self.__COLNAME_frameNumber, self.__COLNAME_dotName, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]

        manual_filepath = folderStruct.getRedDotsManualFilepath()
        if folderStruct.fileExists(manual_filepath):
            self.__manualDF = pd.read_csv(manual_filepath, delimiter="\t", na_values="(null)")
        else:
            self.__manualDF = pd.DataFrame(columns=column_names)

    @staticmethod
    def createFromFile(folderStruct):
        # type: (FolderStructure) -> RedDotsData
        newObj = RedDotsData(folderStruct)
        return newObj

    def setRawDataFrame(self, df):
        # type: (pd) -> NaN
        self.__rawDF = df

    def manualDF(self):
        return self.__manualDF

    def sort(self):
        self.__rawDF.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)

    def replaceOutlierBetweenTwo(self):
        dataRedDot2 = self.onlyRedDot2()
        self.__replaceOutlierBetweenTwo(dataRedDot2, "centerPoint_x")
        self.__replaceOutlierBetweenTwo(dataRedDot2, "centerPoint_y")

        newRedDots2 = self.__dropRowsThatAppearInManualDF(dataRedDot2)

        dataRedDot1 = self.onlyRedDot1()
        self.__replaceOutlierBetweenTwo(dataRedDot1, "centerPoint_x")
        self.__replaceOutlierBetweenTwo(dataRedDot1, "centerPoint_y")

        newRedDots1 = self.__dropRowsThatAppearInManualDF(dataRedDot1)

        withoutOutliers = pd.concat([newRedDots1, newRedDots2], ignore_index=True)

        self.__saveRawDFToFile(withoutOutliers)

    def __dropRowsThatAppearInManualDF(self, df):

        # remove rows from
        tmp2 = pd.merge(df[['frameNumber', "dotName"]], self.__manualDF[['frameNumber', "dotName"]],
                        on='frameNumber',
                        how='left', suffixes=('_all', '_man'))
        toDrop2 = tmp2[tmp2['dotName_man'].notnull()]

        #ingnore errors, because there are rows in manualDF that are not in DF and they generate unnecessary error/warning
        return df.drop(toDrop2.index, errors="ignore")

    def __combinedDF(self):
        combinedDF = pd.concat([self.__rawDF, self.__manualDF]).reset_index()
        combinedDF.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)
        return combinedDF

    def onlyRedDot2(self):
        # type: () -> pd
        dataRedDot2 = self.__combinedDF().loc[self.__combinedDF()['dotName'] == self.__VALUE_redDot2]
        return dataRedDot2

    def onlyRedDot1(self):
        # type: () -> pd
        dataRedDot1 = self.__combinedDF().loc[self.__combinedDF()['dotName'] == self.__VALUE_redDot1]
        return dataRedDot1

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
        return len(self.__combinedDF().index)

    def minFrameID(self):
        return self.__combinedDF()[self.__COLNAME_frameNumber][0]

    def maxFrameID(self):
        drifts = DriftData.createFromFile(self.__folderStruct.getDriftsFilepath())
        return drifts.maxFrameID()
        #return self.__rawDF[self.__COLNAME_frameNumber].max()

    def minFrameID(self):
        drifts = DriftData.createFromFile(self.__folderStruct.getDriftsFilepath())
        return drifts.minFrameID()

        #return self.__rawDF[self.__COLNAME_frameNumber].min()

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
        self.__manualDF = self.__manualDF.append(rowRedDot1, ignore_index=True)
        self.__manualDF = self.__manualDF.append(rowRedDot2, ignore_index=True)
        self.__saveManualDFToFile()

    def forPlotting(self):
        dataRedDot1 = self.onlyRedDot1()[[self.__COLNAME_frameNumber,self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]
        dataRedDot2 = self.onlyRedDot2()[[self.__COLNAME_frameNumber,self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]

        dfToPlot = pd.merge(dataRedDot1, dataRedDot2, on='frameNumber', how='outer', suffixes=('_dot1', '_dot2'))
        return dfToPlot.sort_values(by=['frameNumber'])

    def interpolated(self):
        df = self.forPlotting().copy()
        df = df.set_index("frameNumber")

        minVal = self.minFrameID()
        maxVal = self.maxFrameID()
        everyFrame = pd.DataFrame(numpy.arange(start=minVal, stop=maxVal, step=1), columns=["frameNumber"]).set_index("frameNumber")
        df = df.combine_first(everyFrame).reset_index()
        df = df.interpolate(limit_direction = 'both')
        df['distance'] = pow(pow(df["centerPoint_x_dot2"] - df["centerPoint_x_dot1"], 2) + pow(df["centerPoint_y_dot2"] - df["centerPoint_y_dot1"], 2), 0.5) #.astype(int)

        df[self.__COLNAME_mm_per_pixel] = self.__distance_between_reddots_mm/df['distance']
        return df

    def __saveManualDFToFile(self):
        filepath = self.__folderStruct.getRedDotsManualFilepath()
        self.__manualDF.to_csv(filepath, sep='\t', index=False)

    def __saveRawDFToFile(self, withoutOutliersDF):
        filepath = self.__folderStruct.getRedDotsRawFilepath()
        withoutOutliersDF.to_csv(filepath, sep='\t', index=False)

    def saveInterpolatedDFToFile(self):
        interpolatedDF = self.interpolated()
        filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
        interpolatedDF.to_csv(filepath, sep='\t', index=False)
