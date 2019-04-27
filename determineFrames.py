import math

import cv2
from pandas.compat.numpy import np

from Frame import Frame
from ImageWindow import ImageWindow
from VelocityDetector import VelocityDetector
from VideoStream import VideoStream
from common import Point, Box

rootDirectory = "C:/workspaces/AnjutkaVideo/output/"

import csv



framesFilePath = rootDirectory+"/framesInFives.csv"
cutFramesFilePath = rootDirectory+"/cutFrames2.csv"

cutFramesFile = open(cutFramesFilePath, 'wb')

yDrift = 0
frameNumber = 0
prevFrameNumber= 0
cumulativeDrift = 0
printedFrames = 1
prevFrameToUse = 0
with open(framesFilePath) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print('Column names are: '+", ".join(row))
            line_count += 1
        else:
            prevFrameNumber = frameNumber
            prevYDrift = yDrift

            frameNumber = row[0]
            yDrift = float(row[1].replace(",","."))

            prevCumulativeDrift = cumulativeDrift
            cumulativeDrift += yDrift

            driftPerFrame = yDrift/(int(frameNumber)-int(prevFrameNumber))
            #print (frameNumber, yDrift, cumulativeDrift, prevFrameNumber, prevYDrift, prevCumulativeDrift, driftPerFrame)

            nextFrameBreak= 1080*printedFrames
            if cumulativeDrift > (nextFrameBreak):
                pixelsToBacktrack = cumulativeDrift - nextFrameBreak
                framesToBacktrack = pixelsToBacktrack/driftPerFrame
                frameToUse = int(frameNumber)-math.floor(framesToBacktrack)
                frameJump = frameToUse - prevFrameToUse
                print (int(frameToUse), printedFrames, frameJump, cumulativeDrift, pixelsToBacktrack, framesToBacktrack, math.floor(framesToBacktrack))
                printedFrames = printedFrames+1
                prevFrameToUse = frameToUse

                cutFramesFile.write(str(int(frameToUse)) + "\n")
                cutFramesFile.flush()

            line_count += 1
    print('Processed '+str(line_count)+' lines.')

cutFramesFile.close()