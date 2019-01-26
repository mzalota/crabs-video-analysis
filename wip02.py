#command to install opencv library so that "import cv2" command does not fail
#python -m pip install opencv-python
#python -m pip install numpy

#from skimage.measure import structural_similarity as ssim
#import matplotlib.pyplot as plt
import numpy as np

import cv2


def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def compare(imageA, imageB):


	cropedB = imageB[0:500, 0:1000].copy()
	
	for i in xrange(0,10,1):
		#M = np.float32([[1,0,0],[0,1,i]])
		#shifted = cv2.warpAffine(frame0,M,(cols,rows))
	
		cropedA = imageA[i:500+i, 0:1000].copy()
		
		print "imageB shape"
		print imageB.shape
		
		print "imageA shape"
		print cropedA.shape
		
		diff = mse(cropedB,cropedA)
		print "hi there diff with shifted by i="+str(i)
		print diff
		
		imageDiff = cropedA-cropedB
		cv2.imshow("diff"+str(i),imageDiff)	
		

		
		
frame0_color = cv2.imread("C:/workspaces/AnjutkaVideo/frames/frame1.jpg")
frame1_color = cv2.imread("C:/workspaces/AnjutkaVideo/frames/frame2.jpg")
#frameDiff = frame1-frame0

frame0 = cv2.cvtColor(frame0_color, cv2.COLOR_BGR2GRAY)
frame1 = cv2.cvtColor(frame1_color, cv2.COLOR_BGR2GRAY)

cv2.imshow("image0",frame0)
cv2.imshow("image1",frame1)
cv2.waitKey(0)

print "shape is"
print frame0.shape

rows,cols= frame0.shape

crop_img0 = frame0[0:500, 0:1000]
crop_img1 = frame1[0:500, 0:1000]

cv2.imshow("image0",crop_img0)
cv2.imshow("image1",crop_img1)


compare(frame0, frame1)




cv2.waitKey(0)



diff = mse(frame0,frame1)
print "hi there diff"
print diff


diff2 = mse(frame0,frame0)
print "hi there diff2"
print diff2

cv2.destroyAllWindows()

