from storages.backends.s3boto3 import S3Boto3Storage

class S3DefaultStorage(S3Boto3Storage):
    default_acl = 'private'
    location = 'media'