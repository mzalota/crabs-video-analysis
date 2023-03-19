import cv2
import numpy as np
from matplotlib import pyplot as plt
from functools import partial
import math

################ IMAGE ENHANCEMENT ###############################
from lib.Image import Image


class ImageEnhancer:

    def __init__(self):
        pass


    def scaleImage(self, image, scale_factor):
        image = Image(image)
        image.scale_by_factor(scale_factor)
        return image.asNumpyArray()





############# DETECTORS AND DESCRIPTORS #################

class PointDetector:

    def __init__(self):
        pass


    def detectKeypoints(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        detector = cv2.ORB_create()
        kps, descript = detector.detectAndCompute(gray, None)
        kps = np.float32([kp.pt for kp in kps])
        return (kps, descript)


    def matchKeypoints(self, des1, des2, ratio):
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

    def getGoodKps(self, kpsA, kpsB, matches, status):
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


    def estimateInliers(self, matches, kpsA, kpsB, reprojThresh):
        if matches is not None:
            ptsA = np.float32([kpsA[i] for i in matches[:,1]])
            ptsB = np.float32([kpsB[i] for i in matches[:,0]])
            (H, status) = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, reprojThresh)
            return (matches, H, status)
        else:
            return None


    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
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

    def getGoodKeypoints(self, image1: Image, image2: Image, lo_ratio=0.8, ransac_thresh=10):
        image1 = image1.scale_by_factor(self.__scale_factor)
        image1 = image1.equalize()
        frame1 = image1.asNumpyArray()

        height_frame1 = image1.height()
        width_frame1 = image1.width()  # frame1.shape[:2]

        kps1, ds1 = self.detectKeypoints(frame1)


        image2 = image2.scale_by_factor(self.__scale_factor)
        image2 = image2.equalize()
        frame2 = image2.asNumpyArray()

        kps2, ds2 = self.detectKeypoints(frame2)

        matcher = self.matchKeypoints(ds1, ds2, lo_ratio)

        ret = self.estimateInliers(matcher, kps1, kps2, ransac_thresh)
        if ret is None:
            return False

        matches, H, status = ret

        ptsA, ptsB = self.getGoodKps(kps1, kps2, matches, status)

        sh_f = self.drawMatches(frame1, frame2, kps1, kps2, matches, status)
        sh_f = cv2.resize(sh_f, (1024, 400))
        shifted_frame = cv2.warpPerspective(frame2, H, (width_frame1, height_frame1))

        # if ret is None:
        #     print('None returned from matcher')
        #     step += self.__frame_step_size
        #     iteration += 1
        #     continue

        if self.__show_debug:
            cv2.imshow("WARP", frame1)
            cv2.waitKey(300)
            cv2.imshow("WARP", shifted_frame)
            cv2.waitKey(300)
            cv2.imshow('Matches', sh_f)
            cv2.waitKey(300)
            cv2.destroyWindow('WARP')
            cv2.destroyWindow('Matches')

        self.__ptsA = ptsA
        self.__ptsB = ptsB
        return True

    def points_A(self):
        return self.__ptsA

    def points_B(self):
        return self.__ptsB