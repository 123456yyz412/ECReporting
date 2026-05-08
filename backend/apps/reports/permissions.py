from django.contrib.auth.models import User

from .models import Collection, Query


def user_is_admin(user: User) -> bool:
    return bool(user and (user.is_superuser or user.is_staff))


def user_can_access_collection(user: User, collection: Collection) -> bool:
    if user_is_admin(user):
        return True
    if collection.created_by_id == getattr(user, "id", None):
        return True
    if collection.groups.filter(user=user).exists():
        return True
    return False


def user_can_view_query_sql(user: User, query: Query) -> bool:
    if not query.is_hidden:
        return True
    if user_is_admin(user):
        return True
    if query.created_by_id == getattr(user, "id", None):
        return True
    if query.collection.created_by_id == getattr(user, "id", None):
        return True
    return False
