
from lib.VelocityDetector import VelocityDetector

from lib.VelocityDetectorMultiThreaded import VelocityDetectorMultiThreaded
from lib.VideoStream import VideoStream
from lib.VideoStreamMultiThreaded import VideoStreamMultiThreaded

from lib.Logger import Logger
from lib.data.DriftRawData import DriftRawData
from lib.infra.Configurations import Configurations
from lib.infra.Defaults import Defaults


class DetectDriftsController:
    # DEFAULT_DRIFTS_STEP_SIZE = 2

    def __init__(self, folderStruct):
        self.__folderStruct = folderStruct

    def run(self):
        stepSize = self.step_size()
        print "using stepSize: "+ str(stepSize)

        folderStruct = self.__folderStruct
        # velocityDetector = VelocityDetectorMultiThreaded(folderStruct)
        # videoStream = VideoStreamMultiThreaded(folderStruct.getVideoFilepath())

        if not folderStruct.fileExists(folderStruct.getRawDriftsFilepath()):
            self.__createNewRawFileWithHeaderRow(folderStruct)

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

    def step_size(self):
        # type: () -> int
        configs = Configurations(self.__folderStruct)
        return configs.get_drifts_step_size()

    def __createNewRawFileWithHeaderRow(self, folderStruct):
        driftsFileHeaderRow = VelocityDetector.infoHeaders()

        logger = Logger.openInOverwriteMode(folderStruct.getRawDriftsFilepath())
        logger.writeToFile(driftsFileHeaderRow)
        logger.closeFile()
