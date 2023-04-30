from __future__ import annotations

import glob
#from os import getcwd

import cv2
import numpy as np

from lib.Frame import Frame
from lib.Image import Image
from lib.common import Point


class Camera:
    def __init__(self):
        mtx_glob = glob.glob('resources/CAMERA/*mtx.npy')
        self.__mtx = np.load(mtx_glob[0])

        #print("self.__mtx is ", self.__mtx)
        # self.__mtx is
        # [[2.34308081e+03 0.00000000e+00 1.56529667e+03]
        #  [0.00000000e+00 2.34541467e+03 9.68545150e+02]
        #  [0.00000000e+00 0.00000000e+00 1.00000000e+00]]

        dst_glob = glob.glob('resources/CAMERA/*dst.npy')
        self.__dst = np.load(dst_glob[0])
        #print("self.__dst is ", self.__dst)
        #self.__dst is  [[-0.30592777  0.2554346  -0.00322515 -0.00050018 -0.1366279 ]]

    @staticmethod
    def create_camera_4k() -> Camera:
        camera = Camera()
        #TODO: is this correct frame width and height?
        camera.__frame_width = Frame._FRAME_WIDTH_HIGH_RES
        camera.__frame_height = Frame._FRAME_HEIGHT_HIGH_RES
        return camera

    @staticmethod
    def create_camera_HD() -> Camera:
        camera = Camera()
        #TODO: is this correct frame width and height?
        camera.__frame_width = Frame._FRAME_WIDTH_LOW_RES
        camera.__frame_height = Frame._FRAME_HEIGHT_LOW_RES
        return camera


    def undistort_poinnnnt(self, point: Point):
        return self.undistort_point(point, self.__frame_width, self.__frame_height)

    def undistort_image(self, image: Image, crop_image=False) -> Image:
        image_dimensions = (image.width(), image.height())

        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.__mtx, self.__dst, image_dimensions, 1, image_dimensions)
        ret = cv2.undistort(image.asNumpyArray(), self.__mtx, self.__dst, None, newcameramtx)
        if crop_image:
            x, y, w1, h1 = roi
            ret = ret[y:y + h1, x:x + w1]
            ret = cv2.resize(ret, image_dimensions)
        return Image(ret)

    def undistort_point(self, point: Point, frame_width: int, frame_height: int) -> Point:
        image_size = ((frame_width), (frame_height))
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.__mtx, self.__dst, image_size, 1, image_size)

        points = np.float32(np.array([(point.x, point.y)])[:, np.newaxis, :])
        undistorted_pts = cv2.undistortPoints(points, self.__mtx, self.__dst, P=newcameramtx)

        undistorted_point = Point(int(undistorted_pts[0][0][0]), int(undistorted_pts[0][0][1]))
        return undistorted_point

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
