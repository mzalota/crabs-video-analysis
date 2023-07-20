from configparser import ConfigParser

from lib.FolderStructure import FolderStructure
from lib.infra.Defaults import Defaults


class Configurations:
    SECTION_GENERAL = 'general'
    OPTION_DEBUG_UI = "debug_ui"
    OPTION_DEBUG_UI = "simple_slicer"

    SECTION_DRIFTS = 'drifts'
    OPTION_DRIFTS_STEP_SIZE = 'drifts_step_size'

    SECTION_REDDOTS = 'reddots'
    OPTION_DISTANCE_BETWEEN_REDDOTS = 'distance_between_reddots_millimeters'


    def __init__(self, folderStruct: FolderStructure):

        filepath = folderStruct.getConfigFilepath()
        if not folderStruct.fileExists(filepath):
            print("Config file does not exist. Generating new one with default values")
            newParser = self.__set_default_values()
            self.__save_configs_to_file(newParser, filepath)

        self.__parser = ConfigParser()
        self.__parser.read(filepath)

        # print "parser sections"
        # sections = parser.sections()
        # print sections

    def __set_default_values(self):
        parser = ConfigParser()

        parser.add_section(self.SECTION_GENERAL)
        parser.set(self.SECTION_GENERAL, self.OPTION_DEBUG_UI, str(False))

        parser.add_section(self.SECTION_DRIFTS)
        parser.set(self.SECTION_DRIFTS, self.OPTION_DRIFTS_STEP_SIZE, str(self.__default_drifts_step_size()))

        parser.add_section(self.SECTION_REDDOTS)
        parser.set(self.SECTION_REDDOTS, self.OPTION_DISTANCE_BETWEEN_REDDOTS, str(self.__default_distance_reddots()))

        return parser

    def __save_configs_to_file(self, parser, filepath):
        configFile = open(filepath, 'w')
        # configDataStr = configFile.read()
        parser.write(configFile)
        configFile.close()

    def __default_distance_reddots(self):
        return Defaults.DEFAULT_DISTANCE_BETWEEN_REDDOTS_MM

    def __default_drifts_step_size(self):
        return Defaults.DEFAULT_DRIFTS_STEP_SIZE

    def is_debug(self) -> bool:
        has_value = self._has_value(self.SECTION_GENERAL, self.OPTION_DEBUG_UI)
        if not has_value:
            return False

        value = self._get_value(self.SECTION_GENERAL, self.OPTION_DEBUG_UI)
        if value == "True":
            return True

        return False

    def is_simple_slicer(self) -> bool:
        has_value = self._has_value(self.SECTION_GENERAL, self.OPTION_DEBUG_UI)
        if not has_value:
            return True

        value = self._get_value(self.SECTION_GENERAL, self.OPTION_DEBUG_UI)
        if value == "False":
            return False

        return True

    def get_drifts_step_size(self):
        # type: () -> int
        if self._has_value(self.SECTION_DRIFTS, self.OPTION_DRIFTS_STEP_SIZE):
            return int(self._get_value(self.SECTION_DRIFTS, self.OPTION_DRIFTS_STEP_SIZE))
        else:
            return self.__default_drifts_step_size()

    def get_distance_between_red_dots(self):
        # type: () -> int
        if self._has_value(self.SECTION_REDDOTS, self.OPTION_DISTANCE_BETWEEN_REDDOTS):
            return int(self._get_value(self.SECTION_REDDOTS, self.OPTION_DISTANCE_BETWEEN_REDDOTS))
        else:
            return self.__default_distance_reddots()


    def _get_value(self, sectionName, optionName):
        return self.__parser.get(sectionName, optionName)

    def _has_value(self, sectionName, optionName):
        if not self.__parser.has_section(sectionName):
            return False

        if not self.__parser.has_option(sectionName, optionName):
            return False

        return True
