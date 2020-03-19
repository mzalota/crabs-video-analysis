import sys
import traceback

import cv2

from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.Image import Image
#from lib.ImageWindow import ImageWindow
from lib.StreamToLogger import StreamToLogger
from lib.VelocityDetector import VelocityDetector
from lib.VideoStream import VideoStream, VideoStreamException

from lib.VelocityDetectorMultiThreaded import VelocityDetectorMultiThreaded
from lib.VideoStreamMultiThreaded import VideoStreamMultiThreaded

from lib.common import Point
from lib.Logger import Logger
from lib.data.DriftRawData import DriftRawData

print ("Starting DetectDrift")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    #rootDirectory = "C:/Users/User/Documents/data/Kara/Video/V_Analysis"
    #rootDirectory = "C:/workspaces/AnjutkaVideo/seeps/c15"

    #rootDirectory = "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
    #rootDirectory = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"

    #videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi'
    #videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi'
    #videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V3_R_20180911_170159.avi'
    #videoFilenameFull = '2018_09_16_St_5994/V3_R_20180916_012323.avi'
    #videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/output_st_v4.mp4'
    #videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi'
    #videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V4__R_20180915_210447.avi'
    #videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V5__R_20180915_211343.avi'
    #videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238.avi'

    #specify filename again
    #videoFilename = "V3_R_20180911_170159"
    #videoFilename = "V3__R_20180915_205551"
    #videoFilename = "V6__R_20180915_212238"
    #videoFilename = "V3_R_20180911_170159"

    #videoFilename = "V20180825_191129_001"

    #rootDirectory ="C:/workspaces/AnjutkaVideo/2019-Kara/St6236_19"
    #videoFilename = "V1"


    rootDirectory ="C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
    videoFilename = "V2"

    folderStruct = FolderStructure(rootDirectory, videoFilename)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())

StreamToLogger(folderStruct.getLogFilepath())

velocityDetector = VelocityDetectorMultiThreaded(folderStruct)
videoStream = VideoStreamMultiThreaded(folderStruct.getVideoFilepath())

velocityDetector = VelocityDetector(folderStruct)
#videoStream = VideoStream(folderStruct.getVideoFilepath())

def newRawFile(folderStruct):
    logger = Logger.openInOverwriteMode(folderStruct.getRawDriftsFilepath())
    driftsFileHeaderRow = VelocityDetector.infoHeaders()
    driftsFileHeaderRow.insert(0, "frameNumber")
    logger.writeToFile(driftsFileHeaderRow)
    return logger


logger = newRawFile(folderStruct)

stepSize = 4

logger = Logger.openInAppendMode(folderStruct.getRawDriftsFilepath())
rawDriftData = DriftRawData(folderStruct)
maxFrameID = rawDriftData.maxFrameID()
if maxFrameID > 1:
    startFrameID = maxFrameID + stepSize
else:
    startFrameID = 5

#cv2.startWindowThread()
#imageWin = ImageWindow("mainWithRedDots", Point(700, 200))


print ("starting processing from frame", startFrameID)

velocityDetector.runLoop(startFrameID, stepSize, logger)

logger.closeFile()
#cv2.destroyAllWindows()

print ("Done DetectDrift")

