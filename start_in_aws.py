from lib.FolderStructure import FolderStructure
from lib.Logger import Logger
from lib.VelocityDetector import VelocityDetector
from lib.data.DriftRawData import DriftRawData
import os

print ("Starting processing in AWS 04")

import boto3

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'https://sqs.eu-central-1.amazonaws.com/876095477992/crabs-processing'

# Receive message from SQS queue
response = sqs.receive_message(
    QueueUrl=queue_url,
    AttributeNames=[
        'SentTimestamp'
    ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=0,
    WaitTimeSeconds=0
)

message = response['Messages'][0]
receipt_handle = message['ReceiptHandle']

# Delete received message from queue
sqs.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
)
print('Received and deleted message: %s' % message)

print ("here 100")
message_body = message['Body']

print ("here 110")

import json

video_file_info = json.loads(message_body)
print ("here 120")

s3_bucket = video_file_info['s3bucket']
s3_rootDir = video_file_info['rootDir']
print ("here 130")
videoFileName = video_file_info['videoFileName']
print ("here 140")


print("s3_bucket",s3_bucket)
print("rootDir",s3_rootDir)
print("videoFileName",videoFileName)

print ("here 150")

s3 = boto3.client('s3')
print ("here 160")
s3_key_video_file = s3_rootDir + "/" + videoFileName + ".avi"
print("s3_key", s3_key_video_file)

local_root_dir = "/tmp/crabs"
print ("here 163")

if not os.path.exists(local_root_dir):
    os.makedirs(local_root_dir)
print ("here 166")

local_filepath = local_root_dir+"/"+videoFileName+".avi"
print("local_filepath", local_filepath)

s3.download_file(s3_bucket, s3_key_video_file, local_filepath)
print ("here 170")

#s3 = boto3.resource('s3')
#s3.meta.client.download_file('mybucket', 'hello.txt', '/tmp/hello.txt')

#s3.Bucket('mybucket').download_file('hello.txt', '/tmp/hello.txt')

#{"rootDir":"s3://crab-videos/Antarctic 2020 AMK79/st6647", "videoFileName":"V10"}

rootDir = local_root_dir


print ("here 173")
os.listdir(rootDir)
print ("here 176")
folderStruct = FolderStructure(rootDir, videoFileName)
print ("here 180")

folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())
print ("here 190")

#StreamToLogger(folderStruct.getLogFilepath())

velocityDetector = VelocityDetector(folderStruct)
print ("here 200")

def newRawFile(folderStruct):
    logger = Logger.openInOverwriteMode(folderStruct.getRawDriftsFilepath())
    driftsFileHeaderRow = VelocityDetector.infoHeaders()
    driftsFileHeaderRow.insert(0, "frameNumber")
    logger.writeToFile(driftsFileHeaderRow)
    return logger

logger = newRawFile(folderStruct)
print ("here 210")

stepSize = 2

logger = Logger.openInAppendMode(folderStruct.getRawDriftsFilepath())
print ("here 220")

rawDriftData = DriftRawData(folderStruct)
print ("here 230")

maxFrameID = rawDriftData.maxFrameID()
if maxFrameID > 1:
    startFrameID = maxFrameID + stepSize
else:
    startFrameID = 5

print ("starting processing from frame", startFrameID)

velocityDetector.runLoop(startFrameID, stepSize, logger)
print ("here 300")

logger.closeFile()
print ("here 310")

os.listdir(rootDir)

print("raw drifts filepath", folderStruct.getRawDriftsFilepath())

s3_key_raw_drifts = s3_rootDir+"/"+videoFileName+"/"+folderStruct.getRawDriftsFilename()

print("s3_key_raw_drifts", s3_key_raw_drifts)

s3.upload_file(folderStruct.getRawDriftsFilepath(), s3_bucket, s3_key_raw_drifts)

print ("done processing in AWS")