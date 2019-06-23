import pandas as pd
import cv2

from lib.Logger import Logger
from lib.SeeFloorSection import SeeFloorSection
from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point, Box
import os
from datetime import datetime

# filename=os.path.splitext(filepath)[0]
# filenameFull=os.path.basename(filepath)
# filename=os.path.splitext(filenameFull)[0]

# rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"

# videoFileName = "V4__R_20180915_210447"
# videoFileName = "V6__R_20180915_212238"
videoFileName = "V3_R_20180911_170159"
# videoFileName = "V2_R_20180911_165730"


folderStruct = FolderStructure(rootDir, videoFileName)

videoStream = VideoStream(folderStruct.getVideoFilepath())


# framesDir = rootDir + "/" + videoFileName + "/seqFrames/"
# outputFilePath = rootDir + "/" + videoFileName + "/" + videoFileName + "_crabs.csv"

class UserWantsToQuitException(Exception):
    pass

def processImage(image, imageWin, frameID):
    origImage = image.copy()
    foundCrabs = list()
    mustExit = False
    while not mustExit:
        keyPressed = imageWin.showWindowAndWaitForClick(image)
        #print ("pressed button", keyPressed)

        if keyPressed == ord("n") or keyPressed == imageWin.KEY_ARROW_DOWN or keyPressed == imageWin.KEY_ARROW_RIGHT or keyPressed == imageWin.KEY_SPACE:
            # process next frame
            mustExit = True
        elif keyPressed == ord("r"):
            # print "Pressed R button" - reset. Remove all marked crabs
            foundCrabs = list()
            image = origImage.copy()
        elif keyPressed == ord("q"):
            # print "Pressed Q button" quit
            message = "User pressed Q button"
            raise UserWantsToQuitException(message)
        else:
            crabBox = getCrabWidth(imageWin, image, frameID)
            foundCrabs.append(crabBox)
        # print("foundCrab", str(crabBox), crabBox.diagonal(), str(crabBox.centerPoint()))

    return foundCrabs
    print "Done with this frame"

def saveCrabToFile(crabOnSeeFloor, frameID):
    crabImage1 = crabOnSeeFloor.getImageOnFrame(frameID)
    frameNumberString = str(frameID).zfill(6)
    imageFileName = "crab" + frameNumberString + ".jpg"
    imageFilePath = folderStruct.getFramesDirpath() + "/" + imageFileName
    crabImage1.writeToFile(imageFilePath)


def getCrabWidth(imageWin, image, frameID):
    mainImage = Image(image)
    crabPoint = imageWin.featureCoordiate
    boxAroundCrab = crabPoint.boxAroundPoint(200)
    crabImage = mainImage.subImage(boxAroundCrab)

    #findViewsOfTheSameCrab(boxAroundCrab, frameID)

    crabWin = ImageWindow.createWindow("crabImage", Box(Point(0, 0), Point(600, 600)))
    crabWin.showWindowAndWaitForTwoClicks(crabImage.asNumpyArray())
    crabWin.closeWindow()

    crabOnMainWindow = crabWin.featureBox.translateCoordinateToOuter(boxAroundCrab.topLeft)
    mainImage.drawLine(crabOnMainWindow.topLeft, crabOnMainWindow.bottomRight)

    return crabOnMainWindow


def findViewsOfTheSameCrab(boxAroundCrab, frameID):
    frame = Frame(frameID, videoStream)
    crabOnSeeFloor = SeeFloorSection(frame, boxAroundCrab)
    crabOnSeeFloor.setThreshold(0.8)
    crabOnSeeFloor.findInAllFrames()
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID())
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 1)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 2)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 3)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 4)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 5)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 6)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 7)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 8)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 9)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 10)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 11)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 12)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 13)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 14)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 15)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 16)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 17)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 18)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 19)
    saveCrabToFile(crabOnSeeFloor, crabOnSeeFloor.getMaxFrameID() - 20)
    crabOnSeeFloor.showSubImage()
    #crabOnSeeFloor.closeWindow()


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

imageWin = ImageWindow("mainWindow", Point(700, 200))

crabsDF = pd.DataFrame(
    columns=['dir', 'filename', 'crabNumber', 'crabWidthPixels', 'crabLocationX', 'crabLocationY', 'crabWidthLine'])
crabNumber = 1

framesDir = folderStruct.getFramesDirpath()

logger = Logger.openInAppendMode(folderStruct.getCrabsFilepath())


for filename in os.listdir(framesDir):
    if not filename.endswith(".jpg"):
        print("Skipping some non JPG file", os.path.join(framesDir, filename))
        continue

    filepath = os.path.join(framesDir, filename)
    image = cv2.imread(filepath)
    frameID = int(filename[5:11])
    # print ("frameStr", frameID)
    try:
        foundCrabs = processImage(image, imageWin, frameID)
        crabNumber = writeCrabsInfoToFile(crabNumber, foundCrabs, logger, crabsDF)
    except UserWantsToQuitException as error:
        #print repr(error)
        print("User requested to quit on frame: "+ str(frameID))
        break

logger.closeFile()
#crabsDF.to_csv(folderStruct.getCrabsFilepath(), sep='\t')

# close all open windows
cv2.destroyAllWindows()
