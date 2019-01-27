# command to install opencv library so that "import cv2" command does not fail
# python -m pip install opencv-python

#python -m pip install --upgrade imutils

#python -m pip install scikit-image

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 -vcodec copy -bsf h264_mp4toannexb "%d.h264"

# ffmpeg -i "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -f image2 "output/%d.h264"

# ffmpeg -i i"C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/V1_R_20180911_165259.avi" -strict -2 output.mp4

import cv2
import numpy as np
from skimage import measure
from skimage.draw import polygon_perimeter

from FeatureMatcher import drawBoxesAroundRedDots, isolateRedDots, drawContoursAroundRedDots

frameFile = "C:/workspaces/AnjutkaVideo/frames/frame7.jpg"

src3 = cv2.imread("C:/workspaces/AnjutkaVideo/frames/frame7.jpg", 1)
# cv2.imshow("hi",src3)

crabFile1 = 'C:/workspaces/AnjutkaVideo/crab_from_frame_1.png'
redDotFile01 = 'C:/workspaces/AnjutkaVideo/red_dot01.png'
redDotFile02 = 'C:/workspaces/AnjutkaVideo/red_dot02.png'

featureImage = cv2.imread(redDotFile01, 1)
img = cv2.imread(redDotFile02, 1)


cv2.imshow('featureImage', featureImage)


withRedDots = drawContoursAroundRedDots(src3)

#https://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/



#isolatedImage = isolateRedDots(src3)

#highlightMatchedFeatureRed(featureImage,mask0)
#labels = measure.label(isolatedImage, neighbors=8, background=0)
#mask = np.zeros(isolatedImage.shape, dtype="uint8")


#cv2.imshow('featureImage', featureImage)
cv2.imshow('mask0', withRedDots)
cv2.namedWindow('mask0', cv2.WINDOW_NORMAL) #) WINDOW_AUTOSIZE
#cv2.resizeWindow('mask0', 200, 300)
cv2.moveWindow('mask0', 400, 300)


#cv2.imshow('aaa', with_boxes)
#cv2.namedWindow('aaa', cv2.WINDOW_NORMAL) #) WINDOW_AUTOSIZE
#cv2.resizeWindow('mask0', 200, 300)
#cv2.moveWindow('aaa', 0, 0)


cv2.waitKey(0)



exit(0)

# upper mask (170-180)
lower_red = np.array([170,50,50])
upper_red = np.array([180,255,255])
mask1 = cv2.inRange(img_hsv, lower_red, upper_red)
print mask1

# join my masks
mask = mask0+mask1

# set my output img to zero everywhere except my mask
output_img = img.copy()
output_img[np.where(mask==0)] = 0

# or your HSV image, which I *believe* is what you want
output_hsv = img_hsv.copy()
output_hsv[np.where(mask==0)] = 0

cv2.imshow('img_hsv', img_hsv)
cv2.imshow('mask0', mask0)
cv2.namedWindow('mask0', cv2.WINDOW_NORMAL) #) WINDOW_AUTOSIZE
cv2.resizeWindow('mask0', 90, 60)

#cv2.imshow('mask1', mask1)
#cv2.imshow('mask', mask)
#cv2.imshow('output_img', output_img)
#cv2.imshow('output_hsv', output_hsv)


cv2.waitKey(0)
cv2.destroyAllWindows()

exit(0)


# Convert BGR to HSV
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

cv2.imshow('hsv', hsv)
cv2.imshow('gray', img_gray)

# define range of blue color in HSV
lower_blue = np.array([10, 255, 255])
upper_blue = np.array([180, 255, 255])

# Threshold the HSV image to get only blue colors
mask = cv2.inRange(hsv, lower_blue, upper_blue)

# Bitwise-AND mask and original image
res = cv2.bitwise_and(frame, frame, mask=mask)

cv2.imshow('frame', frame)
cv2.imshow('mask', mask)
cv2.imshow('res', res)


cv2.waitKey(0)
cv2.destroyAllWindows()

exit(0)

#img_rgb[mask == 255] = [0, 0, 255]


img_gray = cv2.cvtColor(featureImage, cv2.COLOR_BGR2GRAY)

#ret, mask = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV |cv2.THRESH_OTSU)
featureImage[mask == 255] = [0, 0, 255]


featureImage.Set(mask,cv2.Scalar(0,0,255))

cv2.imshow("aaaa", featureImage)

cv2.imshow("output", res)  # show windows

cv2.imshow("mask", mask)  # show windows


cv2.waitKey(0)
cv2.destroyAllWindows()

exit(0)


def drawShape(img, coordinates, color):
    # In order to draw our line in red
    #img = color.gray2rgb(img)

    # Make sure the coordinates are expressed as integers
    coordinates = coordinates.astype(int)

    img[coordinates[:, 0], coordinates[:, 1]] = 0

    return img
