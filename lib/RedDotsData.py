import pandas as pd
import numpy

from lib.FolderStructure import FolderStructure
from lib.PandasWrapper import PandasWrapper
from lib.common import Point


class RedDotsData(PandasWrapper):
    #__rawDF = None
    #__manualDF = None
    #__interpolatedDF = None

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
        #dfRaw = pd.read_csv(filepath, delimiter="\t", na_values="(null)")
        dfRaw = self.readDataFrameFromCSV(filepath)


        self.initializeManualDF(folderStruct)

        # dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum

        self.setRawDataFrame(dfRaw)

    def initializeManualDF(self, folderStruct):
        column_names = [self.__COLNAME_frameNumber, self.__COLNAME_dotName, self.__COLNAME_centerPoint_x, self.__COLNAME_centerPoint_y]

        manual_filepath = folderStruct.getRedDotsManualFilepath()
        if folderStruct.fileExists(manual_filepath):
            self.__manualDF = self.readDataFrameFromCSV(manual_filepath)
            #self.__manualDF = pd.read_csv(manual_filepath, delimiter="\t", na_values="(null)")
        else:
            self.__manualDF = pd.DataFrame(columns=column_names)

    @staticmethod
    def createFromFolderStruct(folderStruct):
        # type: (FolderStructure) -> RedDotsData
        newObj = RedDotsData(folderStruct)
        return newObj

    def setRawDataFrame(self, df):
        # type: (pd) -> NaN
        self.__rawDF = df

    def manualDF(self):
        return self.__manualDF

    def interpolatedDF(self):
        # type: () -> pd
        filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()

        try:
            return self.__interpolatedDF
        except AttributeError:
            # attribute self.__interpolatedDF have not been initialized yet
            self.__interpolatedDF = self.readDataFrameFromCSV(filepath)
            return self.__interpolatedDF


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

    def replaceOutlierBetweenTwo(self):
        dataRedDot2 = self.onlyRedDot2()
        self.__replaceOutlierBetweenTwo(dataRedDot2, "centerPoint_x")
        self.__replaceOutlierBetweenTwo(dataRedDot2, "centerPoint_y")

        newRedDots2 = self.__dropRowsThatAppearInManualDF(dataRedDot2)
        newRedDots2.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)

        dataRedDot1 = self.onlyRedDot1()
        self.__replaceOutlierBetweenTwo(dataRedDot1, "centerPoint_x")
        self.__replaceOutlierBetweenTwo(dataRedDot1, "centerPoint_y")

        newRedDots1 = self.__dropRowsThatAppearInManualDF(dataRedDot1)
        newRedDots1.sort_values(by=[self.__COLNAME_frameNumber, self.__COLNAME_dotName], inplace=True)

        withoutOutliers = pd.concat([newRedDots1, newRedDots2], ignore_index=True)
        #withoutOutliers = withoutOutliers.reset_index()

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
        if self.__manualDF.count()[0] >0:
            combinedDF = pd.concat([self.__rawDF, self.__manualDF]).reset_index(drop=True)
        else:
            #print("manualDF is empty")
            combinedDF = self.__rawDF.copy().reset_index(drop=True)
            combinedDF.reset_index(drop=True)

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



    def midPoint(self, frameId):
        redDot1 = self.getRedDot1(frameId)
        redDot2 = self.getRedDot2(frameId)
        return redDot1.calculateMidpoint(redDot2)

    def getRedDot1(self, frameId):
        # type: (int) -> Point
        dfResult = self.__rowForFrame(frameId)
        x = dfResult["centerPoint_x_dot1"].iloc[0]
        y = dfResult["centerPoint_y_dot1"].iloc[0]
        return Point(int(x),int(y))

    def getRedDot2(self, frameId):
        # type: (int) -> Point
        dfResult = self.__rowForFrame(frameId)
        x = dfResult["centerPoint_x_dot2"].iloc[0]
        y = dfResult["centerPoint_y_dot2"].iloc[0]
        return Point(int(x),int(y))

    def getDistancePixels(self, frameId):
        # type: (int) -> float
        dfResult = self.__rowForFrame(frameId)
        return dfResult["distance"].iloc[0]

    def getMMPerPixel(self, frameId):
        # type: (int) -> float
        dfResult = self.__rowForFrame(frameId)
        return dfResult["mm_per_pixel"].iloc[0]

    def __rowForFrame(self, frameId):
        df = self.interpolatedDF()
        dfResult = df.loc[df[RedDotsData.__COLNAME_frameNumber] == frameId]
        return dfResult

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
        gapStartFrameID1 = redDots1.loc[idxOfMaxGap1, :][self.__COLNAME_frameNumber]
        gapEndFrameID1 = redDots1.loc[idxOfMaxGap1 + 1, :][self.__COLNAME_frameNumber]
        gapSize1 = gapEndFrameID1 - gapStartFrameID1

        redDots2 = self.onlyRedDot2().reset_index()
        idxOfMaxGap2 = self.__indexOfBiggestGap(redDots2)
        gapStartFrameID2 = redDots2.loc[idxOfMaxGap2, :][self.__COLNAME_frameNumber]
        gapEndFrameID2 = redDots2.loc[idxOfMaxGap2 + 1, :][self.__COLNAME_frameNumber]
        gapSize2 = gapEndFrameID2 - gapStartFrameID2

        print ("gaps and frames", gapSize1, gapSize2, gapStartFrameID1, gapStartFrameID2,idxOfMaxGap1, idxOfMaxGap2)
        if gapSize2 > gapSize1:
            gapMiddleFrameID = gapEndFrameID2 - int(gapSize2/ 2)
        else:
            gapMiddleFrameID = gapEndFrameID1 - int(gapSize1/ 2)

        return gapMiddleFrameID

    def __indexOfBiggestGap(self, newDF):
        #nextFrameID = newDF[self.__COLNAME_frameNumber].shift(periods=-1)
        #gaps = abs(newDF[self.__COLNAME_frameNumber] - nextFrameID)
        #value = max(gaps)
        #print ("largest gap size", value)

        #idx = pd.Index(gaps)
        #idxOfMaxGap = idx.get_loc(value)


        #idxOfMaxGap = gaps.idxmax()

        #-----
        #df = newDF.copy()
        #df["nextFrameID"] = newDF[self.__COLNAME_frameNumber].shift(periods=-1)
        #df["gap"] = nextFrameID - newDF[self.__COLNAME_frameNumber]

        df = newDF.copy()

        df["nextFrameID"] = df["frameNumber"].shift(periods=-1)
        df["gap"] = df["nextFrameID"] - df["frameNumber"]
        maxGap = df["gap"].max()
        idxOfMaxGap = df.loc[df['gap'] == maxGap][:1].index[0]
        #print ("idxOfMaxGap", idxOfMaxGap)
        #print(df.loc[df['gap'] == maxGap][:1])
        return idxOfMaxGap

    def getCount(self):
        return len(self.__combinedDF().index)

    def __minFrameIDInRawFile(self):
        return self.__combinedDF()[self.__COLNAME_frameNumber][0]

    def __maxFrameIDInRawFile(self):
        #return self.__combinedDF[self.__COLNAME_frameNumber].max()
        return self.__rawDF[self.__COLNAME_frameNumber].max()

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

    def interpolated(self, minVal=None, maxVal=None):
        if not minVal:
            minVal = self.__minFrameIDInRawFile()
        if not maxVal:
            maxVal = self.__maxFrameIDInRawFile()

        df = self.forPlotting().copy()
        df = df.set_index("frameNumber")

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

    def saveInterpolatedDFToFile(self, minFrameID=None, maxFrameID=None):
        interpolatedDF = self.interpolated(minFrameID, maxFrameID)
        filepath = self.__folderStruct.getRedDotsInterpolatedFilepath()
        interpolatedDF.to_csv(filepath, sep='\t', index=False)
