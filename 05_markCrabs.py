import sys
import cv2

from lib.imageProcessing.Camera import Camera
from lib.infra.CommandLineLauncher import CommandLineLauncher
from lib.infra.FolderStructure import FolderStructure
from lib.ui.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.model.Point import Point
from lib.infra.Configurations import Configurations
from lib.infra.MyTimer import MyTimer
from lib.seefloor.InterpolateController import InterpolateController
from lib.ui.FileOpenUI import FileOpenUI
from lib.ui.ScientistUI import ScientistUI

print("Launched markCrabs script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    # rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"
    # videoFileName = "R_20200916_202543_20200916_202941"

    # rootDir = "C:/data/AnjutkaVideo/2019/c6259"
    # videoFileName = "V3"

    show_file_select = FileOpenUI()
    rootDir = show_file_select.root_dir()
    videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)

# StreamToLogger(folderStruct.getLogFilepath())
print("Starting markCrabs script")

#Create _config.txt file if it does not exist
configs = Configurations(folderStruct)

timer = MyTimer("Starting MarkCrabs")

videoStream = VideoStream(folderStruct.getVideoFilepath())
Camera.initialize(videoStream)

interpolator = InterpolateController(folderStruct)
interpolator.regenerateSeefloor()
timer.lap("Interpolated Seefloor")

imageWin = ImageWindow("mainWindow", Point(700, 200))
timer.lap("Initialized ImageWindow")

scientistUI = ScientistUI(imageWin, folderStruct, videoStream)
timer.lap("Initialized ScientistUI")

# Uncomment two lines below to get a nice summary which function uses the most time during execution
# import cProfile
# cProfile.run('scientistUI.processVideo()')

scientistUI.processVideo()

# close all open windows
cv2.destroyAllWindows()

timer.lap("Finished session")
print("Dir: "+rootDir+", file "+videoFileName)
