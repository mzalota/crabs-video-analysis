import sys

import cv2

from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.VideoToImages import VideoToImages
from lib.ImageWindow import ImageWindow
from lib.Logger import Logger
from lib.VideoStream import VideoStream
from lib.common import Point, Box
from lib.data.CrabsData import CrabsData
from lib.data.SeeFloor import SeeFloor

print(cv2.__version__)

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

    rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    videoFileName = "V2"
    folderStruct = FolderStructure(rootDir, videoFileName)


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

print ("Done")
