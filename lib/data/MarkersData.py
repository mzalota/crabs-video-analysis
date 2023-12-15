import pandas as pd
from datetime import datetime
from lib.infra.FolderStructure import FolderStructure
from lib.data.PandasWrapper import PandasWrapper
from lib.infra.DataframeWrapper import DataframeWrapper


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
            self.__markersDF = self.readDataFrameFromCSV(filepath, column_names)
            print ("count markers data", self.getCount())
            self.__markersDF = self.__markersDF[1:]  # .reset_index(drop=True)
        else:
            self.__markersDF = pd.DataFrame(columns=column_names)

    def add_mark(self, frame_number, point, marker_id):
        row_to_append = {
                         self.__COLNAME_markerId: marker_id,
                         self.__COLNAME_frameNumber: str(int(frame_number)),
                         self.__COLNAME_crabLocationX: point.x,
                         self.__COLNAME_crabLocationY: point.y,
                         self.__COLNAME_createdOn: datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                         }

        #self.__markersDF = self.__markersDF.append(row_to_append, ignore_index=True)
        self.__markersDF = DataframeWrapper.append_to_df(self.__markersDF, row_to_append)

        #self.__markersDF.to_csv(self.__folderStruct.getMarkersFilepath(), sep='\t', index=False)

        return row_to_append

    def delete_last_mark(self):
        if self.getCount()<=0:
            return

        last_item_idx = self.getCount()-1
        print("removing last marker, index: "+str(last_item_idx))
        self.__markersDF = self.__markersDF.drop([last_item_idx])

    def getCount(self):
        return len(self.__markersDF.index)

    def getPandasDF(self):
        # type: () -> pd.DataFrame
        return self.__markersDF

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

        markersDF = self.__markersDF
        markersDF["frameNumber"] = pd.to_numeric(markersDF["frameNumber"], errors='coerce')
        markersDF["markerId"] = markersDF["markerId"] #.astype('int64')
        markersDF["locationX"] = markersDF["locationX"].astype('int64')
        markersDF["locationY"] = markersDF["locationY"].astype('int64')

        tmpDF = markersDF[(markersDF['frameNumber'] <= upper_frame_id) & (markersDF['frameNumber'] >= lower_frame_id)]
        #print ("count in tmpDF", len(tmpDF.index),len(self.__crabsDF))

        #example of the output
        #[{'crabLocationX': 221, 'crabLocationY': 368, 'frameNumber': 10026},
        # {'crabLocationX': 865, 'crabLocationY': 304, 'frameNumber': 10243},
        # {'crabLocationX': 101, 'crabLocationY': 420, 'frameNumber': 10530}]
        return tmpDF[["frameNumber", "markerId", "locationY", "locationX"]].reset_index(drop=True).to_dict("records")

    def save_to_file(self):
        filepath = self.__folderStruct.getMarkersFilepath()
        self.__markersDF.to_csv(filepath, sep='\t', index=False)