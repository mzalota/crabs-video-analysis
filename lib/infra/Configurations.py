from ConfigParser import ConfigParser

from lib.FolderStructure import FolderStructure


class Configurations:
    SECTION_DRIFTS = 'drifts'

    OPTION_DRIFTS_STEP_SIZE = 'DriftsStepSize'

    def __init__(self, folderStruct):
        # type: (FolderStructure) -> Configurations
        self.__parser = ConfigParser()
        self.__parser.read(folderStruct.getConfigFilepath())

        # print "parser sections"
        # sections = parser.sections()
        # print sections


    def has_drifts_step_size(self):
        return self._has_value(self.SECTION_DRIFTS, self.OPTION_DRIFTS_STEP_SIZE)

    def get_drifts_step_size(self):
        return self._get_value(self.SECTION_DRIFTS, self.OPTION_DRIFTS_STEP_SIZE)

    def _get_value(self, sectionName, optionName):
        return self.__parser.get(sectionName, optionName)

    def _has_value(self, sectionName, optionName):
        if not self.__parser.has_section(sectionName):
            # print "No Section: "+sectionName
            return False

        if not self.__parser.has_option(sectionName, optionName):
            # print "In Section '" + sectionName + "' there is no Option: "+optionName
            return False

        return True


    def __manuallyOpenFile(self):
        configFile = open(self.__configFilepath, 'r')
        configDataStr = configFile.read()
        # print "configDataStr"
        # print configDataStr
        configFile.close()