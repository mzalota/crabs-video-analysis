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
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6692"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6651"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6658"
    #videoFileName = "V4"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.01_6878"
    # videoFileName = "V20200901_215555_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.06_6902"
    # videoFileName = "V20200906_025014_001"

    rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.13_6916"
    videoFileName = "V20200913_204908_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.18_6923"
    # videoFileName = "R_20200918_111643_20200918_112107"



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
        sf.saveGraphDriftsMillimeters()
        sf.saveGraphDriftsPixels()

controller = InterpolateController()
controller.run(folderStruct)

print ("Done inerpolating")