import pandas as pd
import numpy
from datetime import datetime
from lib.FolderStructure import FolderStructure
from lib.PandasWrapper import PandasWrapper


class CrabsData(PandasWrapper):

    __COLNAME_dir = "dir"
    __COLNAME_filename = "filename"
    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_createdOn = "createdOn"
    __COLNAME_crabNumber = "crabNumber"
    __COLNAME_crabWidthPixels = "crabWidthPixels"
    __COLNAME_crabLocationX = "crabLocationX"
    __COLNAME_crabLocationY = "crabLocationY"
    __COLNAME_crabCoordinatePoint = "crabCoordinatePoint"
    __COLNAME_cranbCoordinateBox = "cranbCoordinateBox"

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> CrabsData
        self.__folderStruct = folderStruct
        column_names = [self.__COLNAME_dir,
                        self.__COLNAME_filename,
                        self.__COLNAME_frameNumber,
                        self.__COLNAME_createdOn,
                        self.__COLNAME_crabNumber,
                        self.__COLNAME_crabWidthPixels,
                        self.__COLNAME_crabLocationX,
                        self.__COLNAME_crabLocationY,
                        self.__COLNAME_crabCoordinatePoint,
                        self.__COLNAME_cranbCoordinateBox]

        self.__load_dataframe(column_names)

    def __load_dataframe(self,column_names):
        filepath = self.__folderStruct.getCrabsFilepath()

        if self.__folderStruct.fileExists(filepath):

            #TODO: find good test cases and then refactor this line into PandasWrapper without breaking anything
            self.__crabsDF = pd.read_csv(filepath, delimiter="\t", na_values="(null)", header=None, names=column_names)
            #self.__crabsDF = self.readDataFrameFromCSV(filepath, column_names)

            self.__drop_header_row()
        else:
            self.__crabsDF = pd.DataFrame(columns=column_names)

    def __drop_header_row(self):
        if (self.__crabsDF.iloc[0][0] == 'dir'):
            #we know its a header row because text in first row in first column is "dir"
            self.__crabsDF = self.__crabsDF[1:] #.reset_index(drop=True)
        else:
            #first row is not header. Leave it
            pass

    def add_crab_data(self, frame_number, crabCoordinate):
        framesDir = self.__folderStruct.getVideoFilepath()

        row_to_append = {self.__COLNAME_dir: framesDir,
                         self.__COLNAME_filename: "blabla.filename",
                         self.__COLNAME_frameNumber: str(int(frame_number)),
                         self.__COLNAME_createdOn: datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
                         self.__COLNAME_crabNumber: "0",
                         self.__COLNAME_crabWidthPixels: crabCoordinate.diagonal(),
                         self.__COLNAME_crabLocationX: crabCoordinate.centerPoint().x,
                         self.__COLNAME_crabLocationY: crabCoordinate.centerPoint().y,
                         self.__COLNAME_crabCoordinatePoint: str(crabCoordinate.centerPoint()),
                         self.__COLNAME_cranbCoordinateBox: str(crabCoordinate)
                         }

        self.__crabsDF = self.__crabsDF.append(row_to_append, ignore_index=True)
        self.__crabsDF.to_csv(self.__folderStruct.getCrabsFilepath(), sep='\t', index=False)

        return row_to_append

    def getCount(self):
        return len(self.__crabsDF.index)

    def getPandasDF(self):
        return self.__crabsDF

    def crabsBetweenFrames(self, lower_frame_id, upper_frame_id):
        # type: (int, int) -> dict

        crabsDF = self.__crabsDF
        crabsDF["frameNumber"] = pd.to_numeric(crabsDF["frameNumber"], errors='coerce')
        crabsDF["frameNumber"] = crabsDF["frameNumber"].astype('int64')
        crabsDF["crabLocationX"] = crabsDF["crabLocationX"].astype('int64')
        crabsDF["crabLocationY"] = crabsDF["crabLocationY"].astype('int64')
        crabsDF["crabWidthPixels"] = pd.to_numeric(crabsDF["crabWidthPixels"], errors='coerce')

        tmpDF = crabsDF[(crabsDF['frameNumber'] <= upper_frame_id) & (crabsDF['frameNumber'] >= lower_frame_id)]
        #print ("count in tmpDF", len(tmpDF.index),len(self.__crabsDF))

        #example of the output
        #[{'crabLocationX': 221, 'crabLocationY': 368, 'frameNumber': 10026},
        # {'crabLocationX': 865, 'crabLocationY': 304, 'frameNumber': 10243},
        # {'crabLocationX': 101, 'crabLocationY': 420, 'frameNumber': 10530}]
        return tmpDF[["frameNumber", "crabLocationY", "crabLocationX"]].reset_index(drop=True).to_dict("records")
