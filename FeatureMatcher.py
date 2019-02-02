from collections import namedtuple

import cv2
import numpy as np
from skimage import measure
# https://www.geeksforgeeks.org/template-matching-using-opencv-in-python/
from skimage.draw import polygon_perimeter

Box = namedtuple('Box', 'topLeft bottomRight')
Point = namedtuple('Point', 'x y')

class FeatureMatcher:

    mask_color  = None
    mask_blurred  = None
    mask_eroded  = None
    mask_dilated = None

    def highlightMatchedFeature(self, img_rgb, template):
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


    def isolateRedDots(self, featureImage):

        self.mask_color = self.__isolateAreasWithRedColor(featureImage)

        self.mask_final = self.__blurErodeDilate(self.mask_color)

        contours = measure.find_contours(self.mask_final, 0.9)

        bounding_boxes = self.__boundingBoxesAroundContours(contours)
        top2Boxes = self.__keepTwoLargestContours(bounding_boxes)

        return top2Boxes


    def __isolateAreasWithRedColor(self, featureImage):

        #TODO: add both ranges of color 0-10 and 150-200
        #lower_red = np.array([150, 0, 190])
        #upper_red = np.array([200, 255, 255])

        lower_red = np.array([0, 0, 150])
        upper_red = np.array([10, 255, 255])

        img_hsv = cv2.cvtColor(featureImage, cv2.COLOR_BGR2HSV)
        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)
        #cv2.imshow("mask0_before_GaussianBlur", mask0)
        return mask0


    def __blurErodeDilate(self, mask_in):
        # perform a series of erosions and dilations to remove
        # any small blobs of noise from the thresholded image
        cv2.imshow("mask_in_before_blur", mask_in)

        self.mask_blurred = cv2.GaussianBlur(mask_in, (11, 11), 0)
        cv2.imshow("mask01_after_blur", self.mask_blurred)

        self.mask_eroded = cv2.erode(self.mask_blurred, None, iterations=1)
        cv2.imshow("mask02_after_erode", self.mask_eroded)

        self.mask_dilated = cv2.dilate(self.mask_eroded, None, iterations=6)
        cv2.imshow("mask03_after_dilate", self.mask_dilated)

        return np.copy(self.mask_dilated)


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
