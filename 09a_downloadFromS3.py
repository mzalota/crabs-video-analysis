import os
import sys
from string import strip

import boto3
import cv2

from lib.CommandLineLauncher import CommandLineLauncher
from lib.FolderStructure import FolderStructure
from lib.StreamToLogger import StreamToLogger
from lib.VideoToImages import VideoToImages
from lib.ImageWindow import ImageWindow
from lib.Logger import Logger
from lib.VideoStream import VideoStream
from lib.common import Point, Box
from lib.data.CrabsData import CrabsData
from lib.data.SeeFloor import SeeFloor

print(cv2.__version__)

print ("Starting to copy files from S3")

bucket_name="crab-videos"
folder="2020-Kara"
dirpath_local="c:/temp/test_s3"

s3 = boto3.resource('s3')
my_bucket = s3.Bucket(bucket_name)

s3_client = boto3.client('s3')

result = list()
for object_summary in my_bucket.objects.filter(Prefix=folder+"/"):
    print("object_summary", object_summary)
    object_summary_key = object_summary.key

    fullpath = dirpath_local + "/" + object_summary_key

    if os.path.exists(fullpath):
        print("file or dir already exists:", fullpath)
        continue

    # last_char = strip(object_summary_key)[-1:]
    # if last_char=="/":
    #     print("skipping directory: ", fullpath)
    #     continue

    last_4_chars = strip(object_summary_key)[-4:]
    if last_4_chars != ".csv":
        print("skipping non CSV file: ", fullpath)
        continue

    location_of_last_slash = fullpath.rfind("/")
    dirpath2 = fullpath[:location_of_last_slash]
    print("creating location_of_last_slash: ", dirpath2)
    if not os.path.exists(dirpath2):
        print("dirpath3 does not exist. creating directory", dirpath2)
        os.makedirs(dirpath2)

    print("creating filepath: ", fullpath)
    file_in_s3_as_object = s3_client.get_object(Bucket=bucket_name, Key=object_summary_key)
    contents_of_file_as_string = str(file_in_s3_as_object['Body'].read().decode())
    # print("contents_of_file_as_string")
    # print(contents_of_file_as_string)

    logFile = open(fullpath, 'wb')
    logFile.write(contents_of_file_as_string)
    logFile.close()


print ("Done downloading from S3")
