from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Collection, Dashboard, Query
from .permissions import user_can_access_collection, user_can_view_query_sql, user_is_admin
from .serializers import CollectionSerializer, DashboardSerializer, QuerySerializer
from .services import run_query
from .sql import is_safe_select_sql


class CollectionViewSet(viewsets.GenericViewSet):
    queryset = Collection.objects.all().order_by("-id")
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if user_is_admin(request.user):
            qs = self.get_queryset().filter(is_active=True)
        else:
            qs = (
                self.get_queryset()
                .filter(is_active=True)
                .filter(Q(created_by=request.user) | Q(groups__user=request.user))
                .distinct()
            )
        return Response(CollectionSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_collection(request.user, obj):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response(CollectionSerializer(obj).data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user_is_admin(request.user):
            serializer.validated_data.pop("group_ids", None)
        obj = serializer.save(created_by=request.user)
        return Response(CollectionSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        obj = self.get_object()
        if not (user_is_admin(request.user) or obj.created_by_id == request.user.id):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user_is_admin(request.user):
            serializer.validated_data.pop("group_ids", None)
        obj = serializer.save()
        return Response(CollectionSerializer(obj).data)

    def destroy(self, request, pk=None):
        obj = self.get_object()
        if not (user_is_admin(request.user) or obj.created_by_id == request.user.id):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QueryViewSet(viewsets.GenericViewSet):
    queryset = Query.objects.select_related("collection", "datasource").all().order_by("-id")
    serializer_class = QuerySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        collection_id = request.query_params.get("collection")
        qs = self.get_queryset()
        if collection_id:
            qs = qs.filter(collection_id=collection_id)
        qs = [q for q in qs if user_can_access_collection(request.user, q.collection)]
        return Response(QuerySerializer(qs, many=True, context={"request": request}).data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_collection(request.user, obj.collection):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response(QuerySerializer(obj, context={"request": request}).data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        collection = serializer.validated_data["collection"]
        if not user_can_access_collection(request.user, collection):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        sql_text = serializer.validated_data["sql_text"]
        if not is_safe_select_sql(sql_text):
            return Response({"detail": "only SELECT/WITH is allowed"}, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.save(created_by=request.user)
        return Response(QuerySerializer(obj, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_collection(request.user, obj.collection):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(obj, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        if obj.is_hidden and not user_can_view_query_sql(request.user, obj):
            return Response({"detail": "query sql is hidden"}, status=status.HTTP_403_FORBIDDEN)

        if "sql_text" in serializer.validated_data and not is_safe_select_sql(serializer.validated_data["sql_text"]):
            return Response({"detail": "only SELECT/WITH is allowed"}, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()
        return Response(QuerySerializer(obj, context={"request": request}).data)

    def destroy(self, request, pk=None):
        obj = self.get_object()
        if not (
            user_is_admin(request.user)
            or obj.created_by_id == request.user.id
            or obj.collection.created_by_id == request.user.id
        ):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_collection(request.user, obj.collection):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        params = request.data.get("params") or {}
        if not is_safe_select_sql(obj.sql_text):
            return Response({"detail": "only SELECT/WITH is allowed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = run_query(db_type=obj.datasource.db_type, instance=obj.datasource, sql=obj.sql_text, params=params)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)

    @action(detail=False, methods=["post"])
    def validate_sql(self, request):
        sql = request.data.get("sql_text") or ""
        return Response({"ok": is_safe_select_sql(sql)})


class DashboardViewSet(viewsets.GenericViewSet):
    queryset = Dashboard.objects.select_related("collection").all().order_by("-id")
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        collection_id = request.query_params.get("collection")
        qs = self.get_queryset()
        if collection_id:
            qs = qs.filter(collection_id=collection_id)
        qs = [d for d in qs if user_can_access_collection(request.user, d.collection)]
        return Response(DashboardSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_collection(request.user, obj.collection):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response(DashboardSerializer(obj).data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        collection = serializer.validated_data["collection"]
        if not user_can_access_collection(request.user, collection):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        obj = serializer.save(created_by=request.user)
        return Response(DashboardSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_collection(request.user, obj.collection):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(DashboardSerializer(obj).data)

    def destroy(self, request, pk=None):
        obj = self.get_object()
        if not (
            user_is_admin(request.user)
            or obj.created_by_id == request.user.id
            or obj.collection.created_by_id == request.user.id
        ):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
