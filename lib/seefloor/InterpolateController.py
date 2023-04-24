from lib.FolderStructure import FolderStructure
from lib.data.CrabsData import CrabsData
from lib.data.DriftData import DriftData
from lib.drifts.DriftManualData import DriftManualData
from lib.drifts.DriftRawData import DriftRawData
from lib.data.RedDotsData import RedDotsData
from lib.data.SeeFloor import SeeFloor
from lib.infra.Configurations import Configurations


class InterpolateController:
    def __init__(self, folderStruct):
        # type: (FolderStructure) -> InterpolateController
        self.__folderStruct = folderStruct

    def step_size(self):
        configs = Configurations(self.__folderStruct)
        return configs.get_drifts_step_size()

    def regenerateSeefloor(self):
        driftsStepSize = self.step_size()
        print("Using driftsStepSize: " + str(driftsStepSize))

        rawDrifts = DriftRawData(self.__folderStruct)
        min_frame_id = rawDrifts.minFrameID()
        max_frame_id = rawDrifts.maxFrameID() + 1

        print ("regenerating/interpolating RedDots")
        rdd = RedDotsData.createFromFolderStruct(self.__folderStruct)
        rdd.saveInterpolatedDFToFile(min_frame_id, max_frame_id)

        # TODO: extract logic in few rows into a "regenerate drafts" module/class
        print ("regenerating/interpolating Drafts")
        manualDrifts = DriftManualData.createFromFile(self.__folderStruct)

        df = rawDrifts.interpolate(manualDrifts, rdd, driftsStepSize)

        drifts = DriftData.createFromFolderStruct(self.__folderStruct)
        drifts.setDF(df)
        drifts.saveToFile(self.__folderStruct.getDriftsFilepath())

        print ("regenerating SeeFloor")
        sf = SeeFloor.createFromFolderStruct(self.__folderStruct)
        sf.saveToFile()

        print ("regenerating crabs_on_seefloor")
        crabs = CrabsData.createFromFolderStruct(self.__folderStruct)
        crabs_on_seefloor_df = crabs.generate_crabs_on_seefloor(sf)
        crabs_on_seefloor_df.save_file_csv(self.__folderStruct.getCrabsOnSeefloorFilepath())

    def regenerateGraphs(self):
        print ("drawing graphs for RedDots")
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
