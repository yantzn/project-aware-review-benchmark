from __future__ import annotations

from .exceptions import DuplicateEmailError, ValidationError
from .models import User
from .repository import UserRepository


MIN_AGE = 18
MAX_AGE = 120
MAX_NAME_LENGTH = 50


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def register_user(self, *, email: str, name: str, age: int) -> User:
        normalized_email = email.strip().lower()
        normalized_name = name.strip()

        if not normalized_email:
            raise ValidationError("email is required")
        if not normalized_name:
            raise ValidationError("name is required")
        if len(normalized_name) > MAX_NAME_LENGTH:
            raise ValidationError("name is too long")
        if not MIN_AGE <= age <= MAX_AGE:
            raise ValidationError("age is out of range")
        if self._repository.exists_by_email(normalized_email):
            raise DuplicateEmailError(normalized_email)

        return self._repository.save(
            email=normalized_email,
            name=normalized_name,
            age=age,
        )
