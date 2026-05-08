from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.datasources.models import DataSourceInstance

from .models import Collection, Dashboard, Query
from .permissions import user_can_view_query_sql


class CollectionSerializer(serializers.ModelSerializer):
    group_ids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id",
            "name",
            "description",
            "group_ids",
            "is_active",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def get_created_by_username(self, obj: Collection):
        return getattr(obj.created_by, "username", None)

    def create(self, validated_data):
        groups = validated_data.pop("group_ids", [])
        obj = Collection.objects.create(**validated_data)
        if groups is not None:
            obj.groups.set(groups)
        return obj

    def update(self, instance: Collection, validated_data):
        groups = validated_data.pop("group_ids", None)
        instance = super().update(instance, validated_data)
        if groups is not None:
            instance.groups.set(groups)
        return instance


class QuerySerializer(serializers.ModelSerializer):
    datasource_id = serializers.PrimaryKeyRelatedField(queryset=DataSourceInstance.objects.all(), source="datasource")
    can_view_sql = serializers.SerializerMethodField()
    collection_name = serializers.SerializerMethodField()

    class Meta:
        model = Query
        fields = [
            "id",
            "collection",
            "collection_name",
            "datasource_id",
            "name",
            "sql_text",
            "is_hidden",
            "can_view_sql",
            "visualization_type",
            "visualization_config",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def get_can_view_sql(self, obj: Query) -> bool:
        request = self.context.get("request")
        if request is None:
            return True
        return user_can_view_query_sql(request.user, obj)

    def get_collection_name(self, obj: Query):
        return getattr(obj.collection, "name", None)

    def to_representation(self, instance: Query):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is not None and not user_can_view_query_sql(request.user, instance):
            data["sql_text"] = None
        return data


class DashboardSerializer(serializers.ModelSerializer):
    collection_name = serializers.SerializerMethodField()

    class Meta:
        model = Dashboard
        fields = [
            "id",
            "collection",
            "collection_name",
            "name",
            "layout_mode",
            "background",
            "definition",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def get_collection_name(self, obj: Dashboard):
        return getattr(obj.collection, "name", None)
