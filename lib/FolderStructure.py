import errno
import os.path

class FolderStructure:
    def __init__(self, rootDirectory, videoFilename):
        self.__rootDirectory = rootDirectory
        self.__videoFilename = videoFilename

    def getRootDirectory(self):
        return self.__rootDirectory

    def getVideoFilepath(self):
        return self.__rootDirectory + "/" + self.__videoFilename + ".avi"

    def getRedDotsRawFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_reddots_raw.csv'

    def getRedDotsInterpolatedFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_reddots_interpolated.csv'

    def getRedDotsManualFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_reddots_manual.csv'

    def getRawDriftsFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_raw_drifts.csv'

    def getDriftsFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_drifts.csv'

    def getSeefloorFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_seefloor.csv'

    def getBadFramesFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_badframes.csv'

    def getFramesDirpath(self):
        return self.__getSubDirpath() + "/seqFrames/"

    def getCrabFramesDirpath(self):
        return self.__getSubDirpath() + "/crabFrames/"

    def getFramesFilepaths(self):
        framesDir = self.getFramesDirpath()
        files = os.listdir(framesDir)
        filepaths = []
        for filename in files:
            filepaths.append(os.path.join(framesDir, filename))
        return filepaths

    def getCrabsFilepath(self):
        return self.__getSubDirpath() + "/" + self.__videoFilename + "_crabs.csv"

    def __getSubDirpath(self):
        return self.__rootDirectory + "/" + self.__videoFilename + "/"

    def getLogFilepath(self):
        return self.__getSubDirpath() + 'stdout.log'

    def fileExists(self, filepath):
        return os.path.isfile(filepath)

    @staticmethod
    def createDirectoriesIfDontExist(filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
