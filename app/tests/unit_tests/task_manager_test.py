from app.interfaces.task_manager import ITaskManager


def test_task_run(task_manager: ITaskManager):
    assert task_manager.send_verify_message(email_in="<EMAIL>")
    assert task_manager.deactivate_verify_code(email_in="<EMAIL>")
    assert task_manager.clean_verify_code_table()
