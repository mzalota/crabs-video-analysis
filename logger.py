from RedDotsDetector import RedDotsDetector


class Logger:
    #__logFile = None

    def __init__(self, filePath):
        self.__logFile = open(filePath, 'wb')

    def writeToFile(self, row):
        self.__writeToCSVFile(self.__logFile, row)

    def __writeToCSVFile(self, file, row):
        file.write("\t".join(str(x) for x in row) + "\n")
        file.flush()

    def closeFile(self):
        self.__logFile.close()
