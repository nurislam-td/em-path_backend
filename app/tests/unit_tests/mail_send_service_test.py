import pytest

from app.core.exceptions import IncorrectVerificationCode
from app.interfaces.task_manager import ITaskManager
from app.interfaces.unit_of_work import IUnitOfWork
from app.schemas.verify_code import VerifyCodeCheck
from app.service import mail_send


async def test_check_code(uow: IUnitOfWork, task_manager: ITaskManager):
    correct_code_str = "777777"
    correct_email = "mail_send_service@example.com"
    code = VerifyCodeCheck(email=correct_email, code=correct_code_str)
    assert 200 == await mail_send.check_code(
        code=code, uow=uow, task_manager=task_manager
    )


async def test_check_incorrect_code(uow: IUnitOfWork, task_manager: ITaskManager):
    incorrect_code_str = "111111"
    correct_email = "mail_send_service@example.com"
    code = VerifyCodeCheck(email=correct_email, code=incorrect_code_str)
    with pytest.raises(IncorrectVerificationCode):
        await mail_send.check_code(code=code, uow=uow, task_manager=task_manager)


async def test_check_incorrect_email(uow: IUnitOfWork, task_manager: ITaskManager):
    correct_code_str = "777777"
    incorrect_email = "wrong@example.com"
    code = VerifyCodeCheck(email=incorrect_email, code=correct_code_str)
    with pytest.raises(IncorrectVerificationCode):
        await mail_send.check_code(code=code, uow=uow, task_manager=task_manager)
