import numpy as np
import cv2
from matplotlib import pyplot as plt
from lib.imageProcessing.Utils import ImageEnhancer as IE

class Analyzer:  
    """
    A class for determining parameters of current frame: amount of haze, amount of Focus, average brightness.
    Takes 3 channel BGR image as an input.
    """

    def __init__(self, image):
        if len(image.shape) < 3:
            raise ValueError("Image must be 3 channels")
        self.__image = cv2.resize(image[:-100, :, :], (720,480))
        self.__image = IE.eqHist(self.__image)

    def getHazeRatio(self):
        min_img = self.__getMinChannel(self.__image)
        dcp = self.__getDarkChannel(min_img)
        return self.__hazeCoefficient(dcp)

    def getFocusRatio(self):
        return self.__variance_of_laplacian(self.__image)

    def getBrightnessRatio(self):
        return self.__estimateBrighntess(self.__image)

    def getCameraHeight(self, mtx, redDots):
        pass

    ########################## HAZE ESTIMATION ##############################
    # https://www.mdpi.com/2073-4433/13/5/710
    def __getMinChannel(self, img):
        return np.amin(img, 2).astype('uint8')

    def __getDarkChannel(self, img, blockSize=55):
        if blockSize % 2 == 0 or blockSize < 3:
            print('blockSize is not odd or too small')
            return None   
        # Try with erode
        kernel = np.ones((35, 35), 'uint8')
        return cv2.erode(img, kernel, iterations=1)

    def __hazeCoefficient(self, dcp_img):
        if len(dcp_img.shape) > 2:
            print('1-channel image accepted only')
            return None
        fave = np.average(dcp_img.reshape(-1))
        return fave

    ########################## BLUR ESTIMATION ##############################
    # https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
    def __variance_of_laplacian(self, img):
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        lap = cv2.Laplacian(img, cv2.CV_64F).var()
        return lap

    ########################## BRIGHTNESS ESTIMATION ##############################
    # Just an average pixel intensity
    def __estimateBrighntess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)