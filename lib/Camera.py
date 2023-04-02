import glob
import cv2
import numpy as np

from lib.common import Point


class Camera:
    def __init__(self):
        self.__mtx = np.load(glob.glob('resources/CAMERA/*mtx.npy')[0])
        self.__is_cropped = True
        self.__dst = np.load(glob.glob('resources/CAMERA/*dst.npy')[0])

    def undistortImage(self, image):
        h, w = image.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.__mtx, self.__dst, (w, h), 1, (w, h))
        ret = cv2.undistort(image, self.__mtx, self.__dst, None, newcameramtx)
        if self.__is_cropped:
            x, y, w1, h1 = roi
            ret = ret[y:y + h1, x:x + w1]
            ret = cv2.resize(ret, (w, h))
        return ret

    def distance_to_object(self, size_of_object_in_pixels, metric_size_of_object):
        #depth is the length along z-axis of object's projection (if object is right at the center of image, then this is the distance from camera lens's center to this object)
        #Zc on this diagram: https://miro.medium.com/v2/resize:fit:1100/format:webp/1*owK4O-NkFj-xFlCAFMzX7w.jpeg
        #see https://towardsdatascience.com/what-are-intrinsic-and-extrinsic-camera-parameters-in-computer-vision-7071b72fb8ec
        return self._get_focal_length_px() * metric_size_of_object / size_of_object_in_pixels

    def _get_focal_length_px(self) -> float:
        # Focal Length is the distance from center of the camera to the sensor. (for this camera, the focal point of the lens is at a distance that is equal 2343 pixels on the sensor... how many nanometers wide is a single pixel sensor on the camera's light sensor array)
        # (if camera has adjustible focus then focal length of camera is distance when focus is set to infinity)
        # Focal Length is in "mtx" matrix in (x0,y0) position and also in (x1,y1) position. See: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
        # we return value from (x0,y0) position
        return self.__mtx[0, 0]

    def get_optical_center(self) -> Point:
        # optical center is the pixel in image where the light that passes through camera len's center ends up hitting the sensor.
        # for example this camera is off from the geometrical center by (-29, 55) pixels
        center_x = self.__mtx[0, 2]
        center_y = self.__mtx[1, 2]
        return Point(center_x, center_y)

    def getCalibrationMatrix(self):
        return self.__mtx

    def getDistortionCoefficients(self):
        return self.__dst
