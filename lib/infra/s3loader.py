import os
from string import strip

import boto3

class s3loader:
    __bucket_name = "crab-videos"

    def main(self,folder_in_s3,  destination_dir_local):
        s3 = boto3.resource('s3')
        s3_client = boto3.client('s3')
        my_bucket = s3.Bucket(self.__bucket_name)

        total_counter = 0
        downloaded_counter=0
        for object_summary in my_bucket.objects.filter(Prefix=folder_in_s3+"/"):
            total_counter +=1
            s3_object_name = object_summary.key
            fullpath = destination_dir_local + "/" + s3_object_name

            if os.path.exists(fullpath):
                print("Skipping. File or dir already exists:", fullpath)
                continue

            if self.__is_folder(s3_object_name):
                print("Skipping. Its a directory: ", fullpath)
                continue

            if self.__is_video_file(s3_object_name):
                print("Skipping. Its a huge video file: ", fullpath)
                continue

            subdir_path = self.__get_filename(fullpath)
            if not os.path.exists(subdir_path):
                print("Subdirectory does not exist. creating directory", subdir_path)
                os.makedirs(subdir_path)

            print("Downloading from s3: ", fullpath)
            file_in_s3_as_object = s3_client.get_object(Bucket=self.__bucket_name, Key=s3_object_name)
            # contents_of_file_as_string = str(file_in_s3_as_object['Body'].read().decode())
            contents_of_file = file_in_s3_as_object['Body'].read()
            self.__write_to_local_file(contents_of_file, fullpath)
            downloaded_counter +=1

        print("total objects in S3:", total_counter)
        print("downloaded files:", downloaded_counter)

    def __is_video_file(self, s3_object_name):
        file_extension = self.__get_extension(s3_object_name)
        if file_extension == ".avi":
            return True
        if file_extension == ".mp4":
            return True
        return False

    def __is_folder(self, s3_object_name):
        last_char = strip(s3_object_name)[-1:]
        if last_char == "/":
            return True
        else:
            return False

    def __write_to_local_file(self, contents_of_file_as_string, fullpath):
        logFile = open(fullpath, 'wb')
        logFile.write(contents_of_file_as_string)
        logFile.close()

    def __get_filename(self, fullpath):
        location_of_last_slash = fullpath.rfind("/")
        dirpath2 = fullpath[:location_of_last_slash]
        return dirpath2

    def __get_extension(self, object_summary_key):
        location_of_last_point = object_summary_key.rfind(".")
        extenstion = object_summary_key[location_of_last_point:]
        return strip(extenstion)