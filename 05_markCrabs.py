import sys
import cv2

from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point
from lib.infra.MyTimer import MyTimer
from lib.seefloor.InterpolateController import InterpolateController
from lib.ui.FileOpenUI import FileOpenUI
from lib.ui.ScientistUI import ScientistUI
from lib.ui.StreamToLogger import StreamToLogger

print("Launched markCrabs script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"
    videoFileName = "R_20200916_202543_20200916_202941"

    # show_file_select = FileOpenUI()
    # rootDir = show_file_select.root_dir()
    # videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)

# StreamToLogger(folderStruct.getLogFilepath())
print("Starting markCrabs script")

timer = MyTimer("Starting MarkCrabs")

videoStream = VideoStream(folderStruct.getVideoFilepath())
timer.lap("Initialized VideoStream")

interpolator = InterpolateController(folderStruct)
interpolator.regenerateSeefloor()
timer.lap("Interpolated Seefloor")

imageWin = ImageWindow("mainWindow", Point(700, 200))
timer.lap("Initialized ImageWindow")

scientistUI = ScientistUI(imageWin, folderStruct, videoStream)
timer.lap("Initialized ScientistUI")

# Uncomment two lines below to get a nice summary which function uses the most time during excecution
# import cProfile
# cProfile.run('scientistUI.processVideo()')

scientistUI.processVideo()

# close all open windows
cv2.destroyAllWindows()

timer.lap("Finished session")
