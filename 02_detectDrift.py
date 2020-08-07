import sys
import traceback

from lib.CommandLineLauncher import CommandLineLauncher
from lib.DetectDriftsController import DetectDriftsController
from lib.FolderStructure import FolderStructure
from lib.StreamToLogger import StreamToLogger

print ("Starting DetectDrift")


folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    # rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    # videoFileName = "V3"

    rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    videoFileName = "V4"

    folderStruct = FolderStructure(rootDir, videoFileName)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())

StreamToLogger(folderStruct.getLogFilepath())

controller = DetectDriftsController()
controller.run(folderStruct)

print ("Done DetectDrift")

