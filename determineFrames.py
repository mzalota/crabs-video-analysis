import cv2
from pandas.compat.numpy import np

from Frame import Frame
from ImageWindow import ImageWindow
from VelocityDetector import VelocityDetector
from VideoStream import VideoStream
from common import Point, Box

rootDirectory = "C:/workspaces/AnjutkaVideo/output/"

print(cv2.__version__)
cv2.startWindowThread()

velocityDetector = VelocityDetector()
vf = None
#imageWin = ImageWindow("mainWithRedDots", Point(700, 200))
imageWin2 = ImageWindow.createWindow("topSubimage",Box(Point(0,0),Point(960,740)))

videoStream = VideoStream('C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/V3__R_20180915_205551.avi')


def processFrame(nextFrame, frame, prevFrame):
    print 'Read a new frame: ', nextFrameNumber

    try:

        #frame = Frame(count, videoStream)
        #frame.saveImageToFile(rootDirectory)

        image = frame.attachNeighbourFrames(nextFrame, prevFrame, 600)

        imageWin2.showWindowAndWaitForClick(image)


    except Exception as error:
        print ("no more frames to read from video ")
        print('Caught this error: ' + repr(error))


def attachNeighbourFrames(frame, nextFrame, prevFrame):
    image = frame.getImgObj()
    image.drawTextInBox(Box(Point(0, 0), Point(80, 50)), frame.getFrameID())
    prevSubImage = buildPrevImagePart(prevFrame, 400)
    nextSubImage = buildNextImagePart(nextFrame, 400)
    res = np.concatenate((nextSubImage.asNumpyArray(), image.asNumpyArray()))
    res2 = np.concatenate((res, prevSubImage.asNumpyArray()))
    return res2


def buildPrevImagePart(prevFrame, height):
    # boxLine = Box(Point(0, prevImage.height() - 3), Point(prevImage.width(), prevImage.height()))
    # prevImage.drawBoxOnImage(boxLine)
    prevSubImage = prevFrame.getImgObj().topPart(height)
    prevSubImage.drawTextInBox(Box(Point(0, 0), Point(80, 50)), prevFrame.getFrameID())
    return prevSubImage


def buildNextImagePart(nextFrame, height):
    nextSubImage = nextFrame.getImgObj().bottomPart(height)
    nextSubImage.drawTextInBox(Box(Point(0, 0), Point(80, 50)), nextFrame.getFrameID())
    return nextSubImage


import csv

framesFilePath = rootDirectory+"/cutFrames.csv"
nextFrameNumber = 0
frameNumber = 0
prevFrameNumber= 0
with open(framesFilePath) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print('Column names are: '+", ".join(row))
            line_count += 1
        else:
            prevFrameNumber = frameNumber
            frameNumber = nextFrameNumber
            nextFrameNumber = row[0]
            print (nextFrameNumber)

            if nextFrameNumber > 0 and frameNumber > 0:
                prevFrame = Frame(prevFrameNumber, videoStream)
                frame = Frame(frameNumber, videoStream)
                nextFrame = Frame(nextFrameNumber, videoStream)
                processFrame(nextFrame, frame, prevFrame)

            line_count += 1
    print('Processed '+str(line_count)+' lines.')


        # cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file

cv2.destroyAllWindows()
