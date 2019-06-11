import csv
import traceback

import pandas as pd
import math

from DriftData import DriftData
from Frame import Frame
from Image import Image


class FramesStitcher:
    #__heightOfFrame = None
    #__videoStream = None
    #__driftsFilePath = None
    #__imagesDir = None
    #__framesToStitch = None

    def __init__(self, videoStream, rootDirectory, videoFileName):
        # type: () -> FramesStitcher

        self.__heightOfFrame = 1080
        self.__videoStream = videoStream

        csvFileName = videoFileName + "_toCut.csv"
        self.__driftsFilePath = rootDirectory + "/" + csvFileName
        self.__imagesDir = rootDirectory #+ "/" + videoFileName + "/"

        # Creating an empty Dataframe with column names only
        self.__framesToStitch = pd.DataFrame(columns=['frameNumber'])


    def determineFrames(self):

        dfRaw = pd.read_csv(self.__driftsFilePath, delimiter="\t", na_values="(null)")
        dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum

        driftData = DriftData(dfRaw)
        self.__constructFramesToStitch(driftData)

        return self.__framesToStitch

    def __constructFramesToStitch(self, driftData):

        nextFrameID = driftData.getFrameID(0)
        while nextFrameID < driftData.maxFrameID():
            #print ("nextFrameID", nextFrameID)
            self.__addNextFrame(nextFrameID)
            nextFrameID = driftData.getNextFrame(self.__heightOfFrame, nextFrameID)
        self.__addNextFrame(driftData.maxFrameID())

    def __addNextFrame(self, frameID):
        self.__framesToStitch = self.__framesToStitch.append({'frameNumber': int(frameID)}, ignore_index=True)


    def processFrame(self, nextFrame, frame, prevFrame):
        #print 'Read a new frame: ', nextFrame.getFrameID()
        try:

            #frame.saveImageToFile(rootDirectory+"/"+videoFileName+"/")
            #frame.saveCollageToFile(rootDirectory+"/"+videoFileName+"/")

            #image = frame.attachNeighbourFrames(nextFrame, prevFrame, 800)
            image = frame.attachNeighbourFrames(nextFrame, prevFrame, 300)
            imgObj = Image(image)

            imageFilePath = frame.constructFilePath(self.__imagesDir)
            print "writing frame image to file: " + imageFilePath
            imgObj.writeToFile(imageFilePath)

            #imageWin2.showWindowAndWaitForClick(image)

        except Exception as error:
            print ("no more frames to read from video ")
            print('Caught this error: ' + repr(error))
            traceback.print_exc()

    def saveFramesToFile(self):

        framesToSaveToFile = self.determineFrames()

        line_count = 0
        for index in range(len(framesToSaveToFile.index) - 2):

            prevFrameNumber = framesToSaveToFile['frameNumber'][index]
            frameNumber = framesToSaveToFile['frameNumber'][index + 1]
            nextFrameNumber = framesToSaveToFile['frameNumber'][index + 2]

            if nextFrameNumber > 0 and frameNumber > 0:
                prevFrame = Frame(prevFrameNumber, self.__videoStream)
                frame = Frame(frameNumber, self.__videoStream)
                nextFrame = Frame(nextFrameNumber, self.__videoStream)
                self.processFrame(nextFrame, frame, prevFrame)

            line_count += 1
        print('Processed ' + str(line_count) + ' lines.')