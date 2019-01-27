# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"

# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2
import numpy as np


from FeatureMatcher import highlightMatchedFeature, drawContoursAroundRedDots, isolateRedDots

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
#vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V2_R_20180911_165730.avi')

#vidcap = cv2.VideoCapture('C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi')
vidcap = cv2.VideoCapture('D:\Video_Biology\Kara\2018\AMK72\2018_09_15_St_5993\V4__R_20180915_210447.avi')


#ffmpeg -i "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi" -strict -2 ../output_st_v3.mp4

success, image = vidcap.read()
count = 81
success = True

cv2.startWindowThread()

sectionWithDots=[300,1300,600,1400]

dotsShift=150

while success:
    print 'Read a new frame: ', count
    print "sectionWithDots"
    print sectionWithDots
    # resize(image, dst, Size(), 0.5, 0.5, interpolation);

    #highlightMatchedFeature(image, featureImage)

    redDotsArea = image[sectionWithDots[0]:sectionWithDots[1], sectionWithDots[2]:sectionWithDots[3]]

    dots = isolateRedDots(redDotsArea)
    topX = int(min(dots[0][0],dots[1][0]))
    bottomX = int(max(dots[0][1], dots[1][1]))
    topY = int(min(dots[0][2], dots[1][2]))
    bottomY = int(max(dots[0][3], dots[1][3]))
    print topX, bottomX, topY, bottomY

    sectionWithDots[0] = sectionWithDots[0] + topX-dotsShift
    sectionWithDots[1] = sectionWithDots[0] + bottomX + dotsShift
    sectionWithDots[2] = sectionWithDots[2] + topY - dotsShift
    sectionWithDots[3] = sectionWithDots[2] + bottomY + dotsShift

    withRedDots = drawContoursAroundRedDots(redDotsArea)

    windowName = 'Detected_' + str(count)
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL) #) WINDOW_AUTOSIZE

    #cv2.resize(image, (0, 0), fx=0.5, fy=0.5)

    cv2.resizeWindow(windowName, 900, 600)
    cv2.moveWindow(windowName, 40, 30)
    cv2.imshow(windowName, withRedDots)

    cv2.imshow("orig", image)

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
