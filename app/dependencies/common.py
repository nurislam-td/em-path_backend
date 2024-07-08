from app.adapters.file_client import S3FileClient
from app.adapters.task_manager import CeleryTaskManager
from app.adapters.unit_of_work import SQLAlchemyUnitOfWork
from app.common.settings import settings
from app.service.abstract.file_client import FileClient
from app.service.abstract.task_manager import ITaskManager
from app.service.abstract.unit_of_work import UnitOfWork


def get_uow() -> UnitOfWork:
    return SQLAlchemyUnitOfWork()


def get_task_manager() -> ITaskManager:
    return CeleryTaskManager()


def get_file_client() -> FileClient:
    return S3FileClient(
        access_key=settings.s3.access_key,
        secret_key=settings.s3.secret_key,
        bucket_name=settings.s3.public_bucket_name,
        endpoint_url=settings.s3.endpoint_url,
    )
