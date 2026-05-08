from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UploadJobViewSet, UploadModuleViewSet

router = DefaultRouter()
router.register(r"datafill/modules", UploadModuleViewSet, basename="datafill-modules")
router.register(r"datafill/jobs", UploadJobViewSet, basename="datafill-jobs")

urlpatterns = [
    path("", include(router.urls)),
]
