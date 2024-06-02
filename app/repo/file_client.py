from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from app.service.abstract.file_client import FileClient


class S3FileClient(FileClient):
    def __init__(self):
        self.config = {
            "access_key": None,
            "secret_key": None,
            "endpoint": None,
        }
        self.bucket_name = ...
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as s3_client:
            yield s3_client

    async def upload_file(self, file_path, file):
        try:
            async with self.get_client() as s3_client:
                await s3_client.upload_file(
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
