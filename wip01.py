# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"

# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2
import time
from pyautogui import press

from FeatureMatcher import FeatureMatcher
from VideoFrame import VideoFrame
from common import Point, distanceBetweenPoints, Box, subImage

import os
filepath="C:/workspaces/AnjutkaVideo/frames/frame1.jpg"
filenameFull=os.path.basename(filepath)
filename=os.path.splitext(filenameFull)[0]


def writeToCSVFile(file, row):
    file.write(";".join(str(x) for x in row) + "\n")
    file.flush()


'''
import csv
with open(csvFilePath, 'wb') as crabsFile:
    writer = csv.writer(crabsFile,delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(dataRows)
crabsFile.close()
'''

#Open File where Frame Info will be written using Semicolumn as a delimiter. Write the Header row into the file
csvFilePath = 'C:/workspaces/AnjutkaVideo/redDots_log06.csv'
frameLogFile = open(csvFilePath, 'wb')

headerRow=VideoFrame.infoHeaders()
headerRow.insert(0, "frameNumber")
writeToCSVFile(frameLogFile, headerRow)


# src3 = cv2.imread("C:/Users/zal0001m/Documents/Private/AnjutkaVideo/IMG_20180814_181351.jpg")
# cv2.imshow("hi",src3)

crabFile1 = 'C:/workspaces/AnjutkaVideo/crab_from_frame_1.png'
redDotFile01 = 'C:/workspaces/AnjutkaVideo/red_dot01.png'
redDotFile02 = 'C:/workspaces/AnjutkaVideo/red_dot02.png'

featureImage = cv2.imread(redDotFile02, 0)
#frame = cv2.imread(redDotFile02, 1)


# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

print(cv2.__version__)
# vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi')
#vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/output_v1.mp4')
#vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi' )

vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi')
#vidcap = cv2.VideoCapture("D:/Video_Biology/Kara/2018/AMK72/2018_09_15_St_5993/V4__R_20180915_210447.avi")


#ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4

#success, image = vidcap.read()
count = 23785 #25130 # 26670 #25130 # 100 26215

cv2.startWindowThread()

def showWindow(windowName, image, position):
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)  #  WINDOW_AUTOSIZE
    cv2.resizeWindow(windowName, 900, 600)
    cv2.moveWindow(windowName, position.x, position.y)
    cv2.imshow(windowName, image)


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, filepath, lineDefined, onePointDefined,featureCoordiate, featureBox

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed


    # check to see if the left mouse button was released
    if event == cv2.EVENT_LBUTTONDOWN:
        #if not onePointDefined:
        #    refPt = [(x, y)]
        #else:
        #    refPt.append((x, y))

        featureCoordiate = Point(x,y)
        featureBox = Box(Point(max(x-50,1),max(y-50,1)),Point(x + 50, y + 50))

        cv2.rectangle(image, (max(x-50,1), max(y-50,1)), (x + 50, y + 50), (255, 0, 0), 2)
        #cv2.imshow("mainWithRedDots", image)



        press('a')

        #if onePointDefined:
        #    lineDefined = True
        #onePointDefined = True

        # draw a rectangle around the region of interest
        # cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)

        lineDefined=False
        if lineDefined:
            cv2.line(image, refPt[0], refPt[1], (0, 0, 255), 1)
            cv2.imshow(filepath, image)

featureCoordiate = Point(0, 0)
featureBox = Box(Point(1800,300),Point(1900,500))

fm = FeatureMatcher()
subImg = None
vf=None
success = True
while success:
    print 'Read a new frame: ', count
    windowName = 'Detected_' + str(count)

    # set the number of the frame to read
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, count)
    success, image = vidcap.read()

    if not success:
        "no more frames to read from video "
        break

    vf_prev = vf
    vf = VideoFrame(image, vf_prev)
    vf.isolateRedDots()
    #print "distance between Red Points"
    #print vf.distanceBetweenRedPoints()

    row=vf.infoAboutFrame()
    row.insert(0, count)

    print row

    writeToCSVFile(frameLogFile, row)

    withRedDots = vf.drawBoxesAroundRedDots()

    #img_rgb = cv2.imread(imagePath)
    #template = cv2.imread(feature_image, 0)


    if subImg is not None:
        print "subImg shape"
        print subImg.shape
        #cv2.imshow('subImg', subImg)
        #showWindow("subImg", subImg, Point(100, 100))
        #showWindow("mainWithRedDots", withRedDots, Point(700, 200))
        #cv2.waitKey(0)
        featureBox = fm.highlightMatchedFeature(withRedDots, subImg)
        if featureBox is not None:
            fm.drawBoxOnImage(withRedDots, featureBox)

    showWindow("mainWithRedDots", withRedDots, Point(700, 200))

    if featureBox is None:
        cv2.setMouseCallback("mainWithRedDots", click_and_crop)
        print "Click on a new feature"
        cv2.waitKey(0)
    else:
        cv2.waitKey(1000)
    #cv2.destroyAllWindows()

    print "featureBox is"
    print featureBox

    subImg = subImage(withRedDots, featureBox)

    # cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file

    count += 15

    if count > 29100:
        break

frameLogFile.close()
