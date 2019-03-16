from VideoFrame import VideoFrame


class Logger:
    __frameLogFile = None
    __driftsLogFile = None

    def __init__(self, redDotsFilePath, driftsFilePath):
        self.__frameLogFile = open(redDotsFilePath, 'wb')
        self.__driftsLogFile = open(driftsFilePath, 'wb')

    def writeToRedDotsFile(self, row):
        self.__writeToCSVFile(self.__frameLogFile, row)

    def writeToDriftsFile(self, row):
        self.__writeToCSVFile(self.__driftsLogFile, row)

    def __writeToCSVFile(self, file, row):
        file.write("\t".join(str(x) for x in row) + "\n")
        file.flush()

    def closeFiles(self):
        self.__frameLogFile.close()
        self.__driftsLogFile.close()