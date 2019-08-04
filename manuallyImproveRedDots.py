import logging

import pandas as pd
import cv2

from lib.DriftData import DriftData
from lib.Frame import Frame
from lib.Logger import Logger
from lib.RedDotsData import RedDotsData
from lib.ScientistUI import ScientistUI, UserWantsToQuitException
from lib.FolderStructure import FolderStructure
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
#videoFileName = "V3_R_20180911_170159"
videoFileName = "V2_R_20180911_165730"
# videoFileName = "V2_R_20180911_165730"

folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())

videoStream = VideoStream(folderStruct.getVideoFilepath())

redDotsData = RedDotsData.createFromFile(folderStruct.getRedDotsFilepath())

imageWin = ImageWindow("mainWithRedDots", Point(700, 200))
imageZoomWin = ImageWindow("zoomImg", Point(100, 100))
zoomBox = Box(Point(800, 400), Point(1300, 700))

redDotsData.sort()
frameID = redDotsData.getMiddleOfBiggestGap()

mustExit = False
while not mustExit:
    #keyPressed = self.__imageWin.showWindowAndWaitForClick(image)
    print ("frame", frameID)

    image = videoStream.readImageObj(frameID)
    image.drawFrameID(frameID)
    frame = Frame(frameID, videoStream)

    # print ("pressed button", keyPressed)
    imageWin.showWindow(image.asNumpyArray())

    zoomImage = image.subImage(zoomBox)
    zoomImage.drawFrameID(frameID)

    keyPressed = imageZoomWin.showWindowAndWaitForTwoClicks(zoomImage.asNumpyArray())

    if keyPressed == ImageWindow.KEY_ARROW_DOWN  or keyPressed == ImageWindow.KEY_SPACE or keyPressed == ord("n"):
        # process next frame
        #mustExit = True
        frameID = frameID+20

    elif keyPressed == ImageWindow.KEY_ARROW_UP:
        # process next frame
        #mustExit = True
        frameID = frameID-20

    elif keyPressed == ImageWindow.KEY_ARROW_RIGHT:
        # process next frame
        #mustExit = True
        frameID = frameID+2

    elif keyPressed == ImageWindow.KEY_ARROW_LEFT:
        # process next frame
        #mustExit = True
        frameID = frameID-2

    #elif keyPressed == ord("r"):
    #    # print "Pressed R button" - reset. Remove all marked crabs
    #    foundCrabs = list()
    #    image = origImage.copy()
    elif keyPressed == ord("q"):
        # print "Pressed Q button" quit
        message = "User pressed Q button"
        raise UserWantsToQuitException(message)
    else:
        redDotsBox = imageZoomWin.featureBox
        print ("redDotsBox Not Translated ", str(redDotsBox))

        redDotsBox = redDotsBox.translateCoordinateToOuter(zoomBox.topLeft)
        print ("redDotsBox Translated ", str(redDotsBox))

        redDotsData.addManualDots(frameID, redDotsBox)
        redDotsData.saveToFile(folderStruct.getRedDotsFilepath())

        redDotsData.sort()
        frameID = redDotsData.getMiddleOfBiggestGap()

cv2.destroyAllWindows()

exit()



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
    if not filename.endswith(".jpg"):
        print("Skipping some non JPG file", os.path.join(framesDir, filename))
        continue

    filepath = os.path.join(framesDir, filename)
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
