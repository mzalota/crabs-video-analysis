from lib.DetectRedDotsController import DetectRedDotsController
from lib.DetectDriftsController import DetectDriftsController
from lib.FolderStructure import FolderStructure
import os
import json
import boto3


class RunInAWS():

    def __init__(self):
        self.__s3client = boto3.client('s3')

    def run(self):

        video_file_s3_info = self.read_message_from_queue()

        s3_bucket = video_file_s3_info['s3bucket']
        s3_rootDir = video_file_s3_info['rootDir']
        videoFileName = video_file_s3_info['videoFileName']

        print("s3_bucket", s3_bucket)
        print("rootDir", s3_rootDir)
        print("videoFileName", videoFileName)

        folderStruct = self.create_local_folders(videoFileName)

        self.download_video_file_from_s3(folderStruct, s3_bucket, s3_rootDir, videoFileName)

        self.detect_red_dots(folderStruct, s3_bucket, s3_rootDir, videoFileName)

        self.detect_drifts(folderStruct, s3_bucket, s3_rootDir, videoFileName)

        os.listdir(folderStruct.getRootDirectory())

    def create_local_folders(self, videoFileName):
        local_root_dir = "/tmp/crabs"
        if not os.path.exists(local_root_dir):
            os.makedirs(local_root_dir)
        folderStruct = FolderStructure(local_root_dir, videoFileName)
        folderStruct.createDirectoriesIfDontExist(folderStruct.getDriftsFilepath())
        return folderStruct

    def download_video_file_from_s3(self,folderStruct, s3_bucket, s3_rootDir, videoFileName):
        local_root_dir = folderStruct.getRootDirectory()
        s3_key_video_file = s3_rootDir + "/" + videoFileName + ".avi"

        local_filepath = local_root_dir + "/" + videoFileName + ".avi"
        print("local_filepath", local_filepath)

        self.__s3client.download_file(s3_bucket, s3_key_video_file, local_filepath)

    def detect_red_dots(self, folderStruct, s3_bucket, s3_rootDir, videoFileName):
        controller = DetectRedDotsController(folderStruct)
        controller.run()

        s3_key_raw_redDots = s3_rootDir + "/" + videoFileName + "/" + folderStruct.getRedDotsRawFilename()
        print("s3_key_raw_redDots", s3_key_raw_redDots)


        self.__s3client.upload_file(folderStruct.getRedDotsRawFilepath(), s3_bucket, s3_key_raw_redDots)

    def detect_drifts(self, folderStruct, s3_bucket, s3_rootDir, videoFileName):
        controller = DetectDriftsController()
        controller.run(folderStruct)

        s3_key_raw_drifts = s3_rootDir + "/" + videoFileName + "/" + folderStruct.getRawDriftsFilename()
        print("s3_key_raw_drifts", s3_key_raw_drifts)

        self.__s3client.upload_file(folderStruct.getRawDriftsFilepath(), s3_bucket, s3_key_raw_drifts)

    def read_message_from_queue(self):
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
        print('Received message: %s' % message)

        receipt_handle = message['ReceiptHandle']
        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Deleted message with handler: %s' % receipt_handle)

        video_file_info = json.loads(message['Body'])
        return video_file_info


print ("Starting processing in AWS 04")

runner = RunInAWS()
runner.run()

print ("done processing in AWS")