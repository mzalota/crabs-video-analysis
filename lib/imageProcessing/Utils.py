import cv2
import numpy as np
from matplotlib import pyplot as plt
from functools import partial
import math

################ IMAGE ENHANCEMENT ###############################

class ImageEnhancer:

    def __init__(self):
        pass

    @staticmethod
    def scaleImage(image, scale_factor):
        new_shape = (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor))
        return cv2.resize(image, new_shape)

    @staticmethod
    def eqHist(image, clache=True, gray_only=False):
        """
        Equalization of image, by default based on CLACHE method
        """
        if gray_only:
            L = image
        else:
            imgHLS = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
            L = imgHLS[:,:,1]
        if clache:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            equ = clahe.apply(L)
        else:
            equ = cv2.equalizeHist(L)

        if gray_only:
            return equ

        imgHLS[:,:,1] = equ
        res = cv2.cvtColor(imgHLS, cv2.COLOR_HLS2BGR)
        return res

    # @staticmethod
    def undistortImage(self, img, mtx, dist, crop=False):
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        ret = cv2.undistort(img, mtx, dist, None, newcameramtx)
        if crop:
            x, y, w1, h1 = roi
            ret = ret[y:y+h1, x:x+w1]
            ret = cv2.resize(ret, (w,h))
        return ret

############# DETECTORS AND DESCRIPTORS #################

class PointDetector:

    def __init__(self):
        pass

    @staticmethod
    def detectKeypoints(image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        detector = cv2.ORB_create()
        kps, descript = detector.detectAndCompute(gray, None)
        kps = np.float32([kp.pt for kp in kps])
        return (kps, descript)

    @staticmethod
    def matchKeypoints(des1, des2, ratio):
        # print('matchKeypoints')
        matcher = cv2.DescriptorMatcher_create('BruteForce')
        try:
            rawMatches = matcher.knnMatch(des1, des2, 2)
        except:
            return None
        # Lowe's ratio test
        matches = []
        for m in rawMatches:
            if len(m) ==2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))
        if len(matches) > 4:
            return np.array(matches)
        else:
            return None

    @staticmethod
    def getGoodKps(kpsA, kpsB, matches, status):
        """
        Filtes keypoints of matched images based on status"""
        pts1, pts2 = [], []
        for ((trainIdx, queryIdx), s) in zip(matches, status):
            # only process the match if the keypoint was successfully
            # matched
            if s == 1:
                ptA = (kpsA[queryIdx][0], kpsA[queryIdx][1])
                ptB = (kpsB[trainIdx][0], kpsB[trainIdx][1])
                pts1.append(ptA)
                pts2.append(ptB)
        return np.array(pts1), np.array(pts2)

    @staticmethod
    def estimateInliers(matches, kpsA, kpsB, reprojThresh):
        if matches is not None:
            ptsA = np.float32([kpsA[i] for i in matches[:,1]])
            ptsB = np.float32([kpsB[i] for i in matches[:,0]])
            (H, status) = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, reprojThresh)
            return (matches, H, status)
        else:
            return None

    @staticmethod
    def drawMatches(imageA, imageB, kpsA, kpsB, matches, status):
        # initialize the output visualization image
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB
        # loop over the matches
        for ((trainIdx, queryIdx), s) in zip(matches, status):
            # only process the match if the keypoint was successfully
            # matched
            if s == 1:
                # draw the match
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)
        # return the visualization
        return vis

