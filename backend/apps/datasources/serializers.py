from rest_framework import serializers

from .models import DataSourceInstance


class DataSourceInstancePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSourceInstance
        fields = ["id", "name", "db_type", "host", "port", "database", "schema", "is_active", "created_at", "updated_at"]


class DataSourceInstanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSourceInstance
        fields = ["name", "db_type", "host", "port", "database", "schema", "username", "password", "is_active"]


class DataSourceInstanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSourceInstance
        fields = ["name", "host", "port", "database", "schema", "username", "password", "is_active"]
