import pandas as pd
from datetime import datetime
from lib.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper


class MarkersData(PandasWrapper):

    __COLNAME_frameNumber = 'frameNumber'
    __COLNAME_createdOn = "createdOn"
    __COLNAME_markerId = "markerId"
    __COLNAME_crabLocationX = "locationX"
    __COLNAME_crabLocationY = "locationY"


    def __init__(self, folderStruct):
        # type: (FolderStructure) -> MarkersData
        self.__folderStruct = folderStruct
        column_names = [
                        self.__COLNAME_markerId,
                        self.__COLNAME_frameNumber,
                        self.__COLNAME_crabLocationX,
                        self.__COLNAME_crabLocationY,
                        self.__COLNAME_createdOn
                        ]

        self.__load_dataframe(column_names)

    def __load_dataframe(self,column_names):
        filepath = self.__folderStruct.getMarkersFilepath()
        if self.__folderStruct.fileExists(filepath):
            self.__crabsDF = self.readDataFrameFromCSV(filepath, column_names)
            print ("count markers data", self.getCount())
            self.__crabsDF = self.__crabsDF[1:]  # .reset_index(drop=True)
        else:
            self.__crabsDF = pd.DataFrame(columns=column_names)

    def add_mark(self, frame_number, point, marker_id):
        row_to_append = {
                         self.__COLNAME_markerId: marker_id,
                         self.__COLNAME_frameNumber: str(int(frame_number)),
                         self.__COLNAME_crabLocationX: point.x,
                         self.__COLNAME_crabLocationY: point.y,
                         self.__COLNAME_createdOn: datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                         }

        self.__crabsDF = self.__crabsDF.append(row_to_append, ignore_index=True)
        self.__crabsDF.to_csv(self.__folderStruct.getMarkersFilepath(), sep='\t', index=False)

        return row_to_append

    def getCount(self):
        return len(self.__crabsDF.index)

    def getPandasDF(self):
        # type: () -> pd.DataFrame
        return self.__crabsDF

    def allFramesWithMarks(self):
        # type: () -> list(int)
        df = self.getPandasDF()
        frames = df[self.__COLNAME_frameNumber].astype(int)
        cleanFrames = frames.drop_duplicates().sort_values()
        return cleanFrames.values.tolist()

    def marksBetweenFrames(self, lower_frame_id, upper_frame_id):
        # type: (int, int) -> dict
        if self.getCount() <= 0:
            return None

        crabsDF = self.__crabsDF
        crabsDF["frameNumber"] = pd.to_numeric(crabsDF["frameNumber"], errors='coerce')
        #crabsDF["frameNumber"] = crabsDF["frameNumber"].astype('int64')
        crabsDF["markerId"] = crabsDF["markerId"].astype('int64')
        crabsDF["locationX"] = crabsDF["locationX"].astype('int64')
        crabsDF["locationY"] = crabsDF["locationY"].astype('int64')

        tmpDF = crabsDF[(crabsDF['frameNumber'] <= upper_frame_id) & (crabsDF['frameNumber'] >= lower_frame_id)]
        #print ("count in tmpDF", len(tmpDF.index),len(self.__crabsDF))

        #example of the output
        #[{'crabLocationX': 221, 'crabLocationY': 368, 'frameNumber': 10026},
        # {'crabLocationX': 865, 'crabLocationY': 304, 'frameNumber': 10243},
        # {'crabLocationX': 101, 'crabLocationY': 420, 'frameNumber': 10530}]
        return tmpDF[["frameNumber", "locationY", "locationX"]].reset_index(drop=True).to_dict("records")

    def save_to_file(self):
        filepath = self.__folderStruct.getMarkersFilepath()
        self.__crabsDF.to_csv(filepath, sep='\t', index=False)