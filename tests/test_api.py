from src.api import create_user
from src.repository import UserRepository
from src.user_service import UserService


def test_create_user_returns_201() -> None:
    status, body = create_user(
        UserService(UserRepository()),
        {"email": "foo@example.com", "name": "Alice", "age": 20},
    )

    assert status == 201
    assert body["email"] == "foo@example.com"


def test_create_user_duplicate_returns_409() -> None:
    service = UserService(UserRepository())
    create_user(service, {"email": "foo@example.com", "name": "Alice", "age": 20})

    status, body = create_user(
        service,
        {"email": "foo@example.com", "name": "Bob", "age": 30},
    )

    assert status == 409
    assert body == {"error": "DUPLICATE_EMAIL"}
