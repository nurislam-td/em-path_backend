from app.service import secure


def test_get_password_hash():
    hashed_pass = secure.get_password_hash(password="CoolPass06@")
    assert isinstance(hashed_pass, bytes)


def test_verify_password():
    hashed_pass = secure.get_password_hash(password="CoolPass06@")
    assert secure.verify_password("CoolPass06@", hashed_pass)


def test_incorrect_password():
    hashed_pass = secure.get_password_hash(password="CoolPass06@")
    assert secure.verify_password("WrongPass", hashed_pass) is False


def test_generate_random_num():
    length = 10
    random_num: str = secure.generate_random_num(length=10)
    assert len(random_num) == length
