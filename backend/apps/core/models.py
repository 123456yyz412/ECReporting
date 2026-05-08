from django.db import models
from django.conf import settings


BUILTIN_BACKGROUNDS = [
    {
        "key": "plain-white",
        "name": "全白原皮",
        "theme": "classic",
        "css": "linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%)",
        "palette": {
            "page_overlay": "rgba(255,255,255,0.42)",
            "header_bg": "rgba(255,255,255,0.94)",
            "sidebar_bg": "rgba(255,255,255,0.92)",
            "content_bg": "rgba(255,255,255,0.48)",
            "panel_bg": "rgba(255,255,255,0.88)",
            "panel_bg_strong": "rgba(255,255,255,0.95)",
            "panel_border": "rgba(148,163,184,0.22)",
            "panel_shadow": "0 18px 45px rgba(15,23,42,0.08)",
            "text_primary": "#0f172a",
            "text_secondary": "#475569",
        },
    },
    {
        "key": "cross-border-ocean",
        "name": "跨境海洋",
        "theme": "cross-border",
        "css": "linear-gradient(135deg, #0b1f3a 0%, #114b8c 45%, #22c1c3 100%)",
        "palette": {
            "page_overlay": "linear-gradient(180deg, rgba(3,18,40,0.22) 0%, rgba(10,37,64,0.18) 100%)",
            "header_bg": "rgba(244,250,255,0.72)",
            "sidebar_bg": "rgba(237,246,255,0.66)",
            "content_bg": "rgba(236,246,255,0.18)",
            "panel_bg": "rgba(241,248,255,0.60)",
            "panel_bg_strong": "rgba(248,252,255,0.76)",
            "panel_border": "rgba(255,255,255,0.28)",
            "panel_shadow": "0 22px 55px rgba(8,47,73,0.18)",
            "text_primary": "#0f172a",
            "text_secondary": "#334155",
        },
    },
    {
        "key": "ecommerce-neon",
        "name": "电商流光",
        "theme": "ecommerce",
        "css": "linear-gradient(135deg, #2b1055 0%, #7597de 45%, #ff7eb3 100%)",
        "palette": {
            "page_overlay": "linear-gradient(180deg, rgba(41,17,78,0.18) 0%, rgba(86,66,146,0.16) 100%)",
            "header_bg": "rgba(255,246,252,0.72)",
            "sidebar_bg": "rgba(251,242,255,0.68)",
            "content_bg": "rgba(255,245,250,0.18)",
            "panel_bg": "rgba(255,247,252,0.58)",
            "panel_bg_strong": "rgba(255,250,253,0.76)",
            "panel_border": "rgba(255,255,255,0.26)",
            "panel_shadow": "0 22px 55px rgba(88,28,135,0.18)",
            "text_primary": "#1f2937",
            "text_secondary": "#4b5563",
        },
    },
    {
        "key": "data-grid",
        "name": "数据矩阵",
        "theme": "data",
        "css": "linear-gradient(135deg, #061a40 0%, #0353a4 40%, #00b4d8 100%)",
        "palette": {
            "page_overlay": "linear-gradient(180deg, rgba(2,12,27,0.20) 0%, rgba(3,37,76,0.16) 100%)",
            "header_bg": "rgba(241,249,255,0.72)",
            "sidebar_bg": "rgba(233,245,255,0.66)",
            "content_bg": "rgba(235,247,255,0.18)",
            "panel_bg": "rgba(239,248,255,0.58)",
            "panel_bg_strong": "rgba(247,252,255,0.74)",
            "panel_border": "rgba(255,255,255,0.26)",
            "panel_shadow": "0 22px 55px rgba(3,37,76,0.20)",
            "text_primary": "#0f172a",
            "text_secondary": "#334155",
        },
    },
    {
        "key": "tech-aurora",
        "name": "科技极光",
        "theme": "technology",
        "css": "linear-gradient(135deg, #0f172a 0%, #1d4ed8 35%, #06b6d4 70%, #7c3aed 100%)",
        "palette": {
            "page_overlay": "linear-gradient(180deg, rgba(15,23,42,0.18) 0%, rgba(30,41,59,0.16) 100%)",
            "header_bg": "rgba(242,247,255,0.72)",
            "sidebar_bg": "rgba(238,244,255,0.66)",
            "content_bg": "rgba(237,244,255,0.18)",
            "panel_bg": "rgba(244,248,255,0.58)",
            "panel_bg_strong": "rgba(249,251,255,0.76)",
            "panel_border": "rgba(255,255,255,0.28)",
            "panel_shadow": "0 22px 55px rgba(49,46,129,0.18)",
            "text_primary": "#0f172a",
            "text_secondary": "#334155",
        },
    },
]


class Branding(models.Model):
    company_name = models.CharField(max_length=200, default="ECReporting")
    logo = models.ImageField(upload_to="branding/", null=True, blank=True)
    page_background_kind = models.CharField(max_length=20, default="builtin")
    page_background_value = models.CharField(max_length=100, default="cross-border-ocean")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Branding"
        verbose_name_plural = "Branding"

    @staticmethod
    def get_solo() -> "Branding":
        obj = Branding.objects.first()
        if obj:
            return obj
        return Branding.objects.create()


class CustomBackground(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="backgrounds/")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="custom_backgrounds"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Custom Background"
        verbose_name_plural = "Custom Backgrounds"

    def __str__(self) -> str:
        return self.name
