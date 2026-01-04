from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Zone
from .serializers import ZoneSerializer
from apps.core.utils import DefaultPagination

# utils
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Zones"])
class ZoneViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows zones to be viewed or edited.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "name",
    ]
    filterset_fields = [
        "is_archive",
    ]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
