from lib.FolderStructure import FolderStructure
from lib.data.DriftData import DriftData
from lib.data.DriftManualData import DriftManualData
from lib.data.DriftRawData import DriftRawData
from lib.data.RedDotsData import RedDotsData
from lib.data.SeeFloor import SeeFloor


class InterpolateController:
    def __init__(self,folderStruct):
        # type: (FolderStructure) -> InterpolateController
        self.__folderStruct = folderStruct

    def regenerateSeefloor(self):
        driftsStepSize = 2
        print ("interpolating DriftData. driftsStepSize: ", driftsStepSize)
        manualDrifts = DriftManualData.createFromFile(self.__folderStruct)

        rawDrifts = DriftRawData(self.__folderStruct)
        df = rawDrifts.interpolate(manualDrifts, driftsStepSize)

        # df = manualDrifts.overwrite_values(df)
        # df = df.interpolate(limit_direction='both')

        drifts = DriftData.createFromFolderStruct(self.__folderStruct)
        drifts.setDF(df)
        drifts.saveToFile(self.__folderStruct.getDriftsFilepath())

        print ("interpolating RedDots")
        rdd = RedDotsData.createFromFolderStruct(self.__folderStruct)
        rdd.saveInterpolatedDFToFile(drifts.minFrameID(), drifts.maxFrameID()+1)

        print ("interpolating SeeFloor")
        sf = SeeFloor.createFromFolderStruct(self.__folderStruct)
        sf.saveToFile()

    def regenerateGraphs(self):
        print ("drawign graphs for RedDots")
        rdd = RedDotsData.createFromFolderStruct(self.__folderStruct)
        rdd.saveGraphOfAngle()
        rdd.saveGraphOfDistance()

        print ("drawing graphs for SeeFloor")
        sf = SeeFloor.createFromFolderStruct(self.__folderStruct)
        sf.saveGraphSeefloorY()
        sf.saveGraphSeefloorX()
        sf.saveGraphSeefloorXY()
        sf.saveGraphDriftsMillimeters()
        sf.saveGraphDriftsPixels()