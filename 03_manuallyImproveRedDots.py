import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.data.RedDotsData import RedDotsData
from lib.data.RedDotsManualData import RedDotsManualData
from lib.FillRedDotsGapsController import FillRedDotsGapsController
from lib.FolderStructure import FolderStructure
from lib.VideoStream import VideoStream
import cv2
from lib.ui.RedDotsUI import RedDotsUI

print ("Starting Manually Improving RedDots")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    #videoFileName = "V3"

    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6651"
    # rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6692"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6658"
    videoFileName = "V3"

    folderStruct = FolderStructure(rootDir, videoFileName)

#StreamToLogger(folderStruct.getLogFilepath())

videoStream = VideoStream(folderStruct.getVideoFilepath())

redDotsManualData = RedDotsManualData(folderStruct)
redDotsUI = RedDotsUI(videoStream)
redDotsData = RedDotsData(folderStruct)

ui = FillRedDotsGapsController(redDotsData, redDotsUI)
ui.showUI()

cv2.destroyAllWindows()

print ("Done Manually Improving RedDots")
exit()


