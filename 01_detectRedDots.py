import sys

from lib.reddots.DetectRedDotsController import DetectRedDotsController
from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.ui.FileOpenUI import FileOpenUI
from lib.ui.StreamToLogger import StreamToLogger


#https://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/
from lib.infra.Configurations import Configurations

print ("Launched Detect RedDots script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"
    videoFileName = "R_20200916_202543_20200916_202941"

    # show_file_select = FileOpenUI()
    # rootDir = show_file_select.root_dir()
    # videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getRedDotsRawFilepath())

#StreamToLogger(folderStruct.getLogFilepath())
print ("Starting to detect RedDots")


#Create _config.txt file if it does not exist
configs = Configurations(folderStruct)

controller = DetectRedDotsController(folderStruct)
if configs.is_debug():
    controller.run_with_debug_UI()
else:
    controller.run()

print ("Done detecting RedDots")

