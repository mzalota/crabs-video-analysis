import cv2
import numpy as np

from lib.Image import Image


############# DETECTORS AND DESCRIPTORS #################

class PointDetector:
    __lo_ratio = 0.8
    __ransac_thresh = 10

    def __init__(self, debug_mode):
        self.__show_debug = debug_mode
        pass


    def __detect_keypoints(self, image: Image):
        gray = cv2.cvtColor(image.asNumpyArray(), cv2.COLOR_RGB2GRAY)
        detector = cv2.ORB_create()
        kps, descript = detector.detectAndCompute(gray, None)
        kps = np.float32([kp.pt for kp in kps])
        return (kps, descript)


    def __match_keypoints(self, des1, des2, ratio):
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

    def __getGoodKps(self, kpsA, kpsB, matches, status):
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


    def __estimate_inliers(self, matches, kpsA, kpsB, reprojThresh):
        if matches is not None:
            ptsA = np.float32([kpsA[i] for i in matches[:,1]])
            ptsB = np.float32([kpsB[i] for i in matches[:,0]])
            (H, status) = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, reprojThresh)
            return (matches, H, status)
        else:
            return None


    def __draw_matches(self, imageA, imageB, kpsA, kpsB, matches, status):
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

    def calculate_keypoints(self, image1: Image, image2: Image):

        frame1 = image1.asNumpyArray()
        frame2 = image2.asNumpyArray()

        kps1, ds1 = self.__detect_keypoints(image1)
        kps2, ds2 = self.__detect_keypoints(image2)

        matcher = self.__match_keypoints(ds1, ds2, self.__lo_ratio)

        ret = self.__estimate_inliers(matcher, kps1, kps2, self.__ransac_thresh)
        if ret is None:
            return False

        matches, H, status = ret

        ptsA, ptsB = self.__getGoodKps(kps1, kps2, matches, status)

        sh_f = self.__draw_matches(frame1, frame2, kps1, kps2, matches, status)
        sh_f = cv2.resize(sh_f, (1024, 400))
        shifted_frame = cv2.warpPerspective(frame2, H, ((image1.width()), (image1.height())))

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

    def absolute_motion(self):
        """
        Function to help estimate, if there is enough motion between frames
        to perform stereo 3d recostruction
        """
        return np.average(np.linalg.norm(self.points_B() - self.points_A(), axis=1))