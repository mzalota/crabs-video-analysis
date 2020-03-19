import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.StreamToLogger import StreamToLogger
from lib.data.DriftRawData import DriftRawData
from lib.FolderStructure import FolderStructure
from lib.data.DriftData import DriftData
from lib.data.SeeFloor import SeeFloor
from lib.data.RedDotsData import RedDotsData

print ("Starting to interpolate Data")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    # rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
    # videoFileName = "V3__R_20180915_205551"
    # videoFileName = "V4__R_20180915_210447"
    # videoFileName = "V6__R_20180915_212238"

    #rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
    # videoFileName = "V3_R_20180911_170159"
    # videoFileName = "V2_R_20180911_165730"
    #videoFileName = "V1_R_20180911_165259"

    #rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6236_19"
    #videoFileName = "V1"

    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    #videoFileName = "V2"

    rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6236_19"
    videoFileName = "V1"

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())

print ("interpolating DriftData")
rawDrifts = DriftRawData(folderStruct)
df = rawDrifts.interpolate(8)

drifts = DriftData.createFromFolderStruct(folderStruct)
drifts.setDF(df)
drifts.saveToFile(folderStruct.getDriftsFilepath())

print ("interpolating RedDots")
rdd = RedDotsData.createFromFolderStruct(folderStruct)
rdd.saveInterpolatedDFToFile(drifts.minFrameID(), drifts.maxFrameID()+1)

print ("interpolating SeeFloor")

sf = SeeFloor.createFromFolderStruct(folderStruct)
sf.saveToFile()

print ("Done inerpolating")