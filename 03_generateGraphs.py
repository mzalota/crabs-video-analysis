import sys

from lib.imageProcessing.Camera import Camera
from lib.infra.CommandLineLauncher import CommandLineLauncher
from lib.VideoStream import VideoStream
from lib.infra.MyTimer import MyTimer
from lib.ui.FileOpenUI import FileOpenUI
from lib.infra.FolderStructure import FolderStructure
from lib.infra.Configurations import Configurations
from lib.seefloor.InterpolateController import InterpolateController

print ("Launched Generate Graphs script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    # rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"

    show_file_select = FileOpenUI()
    rootDir = show_file_select.root_dir()
    videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)

# StreamToLogger(folderStruct.getLogFilepath())
print("Starting to Generate Graphs")

#Create _config.txt file if it does not exist
configs = Configurations(folderStruct)

Camera.initialize(VideoStream(folderStruct.getVideoFilepath()))


timer = MyTimer("InterpolateController")

controller = InterpolateController(folderStruct)

controller.regenerateSeefloor()
timer.lap("Regenerated/reinterpolated Seefloor.csv")

controller.regenerateGraphs()
timer.lap("regenerated graphs")

print("Done generating graphs")
print("Dir: "+rootDir+", file "+videoFileName)