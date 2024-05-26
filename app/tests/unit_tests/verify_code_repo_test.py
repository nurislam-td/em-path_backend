from app.service.abstract.unit_of_work import UnitOfWork


async def test_get_last_active_by_email(uow: UnitOfWork):
    email_in = "user@example.com"
    async with uow:
        verify_code = await uow.verify_code.get_last_active_by_email(email_in)
        assert verify_code.is_active


async def test_update_verify_code_by_email(uow: UnitOfWork):
    email_in = "user@example.com"
    async with uow:
        verify_code = await uow.verify_code.get_last_active_by_email(email_in)
        assert verify_code.is_active
        await uow.verify_code.update(
            values=dict(is_active=False), filters=dict(email=email_in)
        )
        await uow.commit()
        verify_code = await uow.verify_code.get_last_active_by_email(email_in)
    assert verify_code is None
