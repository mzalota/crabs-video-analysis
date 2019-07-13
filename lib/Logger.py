class Logger:
    #__logFile = None


    def __init__(self, filePath, fileMode = 'wb'):
        self.__logFile = open(filePath, fileMode)

    @staticmethod
    def openInAppendMode(filePath):
        # type: (String) -> Logger
        logger = Logger(filePath, 'a')
        return logger

    @staticmethod
    def openInOverwriteMode(filePath):
        # type: (String) -> Logger
        logger = Logger(filePath, 'wb')
        return logger

    def writeToFile(self, row):
        self.__writeToCSVFile(self.__logFile, row)

    def __writeToCSVFile(self, file, row):
        file.write("\t".join(str(x) for x in row) + "\n")
        file.flush()

    def closeFile(self):
        self.__logFile.close()
