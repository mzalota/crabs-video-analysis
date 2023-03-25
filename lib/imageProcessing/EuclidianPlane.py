import cv2
import numpy as np

from lib.Camera import Camera
from lib.Image import Image
from lib.common import Point

class EuclidianPlane:
    def __init__(self, ptsA, ptsB, scale_factor):
        self.__ptsA = ptsA
        self.__ptsB = ptsB
        self.__scale_factor = scale_factor

        camera = Camera()
        self.__mtx = camera.getCalibrationMatrix()
        self.__dst = camera.getDistortionCoefficients()

        self.__plane_normal = None

    @staticmethod
    def __rotate_matrix_from_normal(a, b, c):
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

    def __compute_translation_vector(self, kpsA, kpsB):
        """
        Calculation of translation vector of camera between two images,
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

    def __rotate_image_plane(self, image: Image, R):
        """
        Rotation of image plane based on formula
        X' = RX - RD + D
        where X = K_inv*(u,v,1)
        (u', v', 1) = KX'
        """
        img = image.asNumpyArray()

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

    def __triangulate_matched_points(self, ptsA, ptsB, R, T):
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

    def __estimateAveragePlane(self, points3d):
        calib_points = (points3d / points3d[-1, :]).transpose()

        _, _, v = np.linalg.svd(calib_points)
        v = v.transpose()
        a, b, c, d = v[:, -1]
        if c < 0:
            a, b, c, d = [-element for element in (a,b,c,d)]
        nomal_abs = np.sqrt(a*a + b*b + c*c)
        return np.float32([a/nomal_abs, b/nomal_abs, c/nomal_abs])

    def __rectifyPoint(self, pt):
        mtx = self.__mtx
        normal = self.__plane_normal
        R = self.__rotate_matrix_from_normal(*normal)
        K = mtx.copy()
        K_inv = np.vstack((np.linalg.inv(K), np.array([0,0,1])))
        d = np.array([0,0,1]).transpose()
        t = (d - R.dot(d)).reshape((3,1))
        R1 = np.hstack((R, t))
        matrix = K @ R1 @ K_inv
        matrix = np.linalg.inv(matrix)
        ptN = np.append(pt[0], 1.0)
        ptNN = matrix @ ptN
        recPt = (ptNN[0] / ptNN[-1], ptNN[1] / ptNN[-1])
        return recPt

    def __undistortPoint(self, point, width, height):
        mtx = self.__mtx
        dst = self.__dst
        points = np.float32(np.array(point)[:, np.newaxis, :])
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dst, (width, height), 1, (width, height))
        undistorted_pts = cv2.undistortPoints((point), mtx, dst, P=newcameramtx)
        return undistorted_pts[0]

    def __compute_normal(self):
        ptsA = self.__ptsA
        ptsB = self.__ptsB
        # We assume no rotation between frames, only translation (hence rotation is just an identity matrix)
        rotation = np.identity(3)
        translation = self.__compute_translation_vector(ptsA, ptsB)

        # Triangulate points and calculate plane
        points3D = self.__triangulate_matched_points(ptsA, ptsB, rotation, translation)
        plane_normal = self.__estimateAveragePlane(points3D)
        self.__plane_normal = plane_normal
        return plane_normal

    def rectify_image(self, image_to_rectify: Image) -> Image:
        if self.__plane_normal is None:
            self.__compute_normal()
        plane_normal = self.__plane_normal
        rot_mtx = self.__rotate_matrix_from_normal(*plane_normal)
        res_img = self.__rotate_image_plane(image_to_rectify, rot_mtx)
        return Image(res_img)

    def rectify_point(self, point_to_rectify: Point,  width, height) -> Point:
        if self.__plane_normal is None:
            self.__compute_normal()
        plane_normal = self.__plane_normal
        point = (point_to_rectify.x, point_to_rectify.y)
        undist_point = self.__undistortPoint(point, width, height)
        rec_point = self.__rectifyPoint(undist_point)
        ret_point = Point(rec_point[0], rec_point[1])
        return rec_point

    def get_plane_normal(self):
        return self.__plane_normal

