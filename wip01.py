# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"

# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2
import numpy as np
from collections import namedtuple

from FeatureMatcher import highlightMatchedFeature, drawContoursAroundRedDots, isolateRedDots


Point = namedtuple('Point', 'x y')

Box = namedtuple('Box', 'topLeft bottomRight')


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

success, image = vidcap.read()
count = 1750

cv2.startWindowThread()

sectionWithDots=[300,600,600,1400]
#boxAroundDots=Box(Point(300,600),Point(600,1400))
dotsShift=150

topLeftX= 600
topLeftY= 300
bottomRightX=1400
bottomRightY=700


def showWindow(windowName, image, position):
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)  #  WINDOW_AUTOSIZE
    cv2.resizeWindow(windowName, 900, 600)
    cv2.moveWindow(windowName, position.x, position.y)
    cv2.imshow(windowName, image)

def boxAroundBoxes(box1, box2):
    topLeft=Point(min(box1.topLeft.x, box2.topLeft.x),min(box1.topLeft.y, box2.topLeft.y))
    bottomRight=Point(max(box1.bottomRight.x, box2.bottomRight.x),max(box1.bottomRight.y, box2.bottomRight.y))
    return Box(topLeft, bottomRight)

while success:
    print 'Read a new frame: ', count
    print "sectionWithDots"
    #print sectionWithDots
    # resize(image, dst, Size(), 0.5, 0.5, interpolation);
    print Box(Point(topLeftX,topLeftY), Point(bottomRightX,bottomRightY))
    #highlightMatchedFeature(image, featureImage)


    #redDotsArea = image[sectionWithDots[0]:sectionWithDots[1], sectionWithDots[2]:sectionWithDots[3]]
    #redDotsArea = image[topLeftX: bottomRightX, topLeftY:bottomRightY]
    redDotsArea = image[topLeftY:bottomRightY,topLeftX: bottomRightX]

    print "shape of redDotsArea"
    print redDotsArea.shape


    dots = isolateRedDots(redDotsArea)

    showWindow("redDotsArea", redDotsArea, Point(400, 400))
    cv2.waitKey(0)

    boxAroundBoxesInner = boxAroundBoxes(dots[0], dots[1])
    print "boxAroundBoxesInner"
    print boxAroundBoxesInner

    '''
    topX = int(min(dots[0][0],dots[1][0]))
    bottomX = int(max(dots[0][1], dots[1][1]))
    topY = int(min(dots[0][2], dots[1][2]))
    bottomY = int(max(dots[0][3], dots[1][3]))
    print topX, bottomX, topY, bottomY

    sectionWithDots[0] = max(sectionWithDots[0] + topX-dotsShift,1)
    sectionWithDots[1] = min(sectionWithDots[0] + bottomX + dotsShift,1500)
    sectionWithDots[2] = max(sectionWithDots[2] + topY - dotsShift,1)
    sectionWithDots[3] = min(sectionWithDots[2] + bottomY + dotsShift,1500)
    '''
    sectionWithDots[0] = max(sectionWithDots[0] + dots[0].topLeft.x-dotsShift,1)
    sectionWithDots[1] = min(sectionWithDots[0] + dots[1].bottomRight.x + dotsShift,1500)
    sectionWithDots[2] = max(sectionWithDots[2] + dots[0].topLeft.y - dotsShift,1)
    sectionWithDots[3] = min(sectionWithDots[2] + dots[1].bottomRight.y + dotsShift,1500)

    print "image.shapte"
    print image.shape
    print "shape x width"
    print image.shape[1]

    print "dddddd"
    #print max(boxAroundDots.topLeft.x + boxAroundBoxesInner.topLeft.x - dotsShift,1)

    topLeftX = max(topLeftX + boxAroundBoxesInner.topLeft.x - dotsShift,1)
    topLeftY = max(topLeftY + boxAroundBoxesInner.topLeft.y - dotsShift, 1)
    bottomRightX = min(topLeftX + boxAroundBoxesInner.bottomRight.x + dotsShift, image.shape[1])
    bottomRightY = min(topLeftY + boxAroundBoxesInner.bottomRight.y + dotsShift, image.shape[0])

    print "aaaa"
    #print boxAroundDots


    withRedDots = drawContoursAroundRedDots(redDotsArea)

    windowName = 'Detected_' + str(count)
    showWindow(windowName, image, Point(40,40))

    showWindow("redDots", withRedDots, Point(700, 200))


    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
    ##success,image = vidcap.read()

    # start_frame_number = 50
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, count)

    # Now when you read the frame, you will be reading the 50th frame
    success, image = vidcap.read()

    count += 250

    if count > 29100:
        break
