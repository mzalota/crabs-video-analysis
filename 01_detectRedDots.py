import sys
import cv2

from RedDotsController import RedDotsController
from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure

from lib.StreamToLogger import StreamToLogger


#https://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/

print ("Starting to detect RedDots")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:
    # rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    # videoFileName = "V3"

    rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    videoFileName = "V4"

    # rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6236_19"
    # videoFileName = "V1"

    # rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    # videoFileName = "V2"

    # rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
    # videoFileName = "V3__R_20180915_205551"
    # videoFileName = "V4__R_20180915_210447"
    # videoFileName = "V5__R_20180915_211343"
    # videoFileName = "V6__R_20180915_212238"

    # rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
    # videoFileName = "V1_R_20180911_165259"
    # videoFileName = "V2_R_20180911_165730"
    # videoFileName = "V3_R_20180911_170159"

    folderStruct = FolderStructure(rootDir, videoFileName)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getRedDotsRawFilepath())


StreamToLogger(folderStruct.getLogFilepath())

controller = RedDotsController()
controller.run(folderStruct)

print ("Done detecting RedDots")

