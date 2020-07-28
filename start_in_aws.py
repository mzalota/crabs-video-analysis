print ("Starting processing in AWS 02")

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


rootDir = video_file_info['rootDir']
print ("here 130")
videoFileName = video_file_info['videoFileName']
print ("here 140")


print("rootDir",rootDir)

print("videoFileName",videoFileName)

#{"rootDir":"s3://crab-videos/Antarctic 2020 AMK79/st6647", "videoFileName":"V10"}

print ("done processing in AWS")