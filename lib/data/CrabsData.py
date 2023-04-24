from __future__ import annotations

import pandas as pd
from datetime import datetime
from lib.FolderStructure import FolderStructure
from lib.common import Point
from lib.data.PandasWrapper import PandasWrapper
from lib.data.SeeFloor import SeeFloor
from lib.data.model import Crab
from lib.infra.DataframeWrapper import DataframeWrapper


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

    @staticmethod
    def _column_names():
        return [CrabsData.__COLNAME_dir,
                CrabsData.__COLNAME_filename,
                CrabsData.__COLNAME_frameNumber,
                CrabsData.__COLNAME_createdOn,
                CrabsData.__COLNAME_crabNumber,
                CrabsData.__COLNAME_crabWidthPixels,
                CrabsData.__COLNAME_crabLocationX,
                CrabsData.__COLNAME_crabLocationY,
                CrabsData.__COLNAME_crabCoordinatePoint,
                CrabsData.__COLNAME_cranbCoordinateBox]

    def __init__(self, df: pd.DataFrame) -> CrabsData:
        self.__crabsDF = df

    @staticmethod
    def createEmpty():
        df = pd.DataFrame(columns=(CrabsData._column_names()))
        return CrabsData(df)

    @staticmethod
    def createFromFolderStruct(folderStruct: FolderStructure) -> CrabsData:
        filepath = folderStruct.getCrabsFilepath()
        if not folderStruct.fileExists(filepath):
            return CrabsData.createEmpty()

        #TODO: find good test cases and then refactor this line into PandasWrapper (readDataFrameFromCSV()) without breaking anything
        crabDF = pd.read_csv(filepath, delimiter="\t", na_values="(null)", header=None, names=(CrabsData._column_names()))

        # drop Header Row
        if (crabDF.iloc[0][0] == 'dir'):
            #we know its a header row because text in first row in first column is "dir"
            crabDF = crabDF[1:]  #.reset_index(drop=True)

        return CrabsData(crabDF)


    # def add_crab_entry(self, frame_number: int, crabCoordinate: Point, folderStruct: FolderStructure):
    def add_crab_entry(self, crab: Crab):
        frame_number = crab.getFrameID()
        crabCoordinate = crab.getBox()
        row_to_append = {self.__COLNAME_dir: "blabla.framesDir",
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

        self.__crabsDF = DataframeWrapper.append_to_df(self.__crabsDF, row_to_append)
        return row_to_append

    def save_file(self, folderStruct: FolderStructure):
        dfObj = DataframeWrapper(self.__crabsDF)
        dfObj.save_file_csv(folderStruct.getCrabsFilepath())

    def getCount(self):
        return len(self.__crabsDF.index)

    def getPandasDF(self):
        # type: () -> pd.DataFrame
        return self.__crabsDF

    def allFramesWithCrabs(self):
        # type: () -> list(int)
        crabsDF = self.getPandasDF()
        frames = crabsDF[self.__COLNAME_frameNumber].astype(int)
        cleanFrames = frames.drop_duplicates().sort_values()
        return cleanFrames.values.tolist()

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

    def generate_crabs_on_seefloor(self, sf):
        # type: (SeeFloor) -> DataframeWrapper
        seed_df = self.getPandasDF()[["frameNumber", "crabWidthPixels", "crabLocationX", "crabLocationY"]]

        result_rows = list()
        for markedCrab in DataframeWrapper(seed_df).to_dict():
            new_row = self.__build_new_crab_row(markedCrab, sf)
            result_rows.append(new_row)

        return DataframeWrapper(pd.DataFrame(result_rows))

    def __build_new_crab_row(self, markedCrab, sf):
        # type: (Dict, SeeFloor) -> DataframeWrapper
        result = dict()
        frame_id = int(markedCrab['frameNumber'])
        print("frame_id", frame_id)
        crab_width_px = float(markedCrab['crabWidthPixels'])
        print("crab_width_px", crab_width_px)
        mm_per_pixel = sf.getRedDotsData().getMMPerPixel(frame_id)
        print("mm_per_pixel", mm_per_pixel)
        frame_coord_x_px = int(markedCrab['crabLocationX'])
        frame_coord_y_px = int(markedCrab['crabLocationY'])
        print("frame_coord_x_px", frame_coord_x_px)
        print("frame_coord_y_px", frame_coord_y_px)

        frame_coord_y_mm = frame_coord_y_px * mm_per_pixel
        y_coord_mm = sf.getYCoordMMOrigin(frame_id) + frame_coord_y_mm
        frame_coord_x_mm = frame_coord_x_px * mm_per_pixel
        x_coord_mm = sf.getXCoordMMOrigin(frame_id) + frame_coord_x_mm
        print("y_coord_mm", y_coord_mm)
        print("x_coord_mm", x_coord_mm)

        result['frameNumber'] = frame_id
        result['mm_per_px'] = mm_per_pixel
        result['width_px'] = crab_width_px
        result['width_mm'] = crab_width_px * mm_per_pixel
        result['frame_coord_x_px'] = frame_coord_x_px
        result['frame_coord_y_px'] = frame_coord_y_px
        result['seefloor_coord_y_mm'] = y_coord_mm
        result['seefloor_coord_x_mm'] = x_coord_mm
        return result


