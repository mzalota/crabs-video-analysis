import csv
import traceback

import pandas as pd
import math

from DriftData import DriftData
from Frame import Frame
from Image import Image
from lib.SeeFloor import SeeFloor


class FramesStitcher:
    #__heightOfFrame = None
    #__videoStream = None
    #__driftsFilePath = None
    #__imagesDir = None
    #__framesToStitch = None
    FRAME_HEIGHT = 1080

    def __init__(self, folderStructure, videoStream):
        # type: (FolderStructure, VideoStream) -> FramesStitcher

        self.__videoStream = videoStream

        #csvFileName = videoFileName + "_toCut.csv"
        self.__driftsFilePath = folderStructure.getDriftsFilepath() # rootDirectory + "/" + csvFileName
        self.__folderStructure = folderStructure
        self.__seefloorGeometry = SeeFloor.createFromFolderStruct(folderStructure)
        # Creating an empty Dataframe with column names only
        self.__framesToStitch = pd.DataFrame(columns=['frameNumber'])


    def determineFrames(self):
        # type: () -> pd.DataFrame
        dfRaw = pd.read_csv(self.__driftsFilePath, delimiter="\t", na_values="(null)")
        #dfRaw = dfRaw.rename(columns={dfRaw.columns[0]: "rowNum"}) # rename first column to be rowNum

        driftData = DriftData(dfRaw)
        self.__constructFramesToStitch(driftData)

        return self.__framesToStitch

    def __constructFramesToStitch(self, driftData):

        nextFrameID = driftData.minFrameID()
        while nextFrameID < driftData.maxFrameID():
            #print ("nextFrameID", nextFrameID)
            self.__addNextFrame(nextFrameID)
            nextFrameID = driftData.getNextFrame(self.FRAME_HEIGHT, nextFrameID)
        self.__addNextFrame(driftData.maxFrameID())

    def __addNextFrame(self, frameID):
        self.__framesToStitch = self.__framesToStitch.append({'frameNumber': int(frameID)}, ignore_index=True)

    #TODO: This function (an the whole class) has a lot of duplication of ImagesCollage
    def processFrame(self, nextFrame, frame, prevFrame):
        #print 'Read a new frame: ', nextFrame.getFrameID()
        try:

            #frame.saveImageToFile(rootDirectory+"/"+videoFileName+"/")
            #frame.saveCollageToFile(rootDirectory+"/"+videoFileName+"/")

            #image = frame.attachNeighbourFrames(nextFrame, prevFrame, 800)
            #image = frame.attachNeighbourFrames(nextFrame, prevFrame, 300)
            #imgObj = Image(image)
            imgObj = frame.getImgObj()
            imgObj.drawFrameID(frame.getFrameID())

            imageFileName = frame.constructFilename() #self.__imagesDir)

            self.__writeFrameImage(imageFileName, imgObj)

            self.__writeCrabImage(imageFileName, imgObj, frame.getFrameID())

            #imageWin2.showWindowAndWaitForClick(image)

        except Exception as error:
            print ("no more frames to read from video ")
            print('Caught this error: ' + repr(error))
            traceback.print_exc()

    def __writeFrameImage(self, imageFileName, imgObj):
        imageFilePath = self.__folderStructure.getFramesDirpath() + "/" + imageFileName
        print "writing frame image to file: " + imageFilePath
        imgObj.writeToFile(imageFilePath)

    def __writeCrabImage(self, imageFileName, imgObj, frame_id):
        crabs = self.__seefloorGeometry.crabsOnFrame(frame_id)
        if crabs is not None:
            if len(crabs) > 0:
                crabImageFilePath = self.__folderStructure.getCrabFramesDirpath() + "/" + imageFileName
                print ("Crabs on frame ", frame_id, crabs)
                imgObj.writeToFile(crabImageFilePath)

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