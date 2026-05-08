from django.contrib.auth.models import User

from .models import UploadModule


def user_is_admin(user: User) -> bool:
    return bool(user and (user.is_superuser or user.is_staff))


def user_can_access_module(user: User, module: UploadModule) -> bool:
    if user_is_admin(user):
        return True
    if module.created_by_id == getattr(user, "id", None):
        return True
    if module.groups.filter(user=user).exists():
        return True
    return False

