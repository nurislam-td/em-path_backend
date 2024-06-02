from abc import ABC


class FileClient(ABC):
    async def upload_file(self, file_path, file): ...

    async def get_file(self, file_path): ...
