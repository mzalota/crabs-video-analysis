import errno
import os.path

class FolderStructure:
    def __init__(self, rootDirectory, videoFilename):
        self.__rootDirectory = rootDirectory
        self.__videoFilename = videoFilename

    def getRootDirectory(self):
        return self.__rootDirectory

    def getSubDirpath(self):
        return self.__rootDirectory + "/" + self.__videoFilename + "/"

    def getVideoFilename(self):
        return self.__videoFilename

    def getVideoFilepath(self):
        return self.__rootDirectory + "/" + self.__videoFilename + ".avi"

    def getConfigFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_config.txt'

    def getRedDotsRawFilepath(self):
        return self.getSubDirpath() + self.getRedDotsRawFilename()

    def getRedDotsRawFilename(self):
        return self.__videoFilename + '_reddots_raw.csv'

    def getRedDotsInterpolatedFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_reddots_interpolated.csv'
    
    def getRawNormalsFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_normals_raw.csv'
    
    def getInterpolatedNormalsFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_normals_interpolated.csv'

    def getRedDotsManualFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_reddots_manual.csv'

    def getDriftsManualFilepath(self):
        return self.getSubDirpath() + self.getDriftsManualFilename()

    def getDriftsManualFilename(self):
        return self.__videoFilename + '_drifts_manual.csv'

    def getRawDriftsFilepath(self):
        return self.getSubDirpath() + self.getRawDriftsFilename()

    def getRawDriftsFilename(self):
        return self.__videoFilename + '_raw_drifts.csv'

    def getDriftsFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_drifts_interpolated.csv'

    def getSeefloorFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_seefloor.csv'

    def getBadFramesFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_badframes.csv'

    def getFramesDirpath(self):
        return self.getSubDirpath() + "/seqFrames/"

    def getCrabFramesDirpath(self):
        return self.getSubDirpath() + "/crabFrames/"

    def getSavedFramesDirpath(self):
        return self.getSubDirpath() + "/savedFrames/"

    def getFramesFilepath(self):
        return self.getSubDirpath() + self.__videoFilename + '_seqframes.csv'

    def getGraphRedDotsAngle(self):
        return self.getSubDirpath() + "graph_" + self.__videoFilename + '_reddots_angle.png'

    def getGraphRedDotsDistance(self):
        return self.getSubDirpath() + "graph_" + self.__videoFilename + '_reddots_distance.png'

    def getGraphDriftPerFrameMM(self):
        return self.getSubDirpath() + "graph_" + self.__videoFilename + '_drift_per_frame_mm.png'

    def getGraphDriftPerFramePixels(self):
        return self.getSubDirpath() + "graph_" + self.__videoFilename + '_drift_per_frame_pixels.png'

    def getGraphSeefloorPathXY(self):
        return self.getSubDirpath() + "graph_" + self.__videoFilename + '_seefloor_path_XY.png'

    def getGraphSeefloorAdvancementX(self):
        return self.getSubDirpath() + "graph_" + self.__videoFilename + '_seefloor_advancement_X.png'


    #def getFramesFilepaths(self):
    #    framesDir = self.getFramesDirpath()
    #    files = os.listdir(framesDir)
    #    filepaths = []
    #    for filename in files:
    #        filepaths.append(os.path.join(framesDir, filename))
    #    return filepaths

    def getGraphSeefloorAdvancementY(self):
        return self.getSubDirpath() + "graph_" + self.__videoFilename + '_seefloor_advancement_Y.png'

    def getCrabsFilepath(self):
        return self.__filename_prefix() + "_crabs.csv"

    def getCrabsOnSeefloorFilepath(self):
        return self.__filename_prefix() + "_crabs_on_seefloor.csv"

    def getMarkersFilepath(self):
        return self.__filename_prefix() + "_markers.csv"

    def __filename_prefix(self):
        return self.getSubDirpath() + "/" + self.__videoFilename

    def getLogFilepath(self):
        return self.getSubDirpath() + 'stdout.log'

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
