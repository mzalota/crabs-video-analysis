import cv2

from lib.Frame import Frame
from lib.model.Image import Image
from lib.model.Box import Box
from lib.model.Vector import Vector
from lib.model.Point import Point


class SeeFloorSection:
    #__threshold_for_matching = 0.6
    #__startingBox

    #__topLeftPoints
    #__frameIDs
    #__frames
    #__startingBox

    def __init__(self, frame, box):
        self.__threshold_for_matching = 0.6
        self.__startingBox = box
        self.__frameIDs = list()
        self.__frames = dict()
        self.__topLeftPoints = dict()
        self.__recordFeatureLocationOnFrame(frame, box.topLeft)


    def box_around_feature(self) -> Box:
        max_frame_id = max(self.__frameIDs)
        return self.__boxAroundFeatureForFrame(max_frame_id)

    def number_of_detections(self):
        return len(self.__topLeftPoints)

    def drift_was_detected(self):
        numOfFrames = len(self.__topLeftPoints)
        if numOfFrames <= 1:
            return False
        else:
            return True

    def get_detected_drift(self) -> Vector:
        if not self.drift_was_detected():
            return None

        numOfFrames = len(self.__topLeftPoints)

        lastFrame = self.__frameIDs[numOfFrames-1]
        beforeLastFrame = self.__frameIDs[numOfFrames-2]

        lastPoint = self.__topLeftPoints[lastFrame]
        beforeLastPoint = self.__topLeftPoints[beforeLastFrame]
        driftVector = Vector(lastPoint.x-beforeLastPoint.x, lastPoint.y-beforeLastPoint.y)

        return driftVector

    def __defaultBoxAroundFeature(self):
        box = Box(self.__getTopLeft(),
                      Point(self.__getTopLeft().x + self.__startingBox.width(),
                            self.__getTopLeft().y + self.__startingBox.hight()))
        return box

    def __boxAroundFeatureForFrame(self, frameID: int) -> Box:
        topLeftPoint = self.__getTopLeftForFrame(frameID)
        box = Box(topLeftPoint,
                  Point(topLeftPoint.x + self.__startingBox.width(),
                        topLeftPoint.y + self.__startingBox.hight()))
        return box

    def __getTopLeft(self):
        return self.__getTopLeftForFrame(self.__get_max_frame_id())

    def __getTopLeftForFrame(self, frameID):
        if len(self.__topLeftPoints) < 1:
            return None

        if frameID not in (self.__topLeftPoints):
            return None

        return self.__topLeftPoints[frameID]

    def __recordFeatureLocationOnFrame(self, frame: Frame, topLeftPoint: Point) -> None:
        self.__frameIDs.append(frame.getFrameID())
        self.__topLeftPoints[frame.getFrameID()] = topLeftPoint
        self.__frames[frame.getFrameID()] = frame

    def __get_last_image(self) -> Image:
        return self.__get_image_on_frame(self.__get_max_frame_id())

    def __get_image_on_frame(self, frameID: int)->Image:
        if len(self.__frames)<1:
            return None

        if frameID not in (self.__frames):
            return None

        frame = self.__frames[frameID]
        imgObj = frame.getImgObj()
        img = imgObj.subImage(self.__boxAroundFeatureForFrame(frameID))
        return img

    def get_center_point(self) -> Point:
        box = self.__defaultBoxAroundFeature()
        return box.topLeft.calculateMidpoint(box.bottomRight)

    def findLocationInFrame(self, frame: Frame)->Point:
        newLocation = self.__find_location_of_sub_image(frame.getImgObj(), self.__get_last_image())
        if newLocation:
            self.__recordFeatureLocationOnFrame(frame, newLocation)
        return newLocation

    def __find_location_of_sub_image(self, whereToSearch: Image, whatToFind: Image) -> Point:
        image = whereToSearch.asNumpyArray()
        subImage = whatToFind.asNumpyArray()

        if subImage is None:
            return None

        # Algorithm is described here: https: // www.geeksforgeeks.org / template - matching - using - opencv - in -python /

        # Convert image and subImage to grayscale
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        subImage_gray = cv2.cvtColor(subImage, cv2.COLOR_BGR2GRAY)

        # Perform match operations.
        res = cv2.matchTemplate(img_gray, subImage_gray, cv2.TM_CCOEFF_NORMED)

        #determine which rechtangle on the image is the best fit for subImage (has the highest correlation)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        self.__correlation = max_val

        if max_val < self.__threshold_for_matching:
            # If the best matching box still has correlation below the "threshold" then declare defeat -> we could not find a match for subImage on this image
            return None

        # get w and h, so that we can reconstruct the box
        d, w, h = subImage.shape[::-1]
        topLeft = Point(max_loc[0], max_loc[1])
        Point(topLeft.x + w, topLeft.y + h)

        return topLeft

    def __get_max_frame_id(self):
        # type: () -> String
        return max(self.__frameIDs)
