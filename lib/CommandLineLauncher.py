from lib.FolderStructure import FolderStructure


class CommandLineLauncher:
    @staticmethod
    def initializeFolderStruct(argv):
        # type: () -> FolderStructure
        if len(argv) != 3:
            return None

        arguments = len(argv) - 1
        print ("The Script is called with %i arguments" % (arguments))
        rootDir = (argv[1])
        videoFileName = (argv[2])
        folderStruct = FolderStructure(rootDir, videoFileName)
        return folderStruct

