import cv2

from lib.FolderStructure import FolderStructure
from lib.FramesStitcher import FramesStitcher
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point, Box

print(cv2.__version__)

#rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
#videoFileName = "V3__R_20180915_205551"
#videoFileName = "V4__R_20180915_210447"
#videoFileName = "V5__R_20180915_211343"
#videoFileName = "V6__R_20180915_212238"

#rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
#videoFileName = "V1_R_20180911_165259"
#videoFileName = "V2_R_20180911_165730"
#videoFileName = "V3_R_20180911_170159"

rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
videoFileName = "V2"

folderStruct = FolderStructure(rootDir, videoFileName)
videoStream = VideoStream(folderStruct.getVideoFilepath())

framesStitcher = FramesStitcher(folderStruct, videoStream)

#framesToSaveToFile = framesStitcher.determineFrames()
#print("Dataframe Contains:", framesToSaveToFile)

framesStitcher.saveFramesToFile()

