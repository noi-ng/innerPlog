from enum import StrEnum


class AccountStatus(StrEnum):
    ACTIVE = "active"
    BANNED = "banned"


class UserRole(StrEnum):
    ADMIN = "admin"
    WRITER = "writer"


class PostStatus(StrEnum):
    PUBLIC = "public"
    DRAFT = "draft"
    BANNED = "banned"
