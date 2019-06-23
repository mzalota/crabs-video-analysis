import pandas as pd
import cv2

from lib.SeeFloorSection import SeeFloorSection
from lib.FolderStructure import FolderStructure
from lib.Frame import Frame
from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point, Box
import os

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


def processImage(image, imageWin, frameID):
    origImage = image.copy()
    foundCrabs = list()
    mustExit = False
    while not mustExit:
        keyPressed = imageWin.showWindowAndWaitForClick(image)
        print ("pressed button", keyPressed)
        # if the 'n' key is pressed return
        if keyPressed == ord("n") or keyPressed == 0:  # pressed right arrow
            mustExit = True
        elif keyPressed == ord("r"):
            # print "Pressed R button"
            foundCrabs = list()
            image = origImage.copy()
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

    frame1 = Frame(frameID, videoStream)
    # frame2 = Frame(frameID + 50, videoStream)
    # frame3 = Frame(frameID - 50, videoStream)


    crabOnSeeFloor = SeeFloorSection(frame1, boxAroundCrab)
    crabOnSeeFloor.setThreshold(0.8)

    crabOnSeeFloor.findInAllFrames()
    #crabOnSeeFloor.showSubImageForFrame(crabOnSeeFloor.getMaxFrameID())
    #crabImage2 = crabOnSeeFloor.getImageOnFrame(crabOnSeeFloor.getMaxFrameID() - 1)
    #crabImage3 = crabOnSeeFloor.getImageOnFrame(crabOnSeeFloor.getMaxFrameID() - 2)

    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID())
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-1)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-2)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-3)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-4)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-5)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-6)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-7)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-8)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-9)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-10)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-11)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-12)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-13)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-14)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-15)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-16)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-17)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-18)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-19)
    saveCrabToFile(crabOnSeeFloor,crabOnSeeFloor.getMaxFrameID()-20)


    # print ("frame1", crabOnSeeFloor.infoAboutFeature())
    # crabOnSeeFloor.showSubImage()

    # crabOnSeeFloor.findFeature(frame2)
    # print ("frame2", crabOnSeeFloor.infoAboutFeature())

    # crabOnSeeFloor.findFeature(frame3)
    # print ("frame3",crabOnSeeFloor.infoAboutFeature())


    # crabOnSeeFloor.showSubImage()

    crabWin = ImageWindow.createWindow("crabImage", Box(Point(0, 0), Point(600, 600)))
    crabWin.showWindowAndWaitForTwoClicks(crabImage.asNumpyArray())
    crabWin.closeWindow()

    crabOnSeeFloor.closeWindow()

    crabOnMainWindow = crabWin.featureBox.translateCoordinateToOuter(boxAroundCrab.topLeft)
    mainImage.drawLine(crabOnMainWindow.topLeft, crabOnMainWindow.bottomRight)

    return crabOnMainWindow

imageWin = ImageWindow("mainWindow", Point(700, 200))

crabsDF = pd.DataFrame(
    columns=['dir', 'filename', 'crabNumber', 'crabWidthPixels', 'crabLocationX', 'crabLocationY', 'crabWidthLine'])

crabNumber = 1
framesDir = folderStruct.getFramesDirpath()
for filename in os.listdir(framesDir):

    if filename.endswith(".jpg"):
        filepath = os.path.join(framesDir, filename)
        image = cv2.imread(filepath)
        frameID = int(filename[5:11])
        # print ("frameStr", frameID)
        foundCrabs = processImage(image, imageWin, frameID)
        for crab in foundCrabs:
            crabsDF = crabsDF.append(
                {'dir': framesDir, 'filename': filename, 'frameID': frameID, 'crabNumber': crabNumber,
                 'crabWidthPixels': crab.diagonal(),
                 'crabLocationX': crab.centerPoint().x, 'crabLocationY': crab.centerPoint().y, 'crabWidthLine': crab},
                ignore_index=True)

            print("crab", framesDir, filename, frameID, crabNumber, crab.diagonal(), crab.centerPoint().x,
                  crab.centerPoint().y,
                  str(crab.centerPoint()), str(crab))
            crabNumber += 1
        continue
    else:
        print("Skipping some non JPG file", os.path.join(framesDir, filename))
        continue

crabsDF.to_csv(folderStruct.getCrabsFilepath(), sep='\t')

# close all open windows
cv2.destroyAllWindows()
