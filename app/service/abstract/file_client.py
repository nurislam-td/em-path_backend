from typing import Protocol


class FileClient(Protocol):
    async def upload_file(self, file_path, file): ...

    async def get_file(self, file_path): ...
