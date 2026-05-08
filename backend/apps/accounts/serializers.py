from django.contrib.auth.models import Group, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source="groups")
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_admin",
            "groups",
            "group_ids",
            "date_joined",
        ]

    def get_is_admin(self, obj: User) -> bool:
        return bool(obj.is_superuser or obj.is_staff)


class UserCreateSerializer(serializers.ModelSerializer):
    group_ids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "is_active", "group_ids", "is_staff"]

    def create(self, validated_data):
        groups = validated_data.pop("group_ids", [])
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if groups:
            user.groups.set(groups)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    group_ids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "is_active", "group_ids", "is_staff"]

    def update(self, instance: User, validated_data):
        groups = validated_data.pop("group_ids", None)
        instance = super().update(instance, validated_data)
        if groups is not None:
            instance.groups.set(groups)
        return instance


class UserResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)


class GroupSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "user_count"]

    def get_user_count(self, obj: Group) -> int:
        return obj.user_set.count()


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]
