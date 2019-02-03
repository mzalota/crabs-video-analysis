import cv2
import numpy as np
from skimage import measure

from common import Box, Point


class FeatureMatcher:

    def highlightMatchedFeature(self, img_rgb, template):

        #fm = FeatureMatcher()

        #https: // www.geeksforgeeks.org / template - matching - using - opencv - in -python /
        # Convert it to grayscale
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        # Read the template
        # Store width and heigth of template in w and h
        #print "template.shape[::-1]"
        #print template.shape[::-1]
        d, w, h = template.shape[::-1]
        # Perform match operations.
        res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        # Specify a threshold (it was 0.8)
        threshold = 0.6
        # Store the coordinates of matched area in a numpy array
        loc = np.where(res >= threshold)
        # Draw a rectangle around the matched region.
        newLocation = None
        for pt in zip(*loc[::-1]):
            #print "in highlightMatchedFeature pt is"
            #print pt
            #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
            newLocation = Box(Point(pt[0],pt[1]),Point(pt[0] + w,pt[1] + h))
        #if newLocation is not None:
            #self.drawBoxOnImage(img_rgb, newLocation)

        print "newLocation"
        print newLocation
        return newLocation

    def drawBoxOnImage(self, image, box):
        cv2.rectangle(image, (box.topLeft.x, box.topLeft.y),
                      (box.bottomRight.x, box.bottomRight.y), (0, 255, 0), 2)