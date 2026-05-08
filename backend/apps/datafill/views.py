from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UploadJob, UploadModule
from .permissions import user_can_access_module, user_is_admin
from .serializers import UploadJobSerializer, UploadModuleSerializer
from .services import build_template_csv, build_template_xlsx, insert_rows, parse_upload_file


class UploadModuleViewSet(viewsets.GenericViewSet):
    queryset = UploadModule.objects.select_related("datasource").all().order_by("-id")
    serializer_class = UploadModuleSerializer
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
        return Response(UploadModuleSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_module(request.user, obj):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response(UploadModuleSerializer(obj).data)

    def create(self, request):
        if not user_is_admin(request.user):
            return Response({"detail": "admin only"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user)
        return Response(UploadModuleSerializer(obj).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        if not user_is_admin(request.user):
            return Response({"detail": "admin only"}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(UploadModuleSerializer(obj).data)

    def destroy(self, request, pk=None):
        if not user_is_admin(request.user):
            return Response({"detail": "admin only"}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def template_csv(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_module(request.user, obj):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        content = build_template_csv(obj)
        resp = HttpResponse(content, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{obj.name}.csv"'
        return resp

    @action(detail=True, methods=["get"])
    def template_xlsx(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_module(request.user, obj):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        content = build_template_xlsx(obj)
        resp = HttpResponse(
            content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp["Content-Disposition"] = f'attachment; filename="{obj.name}.xlsx"'
        return resp

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser])
    def upload(self, request, pk=None):
        obj = self.get_object()
        if not user_can_access_module(request.user, obj):
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)

        f = request.data.get("file")
        if f is None:
            return Response({"detail": "missing file"}, status=status.HTTP_400_BAD_REQUEST)

        job = UploadJob.objects.create(module=obj, filename=getattr(f, "name", ""), created_by=request.user, status="running")

        try:
            content = f.read()
            header, rows = parse_upload_file(job.filename, content)
            inserted = insert_rows(obj, header, rows)
            job.total_rows = len(rows)
            job.inserted_rows = inserted
            job.status = "done"
            job.save(update_fields=["total_rows", "inserted_rows", "status"])
        except Exception as e:
            job.status = "error"
            job.error = str(e)
            job.save(update_fields=["status", "error"])
            return Response({"ok": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"ok": True, "job": UploadJobSerializer(job).data})


class UploadJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UploadJob.objects.select_related("module").all().order_by("-id")
    serializer_class = UploadJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if user_is_admin(self.request.user):
            return qs
        return qs.filter(created_by=self.request.user)
