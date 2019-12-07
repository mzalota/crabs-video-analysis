import pandas as pd

from lib.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper
from lib.data.RedDotsRawData import RedDotsRawData


class RedDotsManualData(PandasWrapper):
    # __df = None
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_dotName = "dotName"
    __COLNAME_centerPoint_x = "centerPoint_x"
    __COLNAME_centerPoint_y = "centerPoint_y"

    __VALUE_redDot1 = "redDot1"
    __VALUE_redDot2 = "redDot2"

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> RedDotsManualData
        self.__folderStruct = folderStruct
        self.__initializeManualDF(folderStruct)

    def __initializeManualDF(self, folderStruct):
        column_names = [self.__COLNAME_frameNumber, self.__COLNAME_dotName, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]

        manual_filepath = folderStruct.getRedDotsManualFilepath()
        if folderStruct.fileExists(manual_filepath):
            self.__df = self.readDataFrameFromCSV(manual_filepath)
            #self.__df = pd.read_csv(manual_filepath, delimiter="\t", na_values="(null)")
        else:
            self.__df = pd.DataFrame(columns=column_names)
            self.__saveManualDFToFile()

    def getCount(self):
        # type: () -> int
        return len(self.__df.index)

    def getPandasDF(self):
        # type: () -> pd.DataFrame
        return self.__df

    def __minFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].max() #[0]

    def __maxFrameID(self):
        # type: () -> int
        return self.__df[self.__COLNAME_frameNumber].max()

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
        self.__df = self.__df.append(rowRedDot1, ignore_index=True)
        self.__df = self.__df.append(rowRedDot2, ignore_index=True)
        self.__saveManualDFToFile()

    def __saveManualDFToFile(self):
        filepath = self.__folderStruct.getRedDotsManualFilepath()
        self.__df.to_csv(filepath, sep='\t', index=False)


    def forPlotting(self):
        dataRedDot1 = self.combinedOnlyRedDot1()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]
        dataRedDot2 = self.combinedOnlyRedDot2()[[self.__COLNAME_frameNumber, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]]

        dfToPlot = pd.merge(dataRedDot1, dataRedDot2, on='frameNumber', how='outer', suffixes=('_dot1', '_dot2'))
        return dfToPlot.sort_values(by=['frameNumber'])


    def combinedDF(self):
        # type: () -> pd.DataFrame

        manualDF = self.getPandasDF().copy()

        redDotsRawData = RedDotsRawData(self.__folderStruct)
        rawDF = redDotsRawData.getPandasDF().copy()

        if manualDF.count()[0] > 0:
            combinedDF = self.__joinWithoutDuplicates(rawDF, manualDF)
        else:
            combinedDF = rawDF

        combinedDF.reset_index(drop=True)
        combinedDF.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)

        return combinedDF

    def getMiddleOfBiggestGap(self):
        # type: () -> int

        redDots1 = self.combinedOnlyRedDot1().reset_index()
        idxOfMaxGap1 = self.__indexOfBiggestGap(redDots1)
        gapStartFrameID1 = redDots1.loc[idxOfMaxGap1, :][self.__COLNAME_frameNumber]
        gapEndFrameID1 = redDots1.loc[idxOfMaxGap1 + 1, :][self.__COLNAME_frameNumber]
        gapSize1 = gapEndFrameID1 - gapStartFrameID1

        redDots2 = self.combinedOnlyRedDot2().reset_index()
        idxOfMaxGap2 = self.__indexOfBiggestGap(redDots2)
        gapStartFrameID2 = redDots2.loc[idxOfMaxGap2, :][self.__COLNAME_frameNumber]
        gapEndFrameID2 = redDots2.loc[idxOfMaxGap2 + 1, :][self.__COLNAME_frameNumber]
        gapSize2 = gapEndFrameID2 - gapStartFrameID2

        if gapSize2 > gapSize1:
            gapMiddleFrameID = gapEndFrameID2 - int(gapSize2/ 2)
        else:
            gapMiddleFrameID = gapEndFrameID1 - int(gapSize1/ 2)

        print ("next gapMiddleFrameID", gapMiddleFrameID, "gap1", gapSize1, "gap2", gapSize2, "gapStartFrameID1", gapStartFrameID1, "gapStartFrameID2", gapStartFrameID2, idxOfMaxGap1, idxOfMaxGap2)

        return gapMiddleFrameID

    def __indexOfBiggestGap(self, newDF):
        # type: (pd.DataFrame) -> int
        #nextFrameID = newDF[self.__COLNAME_frameNumber].shift(periods=-1)
        #gaps = abs(newDF[self.__COLNAME_frameNumber] - nextFrameID)
        #value = max(gaps)
        #print ("largest gap size", value)

        #idx = pd.Index(gaps)
        #idxOfMaxGap = idx.get_loc(value)


        #idxOfMaxGap = gaps.idxmax()


        #df = newDF.copy()
        #df["nextFrameID"] = newDF[self.__COLNAME_frameNumber].shift(periods=-1)
        #df["gap"] = nextFrameID - newDF[self.__COLNAME_frameNumber]

        df = newDF.copy()

        df["nextFrameID"] = df["frameNumber"].shift(periods=-1)
        df["gap"] = df["nextFrameID"] - df["frameNumber"]
        maxGap = df["gap"].max()
        idxOfMaxGap = df.loc[df['gap'] == maxGap][:1].index[0]

        return idxOfMaxGap

    def __joinWithoutDuplicates(self, rawDF, manualDF):
        # remove rows from rawDF that appear in manualDF, so that JOIN (concat) does not create duplicate rows
        framesAppearInRawAndManual = rawDF["frameNumber"].isin(manualDF["frameNumber"])
        rawDFWithoutRowsInManualDF = rawDF[framesAppearInRawAndManual == False]
        combinedDF = pd.concat([rawDFWithoutRowsInManualDF, manualDF])
        return combinedDF

    def combinedOnlyRedDot2(self):
        # type: () -> pd
        dataRedDot2 = self.combinedDF().loc[self.combinedDF()['dotName'] == self.__VALUE_redDot2]
        return dataRedDot2

    def combinedOnlyRedDot1(self):
        # type: () -> pd
        dataRedDot1 = self.combinedDF().loc[self.combinedDF()['dotName'] == self.__VALUE_redDot1]
        return dataRedDot1

