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
    #rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6267_19"
    #videoFileName = "V3"


    rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    videoFileName = "V12"

    folderStruct = FolderStructure(rootDir, videoFileName)
    folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())

#StreamToLogger(folderStruct.getLogFilepath())

#velocityDetector = VelocityDetectorMultiThreaded(folderStruct)
#videoStream = VideoStreamMultiThreaded(folderStruct.getVideoFilepath())

velocityDetector = VelocityDetector(folderStruct)
#videoStream = VideoStream(folderStruct.getVideoFilepath())

def newRawFile(folderStruct):
    logger = Logger.openInOverwriteMode(folderStruct.getRawDriftsFilepath())
    driftsFileHeaderRow = VelocityDetector.infoHeaders()
    driftsFileHeaderRow.insert(0, "frameNumber")
    logger.writeToFile(driftsFileHeaderRow)
    return logger

logger = newRawFile(folderStruct)

stepSize = 2

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

