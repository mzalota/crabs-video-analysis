import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.drifts.DetectDriftsController import DetectDriftsController
from lib.FolderStructure import FolderStructure
from lib.ui.StreamToLogger import StreamToLogger
from lib.infra.Configurations import Configurations

print ("Launched DetectDrift script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    # rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    # videoFileName = "V3"

    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    #videoFileName = "V4"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.13_6916"
    # videoFileName = "R_20200913_203053_20200913_203451"
    # videoFileName = "R_20200913_203451_20200913_203849"


    #rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    #videoFileName = "R_20200916_194953_20200916_195355"

    rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    videoFileName = "R_20200916_194953_20200916_195355"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.01_6878"
    # videoFileName = "V20200901_214516_001"

    folderStruct = FolderStructure(rootDir, videoFileName)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())

# StreamToLogger(folderStruct.getLogFilepath())
print ("Starting DetectDrift")

#Create _config.txt file if it does not exist
configs = Configurations(folderStruct)

controller = DetectDriftsController(folderStruct)
controller.run()

print ("Done DetectDrift")

