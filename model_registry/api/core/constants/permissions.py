from enum import Enum

class Permission(str, Enum):
    CREATE_USER = "user:create"
    VIEW_USER = "user:view"
    EDIT_USER = "user:edit"
    DELETE_USER = "user:delete"
    CREATE_MODEL = "model:create"
    VIEW_MODEL = "model:view"
    EDIT_MODEL = "model:edit"
    DELETE_MODEL = "model:delete"
    USAGE_MODEL = "model:usage"