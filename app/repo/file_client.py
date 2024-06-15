from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from app.service.abstract.file_client import FileClient


class S3FileClient(FileClient):
    def __init__(self, access_key, secret_key, bucket_name, endpoint_url):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as s3_client:
            yield s3_client

    async def upload_file(self, file_path, file):
        try:
            async with self.get_client() as s3_client:
                await s3_client.put_object(
                    Key=file_path,
                    Bucket=self.bucket_name,
                    Body=file,
                )
        except ClientError:
            print("error uploading file")  # TODO add logging

    async def get_file(self, file_path):
        try:
            async with self.get_client() as s3_client:
                response = await s3_client.get_object(
                    Bucket=self.bucket_name, Key=file_path
                )
                file = response["Body"].read()
                return file
        except ClientError:
            print("error getting file")  # TODO add logging
