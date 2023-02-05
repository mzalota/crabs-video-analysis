import os
import sys
import cv2
from easygui import fileopenbox

from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point
from lib.infra.MyTimer import MyTimer
from lib.seefloor.InterpolateController import InterpolateController
from lib.ui.ScientistUI import ScientistUI
from lib.ui.StreamToLogger import StreamToLogger

print("Launched markCrabs script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    # rootDir = "C:/data/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"

    path = fileopenbox(title="Select AVI video file", default="*.avi")
    print("Selected file is: ", path)

    rootDir = os.path.dirname(path)
    filename = os.path.basename(path)
    fileparts = filename.split(".")
    videoFileName = fileparts[0]

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())
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
