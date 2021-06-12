import sys

import cv2

from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.StreamToLogger import StreamToLogger
from lib.VideoToImages import VideoToImages
from lib.ImageWindow import ImageWindow
from lib.Logger import Logger
from lib.VideoStream import VideoStream
from lib.common import Point, Box
from lib.data.CrabsData import CrabsData
from lib.data.SeeFloor import SeeFloor
from lib.seefloor.InterpolateController import InterpolateController

print(cv2.__version__)

print ("Starting to cut video into frames")

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

    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    #videoFileName = "V2"

    # rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6692"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6651"
    #rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6658"
    # videoFileName = "V4"


    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.01_6878"
    # videoFileName = "V20200901_215555_001"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.13_6916"
    # videoFileName = "V20200913_204908_001"
    # videoFileName = "R_20200913_203053_20200913_203451"

    rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.16_6922"
    videoFileName = "R_20200916_194953_20200916_195355"

    # rootDir = "C:/workspaces/AnjutkaVideo/2020-Kara/2020.09.18_6923"
    # videoFileName = "R_20200918_111643_20200918_112107"

    folderStruct = FolderStructure(rootDir, videoFileName)


StreamToLogger(folderStruct.getLogFilepath())

interpolator = InterpolateController(folderStruct)
interpolator.regenerateSeefloor()

seefloorGeometry = SeeFloor.createFromFolderStruct(folderStruct)
videoStream = VideoStream(folderStruct.getVideoFilepath())

framesStitcher = VideoToImages(seefloorGeometry, videoStream)

#framesToSaveToFile = framesStitcher.determineFrames()
#print("Dataframe Contains:", framesToSaveToFile)

frameIDs = framesStitcher.getListOfFrameIDs()
framesStitcher.saveFramesToFile(frameIDs, folderStruct.getFramesDirpath())

loggerFramesCSV = Logger.openInOverwriteMode(folderStruct.getFramesFilepath())
framesStitcher.saveFramesToCSVFile(frameIDs, loggerFramesCSV)

crabsData = CrabsData(folderStruct)
lst = crabsData.allFramesWithCrabs()
framesStitcher.saveFramesToFile(lst, folderStruct.getCrabFramesDirpath())

print ("Done cutting video into frames")
