import pandas as pd
import numpy
import matplotlib.pyplot as plt
import os
import sys

from lib.DriftDataRaw import DriftDataRaw
from lib.FolderStructure import FolderStructure
from lib.DriftData import DriftData
from lib.SeeFloor import SeeFloor
from lib.RedDotsData import RedDotsData
from lib.BadFramesData import BadFramesData

# rootDir ="C:/workspaces/AnjutkaVideo/Kara_Sea_Crab_Video_st_5993_2018/"
# videoFileName = "V3__R_20180915_205551"
# videoFileName = "V4__R_20180915_210447"
# videoFileName = "V6__R_20180915_212238"

# rootDir = "C:/workspaces/AnjutkaVideo/KaraSeaCrabVideoBlagopoluchiyaBay2018/"
# videoFileName = "V3_R_20180911_170159"
# videoFileName = "V2_R_20180911_165730"
# videoFileName = "V1_R_20180911_165259"

rootDir = "C:/workspaces/AnjutkaVideo/2019-Kara/St6279_19"
videoFileName = "V2"

folderStruct = FolderStructure(rootDir, videoFileName)

print ("interpolating DriftData")
rawDrifts = DriftDataRaw(folderStruct)
df = rawDrifts.interpolate()

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