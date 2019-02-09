from VideoFrame import VideoFrame


class Logger:
    __frameLogFile = None
    __featuresLogFile = None

    def __init__(self, csvFilePath, featuresFilePath):
        self.__frameLogFile = open(csvFilePath, 'wb')
        self.__featuresLogFile = open(featuresFilePath, 'wb')

    def writeToRedDotsFile(self, row):
        self.__writeToCSVFile(self.__frameLogFile, row)

    def __writeToCSVFile(self, file, row):
        file.write(";".join(str(x) for x in row) + "\n")
        file.flush()

    def closeFiles(self):
        self.__frameLogFile.close()