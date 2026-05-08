from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.datasources.models import DataSourceInstance

from .models import UploadJob, UploadModule


class UploadModuleSerializer(serializers.ModelSerializer):
    datasource_id = serializers.PrimaryKeyRelatedField(queryset=DataSourceInstance.objects.all(), source="datasource")
    group_ids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)

    class Meta:
        model = UploadModule
        fields = [
            "id",
            "name",
            "datasource_id",
            "table_name",
            "schema",
            "columns",
            "group_ids",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        groups = validated_data.pop("group_ids", [])
        obj = UploadModule.objects.create(**validated_data)
        obj.groups.set(groups)
        return obj

    def update(self, instance: UploadModule, validated_data):
        groups = validated_data.pop("group_ids", None)
        instance = super().update(instance, validated_data)
        if groups is not None:
            instance.groups.set(groups)
        return instance


class UploadJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadJob
        fields = ["id", "module", "filename", "total_rows", "inserted_rows", "status", "error", "created_by", "created_at"]
        read_only_fields = fields
