# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"

# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2
import numpy
import os
import psutil
import gc

from FeatureMatcher import FeatureMatcher
# import time
# from pyautogui import press
from Frame import Frame
from Image import Image
from ImageWindow import ImageWindow
from VelocityDetector import VelocityDetector
from RedDotsDetector import RedDotsDetector
from VideoStream import VideoStream
from common import Point, Box
from logger import Logger


rootDirectory = "C:/workspaces/AnjutkaVideo/"


#vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi')

#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi'
#videoFilenameFull = 'KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi'
#videoFilenameFull = '2018_09_16_St_5994/V3_R_20180916_012323.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/output_st_v4.mp4'
videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V4__R_20180915_210447.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V5__R_20180915_211343.avi'
#videoFilenameFull = 'Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238.avi'
filenameFull = os.path.basename(videoFilenameFull)
videoFilename = os.path.splitext(filenameFull)[0]

videoStream = VideoStream(rootDirectory+"/"+videoFilenameFull)

print "videoFilename is "+videoFilename
#exit(0)

#filepath = "C:/workspaces/AnjutkaVideo/frames/frame1.jpg"
# filenameFull = os.path.basename(filepath)
# filename = os.path.splitext(filenameFull)[0]


# Open File where Frame Info will be written using Semicolumn as a delimiter. Write the Header row into the file
csvFilePath = rootDirectory+'/redDots_log09.csv'
#featuresFilePath = rootDirectory+'/drifts_log09.csv'
featuresFilePath = rootDirectory+videoFilename+'_drifts13.csv'
logger = Logger(csvFilePath, featuresFilePath)

headerRow = RedDotsDetector.infoHeaders()
headerRow.insert(0, "frameNumber")
logger.writeToRedDotsFile(headerRow)

driftsFileHeaderRow = VelocityDetector.infoHeaders()
driftsFileHeaderRow.insert(0, "frameNumber")
#driftsFileHeaderRow.append("frameNumber")
logger.writeToDriftsFile(driftsFileHeaderRow)

# src3 = cv2.imread("C:/Users/zal0001m/Documents/Private/AnjutkaVideo/IMG_20180814_181351.jpg")
# cv2.imshow("hi",src3)

# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi')
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/output_v1.mp4')
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi' )

#vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi')

# vidcap = cv2.VideoCapture("D:/Video_Biology/Kara/2018/AMK72/2018_09_15_St_5993/V4__R_20180915_210447.avi")
# ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4

#imageWinNoBoxes = ImageWindow("withoutFeatureBoxes", Point(700, 20))



# print "image shape"
# print image.shape
# (1080L, 1920L, 3L)


print(cv2.__version__)
cv2.startWindowThread()

velocityDetector = VelocityDetector()
vf = None
imageWin = ImageWindow("mainWithRedDots", Point(700, 200))

stepSize = 5
startingFrameID = 14100 #2000  #22380 #20350   #18200 #30   #10000 #2500  # 5180 #23785  # 25130 # 26670 #25130 # 100 26215
prevDriftLength = 0

prev1 = 0
prev2 = 0
prev3 = 0
prev4 = 0

success = True
while success:

    print 'Read a new frame: ', startingFrameID
    windowName = 'Detected_' + str(startingFrameID)

    try:
        image = videoStream.readImage(startingFrameID)
        frame = Frame(startingFrameID, videoStream)
    except Exception as error:
        print ("no more frames to read from video ")
        print('Caught this error: ' + repr(error))
        break

    '''
    vf_prev = vf
    vf = RedDotsDetector(frame, vf_prev)
    vf.isolateRedDots()
    withRedDotsObj = vf.drawBoxesAroundRedDots()
    withRedDots = frame.getImgObj().asNumpyArray()

    row = vf.infoAboutFrame()
    row.insert(0, count)
    logger.writeToRedDotsFile(row)
    print row
    '''

    # findBrightestSpot()
    '''
    if needToSelectFeature:
        needToSelectFeature = False
        imageWin.showWindowAndWaitForClick(withRedDots)
        firstFeature = imageWin.featureCoordiate
        print "settig first feature location to"
        print firstFeature
        fm.setFeatureLocation(firstFeature)
    '''

    velocityDetector.detectVelocity(frame, image)
    #velocityDetector.detectVelocity(frame, withRedDots)
    driftVector = velocityDetector.getMedianDriftVector()

    print "prevDriftLength: "+ str(prevDriftLength)
    if driftVector is not None:
        driftLength = driftVector.length()

        if prevDriftLength == 0:
            #just for initialization
            prevDriftLength = driftLength

        driftsRow = velocityDetector.infoAboutDrift()
        driftsRow.insert(0, startingFrameID)
        print driftsRow

        if abs(abs(driftLength)-abs(prevDriftLength)) < abs(prevDriftLength)/2:
            prevDriftLength = driftLength
        else:
            # this is outlier. ignore it
            print "OUTLIER"
            driftsRow.append("OUTLIER")
        logger.writeToDriftsFile(driftsRow)

    #print "drift distance/angle is: "+str(driftDistance) + "/" + str(driftAngle)
    #print "drift vector is: "+str(driftVector)

    #img = Image(withRedDots)
    img = Image(image)
    img.drawDriftVectorOnImage(driftVector)

    #withRedDots = img.asNumpyArray()

    #imageWin.showWindowAndWait(img.asNumpyArray(), 1000)

    imageWin.showWindowAndWaitForClick(img.asNumpyArray())

    # cv2.destroyAllWindows()


    startingFrameID += stepSize

    #gc.collect()
    #printMemoryUsage()

    if startingFrameID > 99100:
        break

logger.closeFiles()


# img_rgb = cv2.imread(imagePath)
# template = cv2.imread(feature_image, 0)
