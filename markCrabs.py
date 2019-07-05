import logging

import pandas as pd
import cv2

from lib.CrabMarker import CrabMarker, UserWantsToQuitException
from lib.Logger import Logger
from lib.SeeFloorSection import SeeFloorSection
from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.StreamToLogger import StreamToLogger
from lib.VideoStream import VideoStream
from lib.common import Point, Box
import os
from datetime import datetime


# rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"

# videoFileName = "V4__R_20180915_210447"
# videoFileName = "V6__R_20180915_212238"
videoFileName = "V3_R_20180911_170159"
# videoFileName = "V2_R_20180911_165730"

folderStruct = FolderStructure(rootDir, videoFileName)
StreamToLogger(folderStruct.getLogFilepath())


videoStream = VideoStream(folderStruct.getVideoFilepath())


# framesDir = rootDir + "/" + videoFileName + "/seqFrames/"
# outputFilePath = rootDir + "/" + videoFileName + "/" + videoFileName + "_crabs.csv"





def writeCrabsInfoToFile(crabNumber, foundCrabs, logger, crabsDF):
    for crab in foundCrabs:
        crabsDF = crabsDF.append(
            {'dir': framesDir, 'filename': filename, 'frameID': frameID, 'crabNumber': crabNumber,
             'crabWidthPixels': crab.diagonal(),
             'crabLocationX': crab.centerPoint().x, 'crabLocationY': crab.centerPoint().y, 'crabWidthLine': crab},
            ignore_index=True)

        row = list()
        row.append(framesDir)
        row.append(filename)
        row.append(frameID)
        row.append(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
        row.append(crabNumber)
        row.append(crab.diagonal())
        row.append(crab.centerPoint().x)
        row.append(crab.centerPoint().x)
        row.append(str(crab.centerPoint()))
        row.append(str(crab))

        print ("row", row)

        logger.writeToFile(row)


        crabNumber += 1
    return crabNumber


crabsDF = pd.DataFrame(
    columns=['dir', 'filename', 'crabNumber', 'crabWidthPixels', 'crabLocationX', 'crabLocationY', 'crabWidthLine'])
crabNumber = 1

imageWin = ImageWindow("mainWindow", Point(700, 200))
crabMarker = CrabMarker(imageWin,folderStruct,videoStream)

logger = Logger.openInAppendMode(folderStruct.getCrabsFilepath())
framesDir = folderStruct.getFramesDirpath()
for filename in os.listdir(framesDir):
    if not filename.endswith(".jpg"):
        print("Skipping some non JPG file", os.path.join(framesDir, filename))
        continue

    filepath = os.path.join(framesDir, filename)
    image = cv2.imread(filepath)
    frameID = int(filename[5:11])
    # print ("frameStr", frameID)
    try:
        foundCrabs = crabMarker.processImage(image, frameID)
        crabNumber = writeCrabsInfoToFile(crabNumber, foundCrabs, logger, crabsDF)
    except UserWantsToQuitException as error:
        #print repr(error)
        print("User requested to quit on frame: "+ str(frameID))
        break

logger.closeFile()
#crabsDF.to_csv(folderStruct.getCrabsFilepath(), sep='\t')

# close all open windows
cv2.destroyAllWindows()
