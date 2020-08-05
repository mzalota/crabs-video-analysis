import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.StreamToLogger import StreamToLogger
from lib.data.DriftManualData import DriftManualData
from lib.data.DriftRawData import DriftRawData
from lib.FolderStructure import FolderStructure
from lib.data.DriftData import DriftData
from lib.data.SeeFloor import SeeFloor
from lib.data.RedDotsData import RedDotsData

print ("Starting to interpolate Data")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    #rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    # videoFileName = "V2"

    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6692"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6651"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6658"

    videoFileName = "V7"

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())

class InterpolateController:

    def run(self, folderStruct):
        print ("interpolating DriftData")
        manualDrifts = DriftManualData.createFromFile(folderStruct)

        rawDrifts = DriftRawData(folderStruct)
        driftsStepSize = 2
        df = rawDrifts.interpolate(manualDrifts, driftsStepSize)

        # df = manualDrifts.overwrite_values(df)
        # df = df.interpolate(limit_direction='both')

        drifts = DriftData.createFromFolderStruct(folderStruct)
        drifts.setDF(df)
        drifts.saveToFile(folderStruct.getDriftsFilepath())

        print ("interpolating RedDots")
        rdd = RedDotsData.createFromFolderStruct(folderStruct)
        rdd.saveInterpolatedDFToFile(drifts.minFrameID(), drifts.maxFrameID()+1)
        rdd.saveGraphOfAngle()
        rdd.saveGraphOfDistance()

        print ("interpolating SeeFloor")

        sf = SeeFloor.createFromFolderStruct(folderStruct)
        sf.saveToFile()
        sf.saveGraphSeefloorY()
        sf.saveGraphSeefloorX()
        sf.saveGraphSeefloorXY()
        sf.saveGraphDrifts()

controller = InterpolateController()
controller.run(folderStruct)

print ("Done inerpolating")