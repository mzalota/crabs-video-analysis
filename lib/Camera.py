import glob

import cv2
import numpy as np

from lib.imageProcessing.Utils import ImageEnhancer


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
