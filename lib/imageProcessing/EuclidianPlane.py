import cv2
import numpy as np


class EuclidianPlane:
    def __init__(self, ptsA, ptsB, scale_factor, mtx):
        self.__ptsA = ptsA
        self.__ptsB = ptsB
        self.__scale_factor = scale_factor
        self.__mtx = mtx

    def compute_normal(self):
        ptsA = self.__ptsA
        ptsB = self.__ptsB

        # We assume no rotation between frames, only translation (hence rotation is just an identity matrix)
        rotation = np.identity(3)
        translation = self.__compute_translation_vector()

        # Triangulate points and calculate plane
        points3D = self.__triangulate_matched_points(rotation, translation)
        plane_normal = self.__estimateAveragePlane(points3D)

        return plane_normal


    def __compute_translation_vector(self):
        """
        Calculation of translation vector of camera between two images,
        assuming camera tranlsates only, not rotates.
        Based on vanishing point
        """
        kpsA = self.__ptsA
        kpsB = self.__ptsB

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


    def __triangulate_matched_points(self, R, T):
        """
        Return: points in 3D estimated from 2 views
        """
        ptsA = self.__ptsA
        ptsB = self.__ptsB

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
