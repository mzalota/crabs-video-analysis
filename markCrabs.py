import pandas as pd
import cv2


from lib.Image import Image
from lib.ImageWindow import ImageWindow
from lib.common import Point, Box
import os

#filepath="C:/workspaces/AnjutkaVideo/frames/frame1.jpg"
#filepath="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V6__R_20180915_212238/V6__R_20180915_212238/seqFrames/frame003717.jpg"

#filename=os.path.splitext(filepath)[0]

#filenameFull=os.path.basename(filepath)
#filename=os.path.splitext(filenameFull)[0]

#videoFileName = "V4__R_20180915_210447"
#videoFileName = "V6__R_20180915_212238"

videoFileName = "V3_R_20180911_170159"
#videoFileName = "V2_R_20180911_165730"

#rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
rootDir ="C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
framesDir =rootDir+"/"+videoFileName+"/seqFrames/"

outputFilePath =rootDir+"/"+videoFileName+"/"+videoFileName+"_crabs.csv"

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

crabsDF = pd.DataFrame(columns=['dir', 'filename', 'crabNumber','crabWidthPixels','crabLocationX','crabLocationY','crabWidthLine'])

crabNumber = 1
for filename in os.listdir(framesDir):

	if filename.endswith(".jpg"):
		filepath = os.path.join(framesDir, filename)
		image = cv2.imread(filepath)
		foundCrabs = processImage(image,imageWin)
		for crab in foundCrabs:
			crabsDF = crabsDF.append({'dir': framesDir, 'filename': filename, 'crabNumber': crabNumber, 'crabWidthPixels': crab.diagonal(), 'crabLocationX': crab.centerPoint().x, 'crabLocationY': crab.centerPoint().y, 'crabWidthLine': crab}, ignore_index=True)

			print("crab", framesDir, filename, crabNumber, crab.diagonal(),crab.centerPoint().x,crab.centerPoint().y, str(crab.centerPoint()), str(crab))
			crabNumber += 1
		continue
	else:
		print("Skipping some non JPG file", os.path.join(framesDir, filename))
		continue

crabsDF.to_csv(outputFilePath, sep='\t')
	
# close all open windows
cv2.destroyAllWindows()		

