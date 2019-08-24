import pandas as pd
import numpy
from datetime import datetime
from lib.FolderStructure import FolderStructure


class CrabsData:

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

        self.__load_dataframe()

    def __load_dataframe(self):
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
        filepath = self.__folderStruct.getCrabsFilepath()
        self.__crabsDF = pd.read_csv(filepath, delimiter="\t", na_values="(null)", header=None, names=column_names)

        self.__drop_header_row()

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