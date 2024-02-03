from lib.infra.FolderStructure import FolderStructure
from lib.data.CrabsData import CrabsData
from lib.drifts_interpolate.DriftInterpolatedData import DriftInterpolatedData
from lib.drifts_detect.DriftManualData import DriftManualData
from lib.drifts_interpolate.DriftRawData import DriftRawData
from lib.reddots_interpolate.RedDotsData import RedDotsData
from lib.seefloor.SeeFloor import SeeFloor
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

        print ("regenerating/interpolating RedDots")
        rdd = RedDotsData.createFromFolderStruct(self.__folderStruct)
        #TODO. get rid of this line. For now I am just calling to initialize pandas_df in RedDotsData
        rdd.getPandasDF()

        # TODO: extract logic in few rows into a "regenerate drafts" module/class
        print ("regenerating/interpolating Drafts")
        manualDrifts = DriftManualData.createFromFile(self.__folderStruct)

        drifts_interpolated_df = rawDrifts.interpolate(manualDrifts, rdd, driftsStepSize)

        drifts = DriftInterpolatedData.createFromFolderStruct(self.__folderStruct)
        drifts.setDF(drifts_interpolated_df)
        drifts.saveToFile(self.__folderStruct.getDriftsFilepath())

        print("regenerating SeeFloor")
        sf = SeeFloor.createFromFolderStruct(self.__folderStruct)
        sf.saveToFile()

        print ("regenerating crabs_on_seefloor")
        crabs = CrabsData.createFromFolderStruct(self.__folderStruct)
        crabs_on_seefloor_df = crabs.generate_crabs_on_seefloor(sf)
        crabs_on_seefloor_df.save_file_csv(self.__folderStruct.getCrabsOnSeefloorFilepath())

    def regenerateGraphs(self):
        print("drawing graphs for RedDots")
        rdd = RedDotsData.createFromFolderStruct(self.__folderStruct)
        # rdd.saveGraphs(13000, 14000)
        # rdd.saveGraphs(1000,1500)
        rdd.saveGraphs()

        print("drawing graphs for SeeFloor")
        sf = SeeFloor.createFromFolderStruct(self.__folderStruct)
        sf.saveGraphForZoomInstananeous()
        sf.saveGraphSeefloorY()
        sf.saveGraphSeefloorX()
        sf.saveGraphSeefloorXY()
        sf.saveGraphDriftsMillimeters()
        sf.saveGraphDriftsPixels()
