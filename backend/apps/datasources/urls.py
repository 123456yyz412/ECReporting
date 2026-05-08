from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DataSourceInstanceViewSet

router = DefaultRouter()
router.register(r"datasources", DataSourceInstanceViewSet, basename="datasources")

urlpatterns = [
    path("", include(router.urls)),
]
