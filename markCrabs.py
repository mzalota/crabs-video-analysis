import logging

import pandas as pd
import cv2

from lib.DriftData import DriftData
from lib.Logger import Logger
from lib.ScientistUI import ScientistUI, UserWantsToQuitException
from lib.FolderStructure import FolderStructure
from lib.ImageWindow import ImageWindow
from lib.StreamToLogger import StreamToLogger
from lib.VideoStream import VideoStream
from lib.common import Point
import os
from datetime import datetime



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


# framesDir = rootDir + "/" + videoFileName + "/seqFrames/"
# outputFilePath = rootDir + "/" + videoFileName + "/" + videoFileName + "_crabs.csv"

def writeCrabsInfoToFile(foundCrabs, logger, crabsDF):
    for crabTuple in foundCrabs:
        crabNumber = crabTuple[0]
        frameID = crabTuple[1]
        crabCoordinate = crabTuple[2]
        crabsDF = crabsDF.append(
            {'dir': framesDir, 'filename': filename, 'frameID': frameID, 'crabNumber': crabNumber,
             'crabWidthPixels': crabCoordinate.diagonal(),
             'crabLocationX': crabCoordinate.centerPoint().x, 'crabLocationY': crabCoordinate.centerPoint().y, 'crabWidthLine': crabCoordinate},
            ignore_index=True)

        row = list()
        row.append(framesDir)
        row.append(filename)
        row.append(frameID)
        row.append(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
        row.append(crabNumber)
        row.append(crabCoordinate.diagonal())
        row.append(crabCoordinate.centerPoint().x)
        row.append(crabCoordinate.centerPoint().y)
        row.append(str(crabCoordinate.centerPoint()))
        row.append(str(crabCoordinate))

        print ("row", row)

        logger.writeToFile(row)

        #crabNumber += 1
    #return crabNumber


crabsDF = pd.DataFrame(
    columns=['dir', 'filename', 'crabNumber', 'crabWidthPixels', 'crabLocationX', 'crabLocationY', 'crabWidthLine'])

driftData = DriftData.createFromFile(folderStruct.getDriftsFilepath())

imageWin = ImageWindow("mainWindow", Point(700, 200))
#crabUI = CrabUI(folderStruct, videoStream, driftData)
scientistUI = ScientistUI(imageWin, folderStruct, videoStream, driftData)

logger = Logger.openInAppendMode(folderStruct.getCrabsFilepath())
framesDir = folderStruct.getFramesDirpath()
for filename in os.listdir(framesDir):
    filepath = os.path.join(framesDir, filename)
    if not filename.endswith(".jpg"):
        print("Skipping some non JPG file", filepath)
        continue

    image = cv2.imread(filepath)
    frameID = int(filename[5:11])
    # print ("frameStr", frameID)
    try:
        foundCrabs = scientistUI.processImage(image, frameID)
        writeCrabsInfoToFile(foundCrabs, logger, crabsDF)
    except UserWantsToQuitException as error:
        #print repr(error)
        print("User requested to quit on frame: "+ str(frameID))
        break

logger.closeFile()
#crabsDF.to_csv(folderStruct.getCrabsFilepath(), sep='\t')

# close all open windows
cv2.destroyAllWindows()
