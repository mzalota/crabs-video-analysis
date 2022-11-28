import os
import sys

from easygui import easygui

from lib.CommandLineLauncher import CommandLineLauncher
from lib.infra.MyTimer import MyTimer
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

    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    #videoFileName = "V3"
    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"

    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6651"
    # rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6692"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6658"

    #videoFileName = "V4"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.01_6878"
    # videoFileName = "V20200901_215555_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.06_6902"
    # videoFileName = "V20200906_025014_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.13_6916"
    # videoFileName = "V20200913_204908_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    # videoFileName = "R_20200916_194953_20200916_195355"

    path = easygui.fileopenbox()
    print ("selected file is: ", path)

    rootDir = os.path.dirname(path)
    filename = os.path.basename(path)
    fileparts = filename.split(".")
    videoFileName = fileparts[0]

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())
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


