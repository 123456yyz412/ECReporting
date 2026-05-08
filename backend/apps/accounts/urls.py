from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminGroupViewSet, AdminUserViewSet, me

router = DefaultRouter()
router.register(r"admin/users", AdminUserViewSet, basename="admin-users")
router.register(r"admin/groups", AdminGroupViewSet, basename="admin-groups")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", me),
]
