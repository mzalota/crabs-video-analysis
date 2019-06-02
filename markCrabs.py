import matplotlib.pyplot as plt
import numpy as np

import cv2


# import the necessary packages
import argparse
import cv2
import math

from Image import Image
from ImageWindow import ImageWindow
from common import Point, Box
import os

#filepath="C:/workspaces/AnjutkaVideo/frames/frame1.jpg"
filepath="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238/V6__R_20180915_212238/seqFrames/frame003717.jpg"

#filename=os.path.splitext(filepath)[0]

filenameFull=os.path.basename(filepath)
filename=os.path.splitext(filenameFull)[0]


directory ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238/V6__R_20180915_212238/seqFrames/"


def processImage(image, imageWin):

	origImage = image.copy()
	foundCrabs = list()
	mustExit = False
	while not mustExit:
		keyPressed = imageWin.showWindowAndWaitForClick(image)

		# if the 'n' key is pressed return
		if keyPressed == ord("n"):
			#print "Pressed N button"
			mustExit = True
		elif keyPressed == ord("r"):
			#print "Pressed R button"
			foundCrabs = list()
			image = origImage.copy()
		else:
			crabBox = getCrabWidth(imageWin, image)
			foundCrabs.append(crabBox)
			#print("foundCrab", str(crabBox), crabBox.diagonal(), str(crabBox.centerPoint()))

	return foundCrabs
	print "Done with this frame"

def getCrabWidth(imageWin, image):
	mainImage = Image(image)
	crabPoint = imageWin.featureCoordiate
	crabImage = mainImage.subImage(crabPoint.boxAroundPoint(200))
	crabWin = ImageWindow.createWindow("crabImage", Box(Point(0, 0), Point(600, 600)))
	crabWin.showWindowAndWaitForTwoClicks(crabImage.asNumpyArray())
	crabWin.closeWindow()
	crabOnMainWindow = crabWin.featureBox.translateCoordinateToOuter(crabPoint.boxAroundPoint(200).topLeft)
	mainImage.drawLine(crabOnMainWindow.topLeft, crabOnMainWindow.bottomRight)

	return crabOnMainWindow

imageWin = ImageWindow("mainWindow", Point(700, 200))

counter = 1
for filename in os.listdir(directory):
	if filename.endswith(".jpg"):
		filepath = os.path.join(directory, filename)
		image = cv2.imread(filepath)
		foundCrabs = processImage(image,imageWin)
		for crab in foundCrabs:
			print("crab", directory, filename, counter, crab.diagonal(),crab.centerPoint().x,crab.centerPoint().y, str(crab.centerPoint()), str(crab))
			counter += 1
		continue
	else:
		print("Skipping some non JPG file", os.path.join(directory, filename))
		continue



exit()

#csvData.append([filepath,x,y])

framesData = [['frame_filepath', 'image_filename', 'distance', 'red_point_1_x', 'red_point_1_y','red_point_2_x', 'red_point_2_y']]
crabsData =[['frame_filepath', 'image_filename', 'crab_id', 'crab_x', 'crab_y']]


import csv	


with open('C:/workspaces/AnjutkaVideo/frames_log.csv', 'wb') as framesFile:
    writer = csv.writer(framesFile,delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(framesData)
framesFile.close()

with open('C:/workspaces/AnjutkaVideo/crabs_log.csv', 'wb') as crabsFile:
    writer = csv.writer(crabsFile,delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(crabsData)
crabsFile.close()
			
	
# close all open windows
cv2.destroyAllWindows()		

