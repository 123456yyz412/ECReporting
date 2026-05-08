from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import DataSourceInstance
from .serializers import (
    DataSourceInstanceCreateSerializer,
    DataSourceInstancePublicSerializer,
    DataSourceInstanceUpdateSerializer,
)
from .services import get_table_columns, list_tables_and_views


class DataSourceInstanceViewSet(viewsets.GenericViewSet):
    queryset = DataSourceInstance.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return DataSourceInstanceCreateSerializer
        if self.action in ("update", "partial_update"):
            return DataSourceInstanceUpdateSerializer
        return DataSourceInstancePublicSerializer

    def list(self, request):
        qs = self.get_queryset().filter(is_active=True)
        return Response(DataSourceInstancePublicSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        return Response(DataSourceInstancePublicSerializer(obj).data)

    def create(self, request):
        if not request.user.is_staff:
            return Response({"detail": "admin only"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user)
        return Response(DataSourceInstancePublicSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        if not request.user.is_staff:
            return Response({"detail": "admin only"}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(DataSourceInstancePublicSerializer(obj).data)

    def partial_update(self, request, pk=None):
        if not request.user.is_staff:
            return Response({"detail": "admin only"}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(DataSourceInstancePublicSerializer(obj).data)

    def destroy(self, request, pk=None):
        if not request.user.is_staff:
            return Response({"detail": "admin only"}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        try:
            obj.delete()
        except ProtectedError:
            return Response(
                {"detail": "该数据源已被报表查询或填报模块引用，不能删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def tables(self, request, pk=None):
        obj = self.get_object()
        return Response(list_tables_and_views(obj))

    @action(detail=True, methods=["get"])
    def columns(self, request, pk=None):
        obj = self.get_object()
        table = request.query_params.get("table")
        schema = request.query_params.get("schema")
        if not table:
            return Response({"detail": "missing table"}, status=status.HTTP_400_BAD_REQUEST)
        cols = get_table_columns(obj, table_name=table, schema=schema)
        return Response([{"name": c.name, "data_type": c.data_type, "comment": c.comment} for c in cols])

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def test_connection(self, request, pk=None):
        obj = self.get_object()
        try:
            list_tables_and_views(obj)
        except Exception as e:
            return Response({"ok": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"ok": True})
