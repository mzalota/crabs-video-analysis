import cv2

from lib.data.DriftData import DriftData
from lib.ui.ScientistUI import ScientistUI
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point

#rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
#videoFileName = "V3__R_20180915_205551"
#videoFileName = "V4__R_20180915_210447"
#videoFileName = "V5__R_20180915_211343"
#videoFileName = "V6__R_20180915_212238"

#rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
#videoFileName = "V1_R_20180911_165259"
#qvideoFileName = "V2_R_20180911_165730"
#videoFileName = "V3_R_20180911_170159"

#rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6236_19"
#videoFileName = "V1"

rootDir ="C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
videoFileName = "V2"

folderStruct = FolderStructure(rootDir, videoFileName)
#StreamToLogger(folderStruct.getLogFilepath())

videoStream = VideoStream(folderStruct.getVideoFilepath())

driftData = DriftData.createFromFolderStruct(folderStruct)

print("cv2 version", cv2.__version__)

imageWin = ImageWindow("mainWindow", Point(700, 200))

scientistUI = ScientistUI(imageWin, folderStruct, videoStream, driftData)

#Uncomment two lines below to get a nice summary which function uses the most time during excecution
#import cProfile
#cProfile.run('scientistUI.processVideo()')

scientistUI.processVideo()

# close all open windows
cv2.destroyAllWindows()
exit()


