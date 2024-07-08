from app.tasks.tasks import (
    clean_verify_code_table,
    deactivate_verify_code,
    send_verify_message,
)


class CeleryTaskManager:
    @staticmethod
    def send_verify_message(email_in: str):
        send_verify_message.delay(email_in)

    @staticmethod
    def deactivate_verify_code(email_in: str):
        deactivate_verify_code.delay(email_in)

    @staticmethod
    def clean_verify_code_table():
        clean_verify_code_table.delay()
