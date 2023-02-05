import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.drifts.DetectDriftsController import DetectDriftsController
from lib.FolderStructure import FolderStructure
from lib.ui.FileOpenUI import FileOpenUI
from lib.ui.StreamToLogger import StreamToLogger
from lib.infra.Configurations import Configurations

print ("Launched DetectDrift script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    # rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"

    show_file_select = FileOpenUI()
    rootDir = show_file_select.root_dir()
    videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())

StreamToLogger(folderStruct.getLogFilepath())
print ("Starting DetectDrift")

#Create _config.txt file if it does not exist
configs = Configurations(folderStruct)

controller = DetectDriftsController(folderStruct)
controller.run()

print ("Done DetectDrift")

