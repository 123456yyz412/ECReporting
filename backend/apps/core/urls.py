from django.urls import path

from . import views


urlpatterns = [
    path("health/", views.health),
    path("settings/branding/", views.branding_get),
    path("settings/backgrounds/", views.background_list),
    path("admin/settings/branding/", views.branding_update),
    path("admin/settings/backgrounds/", views.background_create),
    path("admin/settings/backgrounds/<int:pk>/", views.background_delete),
]
