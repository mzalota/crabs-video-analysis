import sys

from lib.CommandLineLauncher import CommandLineLauncher
from lib.StreamToLogger import StreamToLogger
from lib.data.DriftRawData import DriftRawData
from lib.FolderStructure import FolderStructure
from lib.data.DriftData import DriftData
from lib.data.SeeFloor import SeeFloor
from lib.data.RedDotsData import RedDotsData

print ("Starting to interpolate Data")

folderStruct = CommandLineLauncher.initializeFolderStruct(sys.argv)
if folderStruct is None:

    rootDir = "C:\workspaces\AnjutkaVideo\Antarctic_2020_AMK79\st6647"
    videoFileName = "V12"

    folderStruct = FolderStructure(rootDir, videoFileName)

StreamToLogger(folderStruct.getLogFilepath())

print ("interpolating DriftData")
rawDrifts = DriftRawData(folderStruct)
druftsStepSize = 2
df = rawDrifts.interpolate(druftsStepSize)

drifts = DriftData.createFromFolderStruct(folderStruct)
drifts.setDF(df)
drifts.saveToFile(folderStruct.getDriftsFilepath())

print ("interpolating RedDots")
rdd = RedDotsData.createFromFolderStruct(folderStruct)
rdd.saveInterpolatedDFToFile(drifts.minFrameID(), drifts.maxFrameID()+1)

print ("interpolating SeeFloor")

sf = SeeFloor.createFromFolderStruct(folderStruct)
sf.saveToFile()

print ("Done inerpolating")