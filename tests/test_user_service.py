import pytest

from src.exceptions import DuplicateEmailError, ValidationError
from src.repository import UserRepository
from src.user_service import UserService


def test_register_user_normalizes_email() -> None:
    service = UserService(UserRepository())

    user = service.register_user(email=" Foo@Example.COM ", name="Alice", age=20)

    assert user.email == "foo@example.com"


def test_register_user_rejects_duplicate_email() -> None:
    service = UserService(UserRepository())
    service.register_user(email="foo@example.com", name="Alice", age=20)

    with pytest.raises(DuplicateEmailError):
        service.register_user(email="FOO@example.com", name="Bob", age=30)


def test_register_user_rejects_age_below_minimum() -> None:
    service = UserService(UserRepository())

    with pytest.raises(ValidationError):
        service.register_user(email="foo@example.com", name="Alice", age=17)
