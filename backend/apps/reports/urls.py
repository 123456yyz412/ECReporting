from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CollectionViewSet, DashboardViewSet, QueryViewSet

router = DefaultRouter()
router.register(r"reports/collections", CollectionViewSet, basename="report-collections")
router.register(r"reports/queries", QueryViewSet, basename="report-queries")
router.register(r"reports/dashboards", DashboardViewSet, basename="report-dashboards")

urlpatterns = [
    path("", include(router.urls)),
]
