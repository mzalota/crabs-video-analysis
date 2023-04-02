import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.infra.MyTimer import MyTimer
from lib.ui.FileOpenUI import FileOpenUI
from lib.ui.StreamToLogger import StreamToLogger
from lib.data.RedDotsData import RedDotsData
from lib.FillRedDotsGapsController import FillRedDotsGapsController
from lib.FolderStructure import FolderStructure
from lib.VideoStream import VideoStream
import cv2

from lib.seefloor.InterpolateController import InterpolateController
from lib.ui.RedDotsUI import RedDotsUI

print ("Launched manually Improving RedDots script")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"

    show_file_select = FileOpenUI()
    rootDir = show_file_select.root_dir()
    videoFileName = show_file_select.filename()

    folderStruct = FolderStructure(rootDir, videoFileName)

# StreamToLogger(folderStruct.getLogFilepath())
print ("Starting Manually Improving RedDots")

timer = MyTimer("Starting manuallyImproveRedDots")
videoStream = VideoStream(folderStruct.getVideoFilepath())
timer.lap("Initialized VideoStream")

redDotsData = RedDotsData.createFromFolderStruct(folderStruct)
timer.lap("Initialized redDotsData")

interpolator = InterpolateController(folderStruct)
interpolator.regenerateSeefloor()
timer.lap("Interpolated SeeFloor")

redDotsUI = RedDotsUI(videoStream)
timer.lap("Initialized RedDotsUI")

ui = FillRedDotsGapsController(redDotsData, redDotsUI)
timer.lap("Initialized FillRedDotsGapsController")
ui.showUI()

cv2.destroyAllWindows()
timer.lap("Finished session")

print ("Done Manually Improving RedDots")
exit()


