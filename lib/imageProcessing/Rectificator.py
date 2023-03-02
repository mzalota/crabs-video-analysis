from lib.imageProcessing.Utils import PointDetector as PD
from lib.imageProcessing.Utils import ImageEnhancer as IE
from lib.VideoStream import VideoStream
import numpy as np
import cv2

class Rectificator:

    def __init__(self, video_stream: VideoStream, frameID):
        self.__vs = video_stream
        self.__frameID = frameID
        self.__vs.setUndistortDefault() # Ensure that frame is undistorted and cropped
        self.__image_to_rectify = self.__vs.readFromVideoCapture(frameID)
        self.__mtx = self.__vs.getCalibrationMatrix()
        self.__dst = self.__vs.getDistortionCoefficients()
        # By default scale 4K video dowm 4 times
        self.__scale_factor = 0.25
        self.__abs_motion_threshold = 50.0
        self.__init_frame_step = 10
        self.__frame_step_size = 2
        self.__show_debug = True

    @staticmethod
    def calculateAbsoluteMotion(ptsA, ptsB):
        """
        Function to help estimate, if there is enough motion between frames
        to perform stereo 3d recostruction
        """
        return np.average(np.linalg.norm(ptsB - ptsA, axis=1))

    @staticmethod
    def rotMatrixFromNormal(a,b,c):
        # a,b,c - coordinates of Z component of rotation
        # Get Z component of rotation
        len_Z = np.sqrt(a*a + b*b + c*c)
        a = a / len_Z
        b = b / len_Z
        c = c / len_Z

        Z = (a, b, c) if c > 0 else (-a, -b, -c)
        
        # Get Y component of rotation from assumption
        # that Y perpendicular to Z and x component of Y is zero
        yy = np.sqrt(1 / (1 + b*b / (c*c)))
        xy = 0.0
        zy = -b * yy / c
        Y = (xy, yy, zy)
        
        # Get X component of rotation
        X = np.cross(Y, Z)
        
        ret = np.vstack((X,Y,Z)).transpose()
        
        return ret

    def setScale(self, value):
        if value > 0.0:
            self.__scale_factor = value

    def computeTranslationVector(self, kpsA, kpsB):
        """
        Calculation of translation vetor of camera between two images,
        assuming camera tranlsates only, not rotates.
        Based on vanishing point
        """
        # Intrinsic parameters
        mtx = self.__mtx * self.__scale_factor
        mtx[-1, -1] = 1.0
        fx = mtx[0, 0]
        fy = mtx[1, 1]
        f = (fx + fy)/2
        cx = mtx[0, -1]
        cy = mtx[1, -1]

        # Matrix for vanihing point calc
        equation_matrix = []
        for X1, X2 in zip(kpsA, kpsB):
            x1, y1, x2, y2 = [*X1, *X2]
            x1 = x1 - cx
            x2 = x2 - cx
            y1 = y1 - cy
            y2 = y2 - cy

            # Calculate coefficients for translation vector calc
            # Params for VP
            a = y2 - y1
            b = x1 - x2
            c = x2*y1 - x1*y2
            equation_matrix.append([a, b, c])

        equation_matrix = np.array(equation_matrix)
        (u, d, v) = np.linalg.svd(equation_matrix)
        v = v.transpose()
        x = v[0,-1]
        y = v[1,-1]
        z = v[2,-1]
        print( 'Vanishing point calculated: ' + str([x,y,z]))
        vanish_point = (int(x/z), int(y/z))
        sqr = np.sqrt(x*x + y*y + z*z)

        # Estimate sign of T-vector
        directions = []
        x_dirs = []
        y_dirs = []
        for X1, X2 in zip(kpsA, kpsB):
            x1, y1, x2, y2 = [*X1, *X2]
            directions.append( (x2-x1)*(vanish_point[0] - x1) + (y2-y1)*(vanish_point[1] - x1) )
            x_dirs.append(x2-x1)
            y_dirs.append(y2-y1)
            
        x_sign = np.sign(np.average(x_dirs))
        y_sign = np.sign(np.average(y_dirs))
        z_sign = np.sign(np.average(directions))

        # Calculate T-vector
        tx = x/sqr
        ty = y/sqr
        tz=  z*f/sqr

        # Place right sign with respect to most component
        if tz**2/(tx*tx + ty*ty) > 1:
            # Replace with Z sign
            if np.sign(tz) != z_sign:
                tx = -tx
                ty = -ty
                tz = -tz
        elif np.sign(tx) != x_sign:
            # Replace with X sign
            if np.sign(tx) * x_sign < 0:
                tx = -tx
                ty = -ty
                tz = -tz
        else:
            # Replace with Y sign
            if np.sign(ty) != y_sign:
                tx = -tx
                ty = -ty
                tz = -tz  

        return np.float32([tx, ty, tz])

    def rotateImagePlane(self, img, R):
        """
        Rotation of image plane based on formula
        X' = RX - RD + D
        where X = K_inv*(u,v,1)
        (u', v', 1) = KX'
        """
        K = self.__mtx
        
        # Load intrinsic and invert it
        K_inv = np.linalg.inv(K)

        # Augmented inverse for further mtx multiplication
        K_inv1 = np.vstack((K_inv, np.array([0,0,1])))

        # Z distance constant, 1
        d = np.array([0,0,1]).transpose()

        # Calculate translation vector
        t = (d - R.dot(d)).reshape((3,1))
        R1 = np.hstack((R, t))

        # Calc result homography
        matrix = K @ R1 @ K_inv1
        
        # Rotate image
        tf_img = cv2.warpPerspective(img, np.linalg.inv(matrix), (img.shape[1], img.shape[0]))
        
        # return transformed image
        return cv2.normalize(tf_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    def triangulateMatchedPoints(self, ptsA, ptsB, R, T):
        """
        Return: points in 3D estimated from 2 views
        """
        mtx = self.__mtx * self.__scale_factor
        mtx[-1, -1] = 1.0
        proj_mtx01 = np.zeros((3,4))
        proj_mtx01[:3,:3] = np.identity(3)
        proj_mtx01 = mtx @ proj_mtx01

        proj_mtx02 = np.zeros((3,4))
        proj_mtx02[:3,:3] = R
        proj_mtx02[:, -1] = T.transpose()
        proj_mtx02 = mtx @ proj_mtx02

        return cv2.triangulatePoints(proj_mtx01, proj_mtx02,
                                        ptsA.transpose(),
                                        ptsB.transpose())

    def estimateAveragePlane(self, points3d):
        calib_points = (points3d / points3d[-1, :]).transpose()

        _, _, v = np.linalg.svd(calib_points)
        v = v.transpose()
        a, b, c, d = v[:, -1]
        if c < 0:
            a, b, c, d = [-element for element in (a,b,c,d)]
        nomal_abs = np.sqrt(a*a + b*b + c*c)
        return np.float32([a/nomal_abs, b/nomal_abs, c/nomal_abs])

    def estimateRectifyStepDirection(self, frame_step):
        # By default step is positive, but if the video is close to end, make it negative instead
        if self.__frameID + frame_step > self.__vs.num_of_frames():
            return -frame_step
        return frame_step
        

    def run(self, lo_ratio=0.8, ransac_thresh=10):
        print('Attempt to rectify current frame')
        motion = 0.0
        step = self.__init_frame_step
        self.__vs.setCropped(False)
        self.__vs.setUndistorted(True)

        frame1 = self.__vs.readFromVideoCapture(self.__frameID)
        frame1 = IE.scaleImage(frame1, self.__scale_factor)
        frame1 = IE.eqHist(frame1)
        
        h,w = frame1.shape[:2]
        kps1, ds1 = PD.detectKeypoints(frame1)
        iteration = 0

        while motion < self.__abs_motion_threshold and iteration < 20:
            step = self.estimateRectifyStepDirection(step)

            frame2_ID = self.__frameID + step
            frame2 = self.__vs.readFromVideoCapture(frame2_ID)
            frame2 = IE.scaleImage(frame2, self.__scale_factor)
            frame2 = IE.eqHist(frame2)

            kps2, ds2 = PD.detectKeypoints(frame2)
            matcher = PD.matchKeypoints(ds1, ds2, lo_ratio)
            ret = PD.estimateInliers(matcher, kps1, kps2, ransac_thresh)

            if ret is None:
                print('None returned from matcher')
                step += self.__frame_step_size
                iteration += 1
                continue
            matches, H, status = ret

            if self.__show_debug:
                sh_f = PD.drawMatches(frame1, frame2, kps1, kps2, matches, status)
                sh_f = cv2.resize(sh_f, (1024, 400))
                shifted_frame = cv2.warpPerspective(frame2, H, (w,h))
                cv2.imshow("WARP", frame1)
                cv2.waitKey(300)
                cv2.imshow("WARP",shifted_frame)
                cv2.waitKey(300)
                cv2.imshow('Matches', sh_f)
                cv2.waitKey(300)
                cv2.destroyWindow('WARP')
                cv2.destroyWindow('Matches')

            ptsA, ptsB = PD.getGoodKps(kps1, kps2, matches, status)
            motion = self.calculateAbsoluteMotion(ptsA, ptsB)
            print(f'Motion between frame {self.__frameID} and {frame2_ID} is {motion}')
            step += self.__frame_step_size

        if motion == 0.0:
            print('Unable to rectify current frame: no motion detected')
            return None

        # Calculate translation vector
        try:
            # We assume no rotation between frames, only translation
            rotation = np.identity(3)
            translation = self.computeTranslationVector(ptsA, ptsB)
        except(TypeError, np.linalg.LinAlgError):
            print('Unable to rectify current frame: can not estimate translation vector')
            return None

        # Triangulate points and calculate plane
        points3D = self.triangulateMatchedPoints(ptsA, ptsB, rotation, translation)
        plane_normal = self.estimateAveragePlane(points3D)
        rot_mtx = self.rotMatrixFromNormal(*plane_normal)
        res_img = self.rotateImagePlane(self.__image_to_rectify, rot_mtx)
        res_img = IE.scaleImage(res_img, 0.25)
        cv2.imshow('Rectified', res_img)
        cv2.waitKey(2000)
        cv2.destroyWindow('Rectified')



        
            
