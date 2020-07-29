import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.StreamToLogger import StreamToLogger
from lib.data.RedDotsManualData import RedDotsManualData
from lib.ui.FillRedDotsGapsUI import FillRedDotsGapsUI
from lib.FolderStructure import FolderStructure
from lib.VideoStream import VideoStream
import cv2
from lib.ui.RedDotsUI import RedDotsUI

print ("Starting Manually Improving RedDots")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    #videoFileName = "V3"

    rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    videoFileName = "V12"

    folderStruct = FolderStructure(rootDir, videoFileName)

#StreamToLogger(folderStruct.getLogFilepath())

videoStream = VideoStream(folderStruct.getVideoFilepath())

redDotsManualData = RedDotsManualData(folderStruct)
redDotsUI = RedDotsUI(videoStream)

ui = FillRedDotsGapsUI(redDotsManualData,redDotsUI)
ui.showUI()

cv2.destroyAllWindows()

print ("Done Manually Improving RedDots")
exit()


