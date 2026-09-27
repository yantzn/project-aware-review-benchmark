from __future__ import annotations

from .models import User


class UserRepository:
    def __init__(self) -> None:
        self._users: list[User] = []

    def exists_by_email(self, email: str) -> bool:
        return any(user.email == email for user in self._users)

    def save(self, *, email: str, name: str, age: int) -> User:
        user = User(id=len(self._users) + 1, email=email, name=name, age=age)
        self._users.append(user)
        return user

    def all(self) -> list[User]:
        return list(self._users)
