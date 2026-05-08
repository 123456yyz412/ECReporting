from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import BUILTIN_BACKGROUNDS, Branding, CustomBackground
from .serializers import (
    BrandingSerializer,
    BrandingUpdateSerializer,
    CustomBackgroundCreateSerializer,
    CustomBackgroundSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([AllowAny])
def branding_get(request):
    obj = Branding.get_solo()
    return Response(BrandingSerializer(obj, context={"request": request}).data)


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def branding_update(request):
    obj = Branding.get_solo()
    serializer = BrandingUpdateSerializer(obj, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    obj = serializer.save()
    return Response(BrandingSerializer(obj, context={"request": request}).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def background_list(request):
    builtins = [
        {
            "key": item["key"],
            "kind": "builtin",
            "name": item["name"],
            "theme": item["theme"],
            "is_builtin": True,
            "css": item["css"],
            "image_url": None,
            "palette": item["palette"],
        }
        for item in BUILTIN_BACKGROUNDS
    ]
    customs = CustomBackgroundSerializer(CustomBackground.objects.all().order_by("-id"), many=True, context={"request": request}).data
    return Response({"builtins": builtins, "customs": customs})


@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser])
def background_create(request):
    serializer = CustomBackgroundCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    obj = serializer.save(created_by=request.user)
    return Response(CustomBackgroundSerializer(obj, context={"request": request}).data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def background_delete(request, pk: int):
    obj = CustomBackground.objects.filter(id=pk).first()
    if obj is None:
        return Response({"detail": "背景不存在"}, status=status.HTTP_404_NOT_FOUND)

    branding = Branding.get_solo()
    if branding.page_background_kind == "custom" and branding.page_background_value == str(obj.id):
        branding.page_background_kind = "builtin"
        branding.page_background_value = BUILTIN_BACKGROUNDS[0]["key"]
        branding.save(update_fields=["page_background_kind", "page_background_value", "updated_at"])

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
