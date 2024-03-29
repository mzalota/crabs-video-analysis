import cv2
import numpy as np
from skimage import measure

from lib.model.Image import Image
from lib.model.Box import Box
from lib.model.Point import Point


class RedDot:
    boxAroundDot = None

    def __init__(self, image, redDotsSearchArea):
        # type: (Image, Box) -> object
        self.__image = image
        self.__redDotsSearchArea = redDotsSearchArea
        selected_box = self.__isolate()
        if selected_box is not None:
            self.boxAroundDot = selected_box.translateCoordinateToOuter(self.__redDotsSearchArea.topLeft)
        else:
            self.boxAroundDot = None

    def dotWasDetected(self):
        if self.boxAroundDot:
            return True
        else:
            return False

    def debugging_images(self):
        return self.__for_debugging

    def __isolate(self):
        featureImage = self.__image.subImage(self.__redDotsSearchArea).asNumpyArray()
        mask_color = self.__isolateAreasWithRedColor(featureImage)
        mask_final = self.__blurErodeDilate(mask_color)

        self.__for_debugging = dict()
        self.__for_debugging["image_orig"] = featureImage
        self.__for_debugging["01_isolated_colors"] = mask_color
        self.__for_debugging["02_blur_dilate"] = mask_final

        contours = measure.find_contours(mask_final, 0.9)
        if len(contours) <= 0:
            return

        bounding_boxes = self.__boundingBoxesAroundContours(contours)
        top2Boxes = self.__keepTwoLargestContours(bounding_boxes)
        selected_box = top2Boxes[0]

        image = self.__draw_boxes(mask_final, bounding_boxes, selected_box)
        self.__for_debugging["03_bounded_boxes"] = image.asNumpyArray()

        return selected_box

    def __draw_boxes(self, mask_final, bounding_boxes, selected_box):
        image = Image(mask_final).copy()
        for box in bounding_boxes:
            # print("box is", str(box))
            image.drawBoxOnImage(box, color=(255, 255, 255))
        image.drawBoxOnImage(selected_box, color=(255, 255, 0))
        return image

    def __isolateAreasWithRedColor(self, featureImage):
        img_hsv = cv2.cvtColor(featureImage, cv2.COLOR_BGR2HSV)

        # red mask (0-10) - red colors
        lower_red = np.array([0, 100, 150]) #150
        upper_red = np.array([10, 255, 255])

        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

        # green/blue mask: green (hue=150) and blue (hue=200)
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
        return bounding_boxes[:2]

    def __boundingBoxesAroundContours(self, contours):
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

    def infoAboutDot(self):
        row = []
        row.append(self.boxAroundDot.centerPoint().x)
        row.append(self.boxAroundDot.centerPoint().y)
        row.append(self.boxAroundDot.topLeft.x)
        row.append(self.boxAroundDot.topLeft.y)
        row.append(self.boxAroundDot.bottomRight.x)
        row.append(self.boxAroundDot.bottomRight.y)
        row.append(self.boxAroundDot.diagonal())

        return row

    def __UNUSED_findBoundingBox(self):
        #https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html#gsc.tab=0

        image_with_boxes = np.copy(self.__getImage())

        bounding_boxes = []
        if self.redDot1.dotWasDetected():
            bounding_boxes.append(self.redDot1.boxAroundDot)
        if self.redDot2.dotWasDetected():
            bounding_boxes.append(self.redDot2.boxAroundDot)

        for box in bounding_boxes:
            c = [box.topLeft.x, box.bottomRight.x, box.bottomRight.x, box.topLeft.x, box.topLeft.x]
            r = [box.bottomRight.y, box.bottomRight.y, box.topLeft.y, box.topLeft.y, box.bottomRight.y]
            rr, cc = polygon_perimeter(r, c, image_with_boxes.shape)
            image_with_boxes[rr, cc] = 1  # set color white
        return image_with_boxes


    def __UNUSED_findBrightestSpot(self, image):
        # https://www.pyimagesearch.com/2014/09/29/finding-brightest-spot-image-using-python-opencv/
        orig = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        radius_ = 37
        gray = cv2.GaussianBlur(gray, (radius_, radius_), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        image = orig.copy()
        cv2.circle(image, maxLoc, radius_, (255, 0, 0), 2)
        #print "brigtest spot maxLoc"
        #print maxLoc
        #print maxVal
        #imageWin.showWindowAndWaitForClick(image)
