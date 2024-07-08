from typing import Protocol


class ITaskManager(Protocol):
    @staticmethod
    def send_verify_message(email_in: str): ...

    @staticmethod
    def deactivate_verify_code(email_in: str): ...

    @staticmethod
    def clean_verify_code_table(): ...
