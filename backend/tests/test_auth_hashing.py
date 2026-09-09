from app.auth.hashing import hash_password, verify_password


def test_password_hash_and_verify():
    password = "MyPassword@123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword@123", hashed) is False