import traceback

from Frame import Frame
from lib.data.SeeFloor import SeeFloor


class VideoToImages:
    #__seefloorGeometry = None
    #__videoStream = None

    def __init__(self, seefloorGeometry, videoStream):
        # type: (SeeFloor, VideoStream) -> VideoToImages
        self.__videoStream = videoStream
        self.__seefloorGeometry = seefloorGeometry

    def getListOfFrameIDs(self):
        # type: (SeeFloor) -> list(int)

        framesLst = list()
        nextFrameID = self.__seefloorGeometry.minFrameID()
        while nextFrameID < self.__seefloorGeometry.maxFrameID():
            framesLst.append(nextFrameID)
            nextFrameID = self.__seefloorGeometry.getNextFrame(nextFrameID)
        framesLst.append(self.__seefloorGeometry.maxFrameID())

        return framesLst

    def __writeToCSVFile(self, logger, frameID):
        heightMM = self.__seefloorGeometry.heightMM(frameID)
        widthMM = self.__seefloorGeometry.widthMM(frameID)
        row = []
        row.append(frameID)
        row.append(heightMM)
        row.append(widthMM)
        logger.writeToFile(row)

    def __processFrame(self, frame, dirpath):
        # type: (Frame, str) -> object
        try:
            imgObj = frame.getImgObj()
            imgObj.drawFrameID(frame.getFrameID())

            imageFileName = frame.constructFilename()
            imageFilePath = dirpath + "/" + imageFileName

            print "writing frame image to file: " + imageFilePath
            imgObj.writeToFile(imageFilePath)

        except Exception as error:
            print ("no more frames to read from video ")
            print('Caught this error: ' + repr(error))
            traceback.print_exc()


    #def __crabsOnFrame(self, frame_id):
    #    # type: (int) -> dict
    #    prev_frame_id = self.__seefloorGeometry.getPrevFrameMM(frame_id)
    #    next_frame_id = self.__seefloorGeometry.getNextFrameMM(frame_id)
    #    markedCrabs = self.__crabsData.crabsBetweenFrames(prev_frame_id, next_frame_id)
    #    return markedCrabs

    def saveFramesToFile(self, lst, dirpath):
        # type: (list(int), str) -> None
        line_count = 0
        for frameID in lst:
            frame = Frame(frameID, self.__videoStream)
            self.__processFrame(frame, dirpath)
            line_count += 1

        print('Processed ' + str(line_count) + ' lines.')


    def saveFramesToCSVFile(self, lst, logger):
        # type: (list(int)) -> None

        row = []
        row.append("frameNumber")
        row.append("heightMM")
        row.append("widthMM")
        logger.writeToFile(row)

        line_count = 0
        for frameID in lst:
            self.__writeToCSVFile(logger, frameID)
            line_count += 1

        print('saveFramesToCSVFile: Processed ' + str(line_count) + ' lines.')
