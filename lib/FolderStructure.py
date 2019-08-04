import os.path

class FolderStructure:
    def __init__(self, rootDirectory, videoFilename):
        self.__rootDirectory = rootDirectory
        self.__videoFilename = videoFilename

    def getVideoFilepath(self):
        return self.__rootDirectory + "/" + self.__videoFilename + ".avi"

    def getRedDotsRawFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_reddots_raw.csv'

    def getRedDotsManualFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_reddots_manual.csv'

    def getRawDriftsFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_raw_drifts.csv'

    def getDriftsFilepath(self):
        return self.__getSubDirpath() + self.__videoFilename + '_drifts.csv'

    def getFramesDirpath(self):
        return self.__getSubDirpath() + "/seqFrames/"

    def getCrabsFilepath(self):
        return self.__getSubDirpath() + "/" + self.__videoFilename + "_crabs.csv"

    def __getSubDirpath(self):
        return self.__rootDirectory + "/" + self.__videoFilename + "/"

    def getLogFilepath(self):
        return self.__getSubDirpath() + 'stdout.log'

    def fileExists(self, filepath):
        return os.path.isfile(filepath)
