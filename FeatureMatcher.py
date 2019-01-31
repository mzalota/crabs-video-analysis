from collections import namedtuple

import cv2
import numpy as np
from skimage import measure
# https://www.geeksforgeeks.org/template-matching-using-opencv-in-python/
from skimage.draw import polygon_perimeter

Box = namedtuple('Box', 'topLeft bottomRight')
Point = namedtuple('Point', 'x y')

def highlightMatchedFeature(img_rgb, template):
    # Convert it to grayscale
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    # Read the template
    # Store width and heigth of template in w and h
    w, h = template.shape[::-1]
    # Perform match operations.
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    # Specify a threshold (it was 0.8)
    threshold = 0.6
    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= threshold)
    # Draw a rectangle around the matched region.
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)


def keepTwoLargestContours(contours):
    print "contours"
    #print contours

    bounding_boxes = []
    for contour in contours:
        Xmin = int(np.min(contour[:, 1]))
        Xmax = int(np.max(contour[:, 1]))
        Ymin = int(np.min(contour[:, 0]))
        Ymax = int(np.max(contour[:, 0]))
        box = Box(Point(Xmin,Ymin), Point(Xmax,Ymax))

        #bounding_boxes.append([Xmin, Xmax, Ymin, Ymax])
        bounding_boxes.append(box)

    # bounding_boxes = sorted(bounding_boxes, key=lambda p: p.area, reverse=True)
    #bounding_boxes = sorted(bounding_boxes, key=lambda box: abs((box[0] - box[1]) * (box[2] - box[3])), reverse=True)
    bounding_boxes = sorted(bounding_boxes, key=lambda box: abs((box.topLeft.x - box.bottomRight.x) * (box.topLeft.y - box.bottomRight.y)), reverse=True)
    print "bounding_boxes"
    print bounding_boxes
    return bounding_boxes[:2]


def isolateRedDots(featureImage):

    img_hsv = cv2.cvtColor(featureImage, cv2.COLOR_BGR2HSV)
    # img_hsv=featureImage
    # lower mask (0-10)
    # lower_red = np.array([0,50,50])
    lower_red = np.array([150, 0, 190])
    upper_red = np.array([200, 255, 255])
    # upper_red = np.array([221,227,224])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

    cv2.imshow("mask0_before_GaussianBlur", mask0)

    mask0 = cv2.GaussianBlur(mask0, (11, 11), 0)

    cv2.imshow("mask0_before_erode", mask0)
    #cv2.waitKey(0)

    # perform a series of erosions and dilations to remove
    # any small blobs of noise from the thresholded image
    mask0 = cv2.erode(mask0, None, iterations=1)

    cv2.imshow("mask0_before_dilate", mask0)

    mask0 = cv2.dilate(mask0, None, iterations=6)

    # cv2.imshow("redDotMask", isolatedImage)
    contours = measure.find_contours(mask0, 0.9)
    top2Boxes = keepTwoLargestContours(contours)
    return top2Boxes


def drawBoxesAroundRedDots_old(image_without_boxes, bounding_boxes):
    #https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0


    with_boxes = np.copy(image_without_boxes)

    for box in bounding_boxes:
        # [Xmin, Xmax, Ymin, Ymax]
        print "area: "
        print box
        print abs((box[0]-box[1])*(box[2]-box[3]))
        r = [box[0], box[1], box[1], box[0], box[0]]
        c = [box[3], box[3], box[2], box[2], box[3]]
        rr, cc = polygon_perimeter(r, c, with_boxes.shape)
        with_boxes[rr, cc] = 1  # set color white
    return with_boxes


#def drawContoursAroundRedDots(src3):
#    contours = isolateRedDots(src3)
#    return drawBoxesAroundRedDots(src3, contours)

