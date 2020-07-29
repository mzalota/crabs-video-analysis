
from lib.VelocityDetector import VelocityDetector

from lib.VelocityDetectorMultiThreaded import VelocityDetectorMultiThreaded
from lib.VideoStream import VideoStream
from lib.VideoStreamMultiThreaded import VideoStreamMultiThreaded

from lib.Logger import Logger
from lib.data.DriftRawData import DriftRawData


class DriftsController:

    def createNewRawFileWithHeaderRow(self, folderStruct):
        driftsFileHeaderRow = VelocityDetector.infoHeaders()

        logger = Logger.openInOverwriteMode(folderStruct.getRawDriftsFilepath())
        logger.writeToFile(driftsFileHeaderRow)
        logger.closeFile()

    def run(self, folderStruct):
        stepSize = 2

        # velocityDetector = VelocityDetectorMultiThreaded(folderStruct)
        # videoStream = VideoStreamMultiThreaded(folderStruct.getVideoFilepath())



        if not folderStruct.fileExists(folderStruct.getRawDriftsFilepath()):
            self.createNewRawFileWithHeaderRow(folderStruct)

        logger = Logger.openInAppendMode(folderStruct.getRawDriftsFilepath())

        rawDriftData = DriftRawData(folderStruct)
        maxFrameID = rawDriftData.maxFrameID()
        if maxFrameID > 1:
            startFrameID = maxFrameID + stepSize
        else:
            startFrameID = 5

        #cv2.startWindowThread()
        #imageWin = ImageWindow("mainWithRedDots", Point(700, 200))

        print ("starting processing from frame", startFrameID)

        velocityDetector = VelocityDetector()
        videoStream = VideoStream(folderStruct.getVideoFilepath())
        velocityDetector.runLoop(startFrameID, stepSize, logger, videoStream)

        logger.closeFile()
        #cv2.destroyAllWindows()
