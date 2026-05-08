from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    GroupCreateSerializer,
    GroupSerializer,
    UserCreateSerializer,
    UserResetPasswordSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class AdminUserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer

    def list(self, request):
        users = self.get_queryset()
        return Response(UserSerializer(users, many=True).data)

    def retrieve(self, request, pk=None):
        user = self.get_object()
        return Response(UserSerializer(user).data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)

    def partial_update(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)

    def destroy(self, request, pk=None):
        user = self.get_object()
        if user.id == request.user.id:
            return Response({"detail": "不能删除当前登录用户"}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_staff or user.is_superuser:
            admin_count = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).exclude(id=user.id).count()
            if admin_count == 0:
                return Response({"detail": "至少保留一个管理员用户"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = UserResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])
        return Response({"ok": True})


class AdminGroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Group.objects.all().order_by("id")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return GroupCreateSerializer
        return GroupSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        group = self.get_object()
        if group.name in {"管理员", "普通用户"}:
            return Response({"detail": "默认用户组不能删除"}, status=status.HTTP_400_BAD_REQUEST)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def set_users(self, request, pk=None):
        group = self.get_object()
        user_ids = request.data.get("user_ids", [])
        users = User.objects.filter(id__in=user_ids)
        with transaction.atomic():
            group.user_set.set(users)
        return Response(GroupSerializer(group).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)
