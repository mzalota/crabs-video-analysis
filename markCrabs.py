import logging


import cv2

from lib.DriftData import DriftData
from lib.Frame import Frame
from lib.Logger import Logger
from lib.ScientistUI import ScientistUI, UserWantsToQuitException
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.StreamToLogger import StreamToLogger
from lib.VideoStream import VideoStream
from lib.common import Point
import os



#rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
#videoFileName = "V3__R_20180915_205551"
#videoFileName = "V4__R_20180915_210447"
#videoFileName = "V5__R_20180915_211343"
#videoFileName = "V6__R_20180915_212238"

rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
videoFileName = "V1_R_20180911_165259"
#videoFileName = "V2_R_20180911_165730"
#videoFileName = "V3_R_20180911_170159"


folderStruct = FolderStructure(rootDir, videoFileName)
StreamToLogger(folderStruct.getLogFilepath())

videoStream = VideoStream(folderStruct.getVideoFilepath())

driftData = DriftData.createFromFile(folderStruct.getDriftsFilepath())

imageWin = ImageWindow("mainWindow", Point(700, 200))

scientistUI = ScientistUI(imageWin, folderStruct, videoStream, driftData)

logger = Logger.openInAppendMode(folderStruct.getCrabsFilepath())

scientistUI.processVideo(logger)

# close all open windows
cv2.destroyAllWindows()
exit()




for filepath in folderStruct.getFramesFilepaths():
    filename = os.path.basename(filepath)
    if not filename.endswith(".jpg"):
        print("Skipping some non JPG file", filepath)
        continue

    image = cv2.imread(filepath)

    frameID = Frame.deconstructFilename(filename)
    try:
         scientistUI.processImage(image, frameID, logger)
    except UserWantsToQuitException as error:
        #print repr(error)
        print("User requested to quit on frame: "+ str(frameID))
        break

logger.closeFile()
#crabsDF.to_csv(folderStruct.getCrabsFilepath(), sep='\t')

