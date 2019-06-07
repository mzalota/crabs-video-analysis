import cv2

from lib.FramesStitcher import FramesStitcher
from lib.ImageWindow import ImageWindow
from lib.VideoStream import VideoStream
from lib.common import Point, Box

print(cv2.__version__)
cv2.startWindowThread()

#imageWin = ImageWindow("mainWithRedDots", Point(700, 200))
imageWin2 = ImageWindow.createWindow("topSubimage",Box(Point(0,0),Point(960,740)))


#filename = "V6__R_20180915_212238"
filename = "V4__R_20180915_210447"
rootDirectory = "C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
csvFilesDirectory = rootDirectory+"/"+filename+"/"


videoFileName = filename

#videoStream = VideoStream("C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"+videoFileName+".avi")
videoStream = VideoStream(rootDirectory+"/"+videoFileName+".avi")

framesStitcher = FramesStitcher(videoStream, csvFilesDirectory, videoFileName)
#framesToSaveToFile = framesStitcher.determineFrames()
#print("Dataframe Contains:", framesToSaveToFile)

framesStitcher.saveFramesToFile()


cv2.destroyAllWindows()
