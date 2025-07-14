from storages.backends.s3boto3 import S3Boto3Storage

class R2Storage(S3Boto3Storage):
    bucket_name = 'bharbhox'
    endpoint_url = 'https://a5f9ee7b3883a9c77c46adca93821bec.r2.cloudflarestorage.com'
    file_overwrite = False