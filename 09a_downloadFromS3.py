from lib.infra.s3loader import s3loader

print ("Starting to copy files from S3")

folder_in_s3="2020-Kara"
dirpath_local="c:/temp/test_s3"

obj = s3loader()
obj.main(folder_in_s3, dirpath_local)

print ("Done downloading from S3")
