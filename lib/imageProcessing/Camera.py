from __future__ import annotations

import glob
#from os import getcwd

import cv2
import numpy as np

from lib.Frame import Frame
from lib.model.Image import Image
from lib.model.Point import Point
from lib.model.Vector import Vector


#https://learnopencv.com/understanding-lens-distortion/

class Camera:
    __instance = None

    def __init__(self, frame_width: int, frame_height: int):
        self.__frame_width = frame_width
        self.__frame_height = frame_height

        if Frame.is_high_resolution(frame_width):
            print("Loading 4k Camera matrices")
            self.__read_matrices("4K")
        else:
            print("Loading Full_HD_Kara_Sea Camera matrices")
            self.__read_matrices("Full_HD_Kara_Sea")

    def __read_matrices(self, subdir: str):
        filename_mask_mtx = 'resources/CAMERA/' + subdir + '/*mtx.npy'
        mtx_glob = glob.glob(filename_mask_mtx)
        # print("mtx_glob", mtx_glob, "filename_mask_mtx", filename_mask_mtx)
        self.__mtx = np.load(mtx_glob[0])

        # print("self.__mtx is ", self.__mtx)
        # self.__mtx for 4K camera is
        # [[2.34308081e+03 0.00000000e+00 1.56529667e+03]
        #  [0.00000000e+00 2.34541467e+03 9.68545150e+02]
        #  [0.00000000e+00 0.00000000e+00 1.00000000e+00]]

        # self.__mtx for Full_HD_Kara_Sea camera is
        # [[1.37975571e+03 0.00000000e+00 9.72820171e+02]
        #  [0.00000000e+00 1.37404560e+03 5.96419357e+02]
        #  [0.00000000e+00 0.00000000e+00 1.00000000e+00]]


        dst_glob = glob.glob('resources/CAMERA/'+subdir+'/*dst.npy')
        self.__dst = np.load(dst_glob[0])

        # print("self.__dst is ", self.__dst)
        # self.__dst  for 4K camera is:
        # [[-0.30592777  0.2554346  -0.00322515 -0.00050018 -0.1366279 ]]
        # self.__dst  for Full_HD_Kara_Sea camera is:
        # [[-0.30329438  0.20865141 - 0.00037175 - 0.00374731 - 0.08253806]]

    @staticmethod
    def create() -> Camera:
        return Camera.__instance

    @staticmethod
    def initialize(video_stream) -> None:
        frame_width = video_stream.frame_width()
        frame_height = video_stream.frame_height()
        print("Camera.initialize: width, height:", frame_width, frame_height)

        Camera.__instance = Camera(frame_width, frame_height)

    @staticmethod
    def initialize_4k() -> None:
        Camera.__instance = Camera(Frame._FRAME_WIDTH_HIGH_RES, Frame._FRAME_HEIGHT_HIGH_RES)

    def center_point(self) -> Point:
        return Point(int(self.frame_width() / 2), int(self.frame_height() / 2))

    def frame_height(self) -> int:
        return self.__frame_height

    def frame_width(self) -> int:
        return self.__frame_width

    def distortion_at_center(self) -> Vector:
        point = self.get_optical_center()
        return self.distortion_at_point_vector(point)

    def distortion_at_point_vector(self, point: Point) -> Vector:
        if point is None:
            return 1
        point_away_1 = point.translate_by_xy(-10, -10)
        point_away_2 = point.translate_by_xy(10, 10)
        x1, y1 = self.__undistort_point_internal(point_away_1, self.__mtx, self.__dst)
        x2, y2 = self.__undistort_point_internal(point_away_2, self.__mtx, self.__dst)

        x_diff = abs(x1 - x2)
        y_diff = abs(y1 - y2)
        x_distortion = x_diff / abs(point_away_1.x - point_away_2.x)
        y_distortion = y_diff / abs(point_away_1.y - point_away_2.y)

        # if (x_diff>20 or y_diff > 20):
        #     print("STRECHING", x_diff, y_diff, str(point_away_1), str(point_away_2),x1,y1,x2,y2)

        return Vector(x_distortion,y_distortion)

    def getCalibrationMatrix(self):
        return self.__mtx

    def getDistortionCoefficients(self):
        return self.__dst

    def undistort_image(self, image: Image, crop_image=False) -> Image:
        image_dimensions = (image.width(), image.height())

        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.__mtx, self.__dst, image_dimensions, 1, image_dimensions)
        ret = cv2.undistort(image.asNumpyArray(), self.__mtx, self.__dst, None, newcameramtx)
        if crop_image:
            x, y, w1, h1 = roi
            ret = ret[y:y + h1, x:x + w1]
            ret = cv2.resize(ret, image_dimensions)
        return Image(ret)

    def undistort_point(self, point: Point):
        if point is None:
            return None

        x,y = self.__undistort_point_internal(point, self.__mtx, self.__dst)
        return Point(int(x), int(y))

    def __undistort_point_internal(self, point, mtx, dst):
        image_size = ((self.__frame_width), (self.__frame_height))
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dst, image_size, 1, image_size)

        points = np.float32(np.array([(point.x, point.y)])[:, np.newaxis, :])
        undistorted_pts = cv2.undistortPoints(points, mtx, dst, P=newcameramtx)

        x = undistorted_pts[0][0][0]
        y = undistorted_pts[0][0][1]
        return x, y

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
