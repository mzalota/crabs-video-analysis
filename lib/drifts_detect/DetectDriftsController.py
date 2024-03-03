from lib.infra.Logger import Logger
from lib.drifts_detect.VelocityDetector import VelocityDetector
from lib.VideoStream import VideoStream
from lib.drifts_interpolate.DriftRawData import DriftRawData
from lib.infra.Configurations import Configurations


class DetectDriftsController:
    # DEFAULT_DRIFTS_STEP_SIZE = 2

    def __init__(self, folderStruct):
        self.__folderStruct = folderStruct


    def run(self):
        stepSize = self.__step_size()
        print("using stepSize: " + str(stepSize))

        folderStruct = self.__folderStruct
        # velocityDetector = VelocityDetectorMultiThreaded(folderStruct)
        # videoStream = VideoStreamMultiThreaded(folderStruct.getVideoFilepath())

        if not folderStruct.fileExists(folderStruct.getRawDriftsFilepath()):
            self.__createNewRawFileWithHeaderRow(folderStruct)

        #TODO: Move this logger to DriftRawData class. Writing should be happening there.
        logger = Logger.openInAppendMode(folderStruct.getRawDriftsFilepath())

        velocityDetector = VelocityDetector(Configurations(folderStruct).is_debug())
        videoStream = VideoStream.instance(folderStruct.getVideoFilepath())

        rawDriftData = DriftRawData(folderStruct)
        maxFrameID = rawDriftData.max_frame_id()
        if maxFrameID > 1:
            startFrameID = maxFrameID+stepSize
        else:
            startFrameID = videoStream.get_id_of_first_frame(stepSize)

        print("starting processing from frame", startFrameID)

        velocityDetector.runLoop(int(startFrameID), stepSize, logger, videoStream)

        logger.closeFile()

    def __step_size(self):
        # type: () -> int
        configs = Configurations(self.__folderStruct)
        return configs.get_drifts_step_size()

    def __createNewRawFileWithHeaderRow(self, folderStruct):
        driftsFileHeaderRow = VelocityDetector.infoHeaders()

        logger = Logger.openInOverwriteMode(folderStruct.getRawDriftsFilepath())
        logger.writeToFile(driftsFileHeaderRow)
        logger.closeFile()
