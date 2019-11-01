import pandas as pd
import cv2

from lib.RedDotsData import RedDotsData
from lib.RedDotsUI import RedDotsUI
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.StreamToLogger import StreamToLogger
from lib.VideoStream import VideoStream
from lib.common import Point, Box
from datetime import datetime


#rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
#videoFileName = "V3__R_20180915_205551"
#videoFileName = "V4__R_20180915_210447"
#videoFileName = "V5__R_20180915_211343"
#videoFileName = "V6__R_20180915_212238"

rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
#videoFileName = "V1_R_20180911_165259"
#videoFileName = "V2_R_20180911_165730"
videoFileName = "V3_R_20180911_170159"

folderStruct = FolderStructure(rootDir, videoFileName)
#StreamToLogger(folderStruct.getLogFilepath())
videoStream = VideoStream(folderStruct.getVideoFilepath())

#imageWin = ImageWindow("mainWithRedDots", Point(700, 200))


ui = RedDotsUI(folderStruct,videoStream)
ui.showUI()

exit()


