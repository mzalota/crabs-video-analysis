# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"

# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2

from VideoFrame import VideoFrame
from common import Point

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
count = 2700

cv2.startWindowThread()

topLeftX= 600
topLeftY= 300
bottomRightX=1400
bottomRightY=700


def showWindow(windowName, image, position):
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)  #  WINDOW_AUTOSIZE
    cv2.resizeWindow(windowName, 900, 600)
    cv2.moveWindow(windowName, position.x, position.y)
    cv2.imshow(windowName, image)


success = True

vf=None

while success:
    print 'Read a new frame: ', count
    windowName = 'Detected_' + str(count)

    # start_frame_number = 50
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, count)

    # Now when you read the frame, you will be reading the 50th frame
    success, image = vidcap.read()
    showWindow(windowName, image, Point(700, 200))

    print "image"
    print type(image)

    vf_prev = vf
    vf = VideoFrame(image, vf_prev)
    vf.isolateRedDots()
    print "distance between Red Points"
    print vf.distanceBetweenRedPoints()

    withRedDots = vf.drawBoxesAroundRedDots()

    #windowName = 'Detected_' + str(count)
    #showWindow(windowName, image, Point(40, 40))
    showWindow(windowName, withRedDots, Point(700, 200))

    #showWindow("redDotsImageFragment", redDotsImageFragment, Point(700, 600))

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
    ##success,image = vidcap.read()


    count += 25

    if count > 29100:
        break
