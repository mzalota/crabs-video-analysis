# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"

# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2
#import time
#from pyautogui import press

from ImageWindow import ImageWindow
from FeatureMatcher import FeatureMatcher
from VideoFrame import VideoFrame
from common import Point

import os

from logger import Logger

filepath = "C:/workspaces/AnjutkaVideo/frames/frame1.jpg"
#filenameFull = os.path.basename(filepath)
#filename = os.path.splitext(filenameFull)[0]


def writeToCSVFile(file, row):
    file.write(";".join(str(x) for x in row) + "\n")
    file.flush()


# Open File where Frame Info will be written using Semicolumn as a delimiter. Write the Header row into the file
csvFilePath = 'C:/workspaces/AnjutkaVideo/redDots_log06.csv'
featuresFilePath = 'C:/workspaces/AnjutkaVideo/features_log06.csv'
logger = Logger(csvFilePath, featuresFilePath)

headerRow = VideoFrame.infoHeaders()
headerRow.insert(0, "frameNumber")
logger.writeToRedDotsFile(headerRow)

# src3 = cv2.imread("C:/Users/zal0001m/Documents/Private/AnjutkaVideo/IMG_20180814_181351.jpg")
# cv2.imshow("hi",src3)

crabFile1 = 'C:/workspaces/AnjutkaVideo/crab_from_frame_1.png'
redDotFile01 = 'C:/workspaces/AnjutkaVideo/red_dot01.png'
redDotFile02 = 'C:/workspaces/AnjutkaVideo/red_dot02.png'

featureImage = cv2.imread(redDotFile02, 0)

# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

print(cv2.__version__)
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi')
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/output_v1.mp4')
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi' )

vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi')
# vidcap = cv2.VideoCapture("D:/Video_Biology/Kara/2018/AMK72/2018_09_15_St_5993/V4__R_20180915_210447.avi")


# ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4


count = 100 # 5180 #23785  # 25130 # 26670 #25130 # 100 26215

needToSelectFeature = True

cv2.startWindowThread()

imageWin = ImageWindow("mainWithRedDots", Point(700, 200))

imageWinNoBoxes = ImageWindow("withoutFeatureBoxes", Point(700, 20))

featureBox = None
fm = FeatureMatcher(Point(1250, 75))
fm2 = FeatureMatcher(Point(1500, 350),503)
fm3 = FeatureMatcher(Point(500, 350),601)
fm4 = FeatureMatcher(Point(1000, 350),547)

print fm.infoHeaders()

subImg = None
vf = None
success = True


def findBrightestSpot():
    global image
    # https://www.pyimagesearch.com/2014/09/29/finding-brightest-spot-image-using-python-opencv/
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    radius_ = 37
    gray = cv2.GaussianBlur(gray, (radius_, radius_), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    image = orig.copy()
    cv2.circle(image, maxLoc, radius_, (255, 0, 0), 2)
    print "brigtest spot maxLoc"
    print maxLoc
    print maxVal
    imageWin.showWindowAndWaitForClick(image)


while success:
    print 'Read a new frame: ', count
    windowName = 'Detected_' + str(count)

    # set the number of the frame to read
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, count)
    success, image = vidcap.read()
    #print "image shape"
    #print image.shape
    #(1080L, 1920L, 3L)

    if not success:
        "no more frames to read from video "
        break

    vf_prev = vf
    vf = VideoFrame(image, vf_prev)
    imageCopy = image.copy()
    vf.isolateRedDots()
    withRedDots = vf.drawBoxesAroundRedDots()

    row = vf.infoAboutFrame()
    row.insert(0, count)
    logger.writeToRedDotsFile(row)

    #findBrightestSpot()
    '''
    if needToSelectFeature:
        needToSelectFeature = False
        imageWin.showWindowAndWaitForClick(withRedDots)
        firstFeature = imageWin.featureCoordiate
        print "settig first feature location to"
        print firstFeature
        fm.setFeatureLocation(firstFeature)
    '''

    fm.getFeature(imageCopy)
    fm2.getFeature(imageCopy)
    fm3.getFeature(imageCopy)
    fm4.getFeature(imageCopy)

    #imageWinNoBoxes.showWindow(withRedDots)

    fm.showSubImage()
    fm2.showSubImage()
    fm3.showSubImage()
    fm4.showSubImage()

    fm.drawBoxOnImage(withRedDots)
    fm2.drawBoxOnImage(withRedDots)
    fm3.drawBoxOnImage(withRedDots)
    fm4.drawBoxOnImage(withRedDots)

    #print fm.infoAboutFeature()
    #print fm2.infoAboutFeature()
    #print fm3.infoAboutFeature()
    #print fm4.infoAboutFeature()

    imageWin.showWindowAndWait(withRedDots, 1000)

    # imageWin.showWindowAndWaitForClick(withRedDots)

    # cv2.destroyAllWindows()



    count += 5

    if count > 29100:
        break

        # cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file

logger.closeFiles()


# img_rgb = cv2.imread(imagePath)
# template = cv2.imread(feature_image, 0)

