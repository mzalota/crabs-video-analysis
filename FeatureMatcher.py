import cv2
import numpy


class FeatureMatcher:

    def highlightMatchedFeature(self, img_rgb, template):

        fm = FeatureMatcher()

        #https: // www.geeksforgeeks.org / template - matching - using - opencv - in -python /
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