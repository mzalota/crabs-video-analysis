from collections import namedtuple

import cv2
import numpy as np
from skimage import measure

from common import Point, Box


class RedDot:
    __dotLocationInner = None
    boxAroundDot = None

    def __init__(self, frame, redDotsSearchArea):
        self.__frame = frame
        self.__redDotsSearchArea = redDotsSearchArea

    def __getImage(self):
        return self.__frame.getImage()

    def dotWasDetected(self):
        if self.boxAroundDot:
            return True
        else:
            return False

    def isolateRedDots(self, debugWindowName = None):

        featureImage = self.__redDotsSearchImage(self.__getImage(), self.__redDotsSearchArea)
        mask_color = self.__isolateAreasWithRedColor(featureImage)
        mask_final = self.__blurErodeDilate(mask_color)
        contours = measure.find_contours(mask_final, 0.9)

        bounding_boxes = self.__boundingBoxesAroundContours(contours)
        top2Boxes = self.__keepTwoLargestContours(bounding_boxes)

        if debugWindowName:
            #print "top2Boxes"
            #print top2Boxes

            cv2.imshow(debugWindowName+"_image_to_locate_red_dots", featureImage)
            cv2.imshow(debugWindowName+"_mask_in_before_blur", mask_color)
            #cv2.imshow(debugWindowName+"_mask01_after_blur", self.__mask_blurred)
            #cv2.imshow(debugWindowName+"_mask02_after_erode", self.__mask_eroded)
            cv2.imshow(debugWindowName+"_mask03_after_dilate", mask_final)
            #cv2.waitKey(0)

        if len(top2Boxes)>0:
            #print "topBox"
            #print top2Boxes[0]
            self.__dotLocationInner = top2Boxes[0]
            self.boxAroundDot = top2Boxes[0].translateCoordinateToOuter(self.__redDotsSearchArea.topLeft)
        else:
            pass

        #return top2Boxes


    def __redDotsSearchImage(self,image, redDotsSearchArea):
        """
        :return: numpy.ndarray 
        """
        #print "redDotsSearchArea"
        #print redDotsSearchArea
        return image[redDotsSearchArea.topLeft.y:redDotsSearchArea.bottomRight.y, redDotsSearchArea.topLeft.x: redDotsSearchArea.bottomRight.x]


    def __isolateAreasWithRedColor(self, featureImage):

        img_hsv = cv2.cvtColor(featureImage, cv2.COLOR_BGR2HSV)

        #TODO: add both ranges of color 0-10 and 150-200
        #lower_red = np.array([150, 0, 190])
        #upper_red = np.array([200, 255, 255])

        # lower mask (0-10)
        lower_red = np.array([0, 100, 150]) #150
        upper_red = np.array([10, 255, 255])

        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

        # upper mask (170-180)
        lower_red = np.array([150, 100, 150]) #150
        upper_red = np.array([200, 255, 255])
        mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

        # join my masks
        mask = mask0 + mask1

        return mask


    def __blurErodeDilate(self, mask_in):
        # perform a series of erosions and dilations to remove
        # any small blobs of noise from the thresholded image
        mask_blurred = cv2.GaussianBlur(mask_in, (11, 11), 0)
        mask_eroded = cv2.erode(mask_blurred, None, iterations=1)
        mask_dilated = cv2.dilate(mask_eroded, None, iterations=6)
        #return np.copy(mask_dilated)
        return mask_dilated


    def __keepTwoLargestContours(self, bounding_boxes):
        bounding_boxes = sorted(bounding_boxes, key=lambda box: abs((box.topLeft.x - box.bottomRight.x) * (box.topLeft.y - box.bottomRight.y)), reverse=True)
        #print "bounding_boxes"
        #print bounding_boxes
        return bounding_boxes[:2]

    def __boundingBoxesAroundContours(self, contours):
        #print "contours"
        # print contours
        bounding_boxes = []
        for contour in contours:
            box = self.__boundingBoxAroundContour(contour)
            bounding_boxes.append(box)
        return bounding_boxes

    def __boundingBoxAroundContour(self, contour):
        Xmin = int(np.min(contour[:, 1]))
        Xmax = int(np.max(contour[:, 1]))
        Ymin = int(np.min(contour[:, 0]))
        Ymax = int(np.max(contour[:, 0]))
        box = Box(Point(Xmin, Ymin), Point(Xmax, Ymax))
        return box
