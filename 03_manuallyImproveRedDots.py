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

    #rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
    #videoFileName = "V3__R_20180915_205551"
    #videoFileName = "V4__R_20180915_210447"
    #videoFileName = "V5__R_20180915_211343"
    #videoFileName = "V6__R_20180915_212238"

    #rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
    #videoFileName = "V1_R_20180911_165259"
    #videoFileName = "V2_R_20180911_165730"
    #videoFileName = "V3_R_20180911_170159"

    # rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6236_19"
    # videoFileName = "V1"


    rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    videoFileName = "V3"

    #rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    #videoFileName = "V1"

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())

videoStream = VideoStream(folderStruct.getVideoFilepath())

redDotsManualData = RedDotsManualData(folderStruct)
redDotsUI = RedDotsUI(videoStream)

ui = FillRedDotsGapsUI(redDotsManualData,redDotsUI)
ui.showUI()

cv2.destroyAllWindows()

print ("Done Manually Improving RedDots")
exit()


