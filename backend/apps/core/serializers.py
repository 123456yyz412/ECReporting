from rest_framework import serializers

from .models import BUILTIN_BACKGROUNDS, Branding, CustomBackground


def build_selected_background(obj: Branding, request):
    if obj.page_background_kind == "custom":
        asset = CustomBackground.objects.filter(id=obj.page_background_value).first()
        if asset and asset.image:
            url = asset.image.url
            if request is not None:
                url = request.build_absolute_uri(url)
            return {
                "kind": "custom",
                "key": str(asset.id),
                "name": asset.name,
                "is_builtin": False,
                "image_url": url,
                "css": None,
                "palette": {
                    "page_overlay": "linear-gradient(180deg, rgba(15,23,42,0.24) 0%, rgba(15,23,42,0.12) 100%)",
                    "header_bg": "rgba(255,255,255,0.72)",
                    "sidebar_bg": "rgba(255,255,255,0.66)",
                    "content_bg": "rgba(255,255,255,0.16)",
                    "panel_bg": "rgba(255,255,255,0.58)",
                    "panel_bg_strong": "rgba(255,255,255,0.76)",
                    "panel_border": "rgba(255,255,255,0.28)",
                    "panel_shadow": "0 24px 55px rgba(15,23,42,0.18)",
                    "text_primary": "#0f172a",
                    "text_secondary": "#334155",
                },
            }

    for item in BUILTIN_BACKGROUNDS:
        if item["key"] == obj.page_background_value:
            return {
                "kind": "builtin",
                "key": item["key"],
                "name": item["name"],
                "theme": item["theme"],
                "is_builtin": True,
                "image_url": None,
                "css": item["css"],
                "palette": item["palette"],
            }

    item = BUILTIN_BACKGROUNDS[0]
    return {
        "kind": "builtin",
        "key": item["key"],
        "name": item["name"],
        "theme": item["theme"],
        "is_builtin": True,
        "image_url": None,
        "css": item["css"],
        "palette": item["palette"],
    }


class BrandingSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    page_background = serializers.SerializerMethodField()

    class Meta:
        model = Branding
        fields = ["company_name", "logo_url", "page_background", "updated_at"]

    def get_logo_url(self, obj: Branding):
        if not obj.logo:
            return None
        request = self.context.get("request")
        if request is None:
            return obj.logo.url
        return request.build_absolute_uri(obj.logo.url)

    def get_page_background(self, obj: Branding):
        return build_selected_background(obj, self.context.get("request"))


class BrandingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branding
        fields = ["company_name", "logo", "page_background_kind", "page_background_value"]

    def validate(self, attrs):
        kind = attrs.get("page_background_kind", getattr(self.instance, "page_background_kind", "builtin"))
        value = attrs.get("page_background_value", getattr(self.instance, "page_background_value", "cross-border-ocean"))
        if kind == "builtin":
            if value not in {x["key"] for x in BUILTIN_BACKGROUNDS}:
                raise serializers.ValidationError({"page_background_value": "无效的内置背景"})
        elif kind == "custom":
            if not CustomBackground.objects.filter(id=value).exists():
                raise serializers.ValidationError({"page_background_value": "自定义背景不存在"})
        else:
            raise serializers.ValidationError({"page_background_kind": "无效的背景类型"})
        return attrs


class CustomBackgroundSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()
    is_builtin = serializers.SerializerMethodField()

    class Meta:
        model = CustomBackground
        fields = ["id", "key", "kind", "name", "is_builtin", "image_url", "created_at"]

    def get_image_url(self, obj: CustomBackground):
        request = self.context.get("request")
        if request is None:
            return obj.image.url
        return request.build_absolute_uri(obj.image.url)

    def get_kind(self, obj: CustomBackground):
        return "custom"

    def get_key(self, obj: CustomBackground):
        return str(obj.id)

    def get_is_builtin(self, obj: CustomBackground):
        return False


class CustomBackgroundCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomBackground
        fields = ["name", "image"]
