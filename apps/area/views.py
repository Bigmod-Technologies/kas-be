from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Zone, Area, WorkingDay
from .serializers import ZoneSerializer, AreaSerializer, WorkingDaySerializer
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


@extend_schema(tags=["Zones Areas"])
class AreaViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows areas to be viewed or edited.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = (
        Area.objects.select_related("zone").prefetch_related("working_days").all()
    )
    serializer_class = AreaSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "name",
        "route_number",
    ]
    filterset_fields = [
        "zone",
    ]
    ordering_fields = ["name", "route_number", "created_at"]
    ordering = ["name"]

    @action(
        detail=False,
        methods=["get"],
        serializer_class=WorkingDaySerializer,
        url_path="working-days",
    )
    def working_days(self, request):
        """
        List all working days.
        """
        working_days = WorkingDay.objects.all().order_by("name")
        serializer = self.get_serializer(working_days, many=True)
        return Response(serializer.data)
