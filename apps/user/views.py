from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User, Group
from .serializers import StaffSerializer, GroupSerializer, DeliveryPersonSerializer
from apps.core.utils import DefaultPagination

# utils
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(tags=["Staff"])
class StaffViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows staff to be viewed or edited.
    Creates staff with groups provided in the request and generates random passwords by default if not provided.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = (
        User.objects.select_related("profile")
        .prefetch_related("groups")
        .exclude(is_superuser=True)
    )
    serializer_class = StaffSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__phone_number",
    ]
    filterset_fields = ["is_active", "groups"]
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(id=self.request.user.id)

    def get_serializer_context(self):
        """Ensure request is passed to serializer context"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(
        detail=False,
        methods=["get"],
        url_path="groups",
        url_name="groups",
        serializer_class=GroupSerializer,
    )
    def list_groups(self, request):
        """List all available groups"""
        groups = Group.objects.all().order_by("name")
        return Response(self.get_serializer(groups, many=True).data)


@extend_schema(tags=["Delivery Persons"])
class DeliveryPersonViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint for delivery persons only (users in the "Delivery man" group).
    Read-only: list and retrieve.
    """

    http_method_names = ["get"]

    queryset = (
        User.objects.select_related("profile")
        .prefetch_related("groups")
        .filter(groups__name="Delivery man")
    )
    serializer_class = DeliveryPersonSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__phone_number",
    ]
    
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["-date_joined"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date_from",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Start date (inclusive). Filters totals by date: DueSell.sale_date, DueCollection.collection_date, OrderDelivery.order_date.",
                required=False,
            ),
            OpenApiParameter(
                name="date_to",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="End date (inclusive). Filters totals by date: DueSell.sale_date, DueCollection.collection_date, OrderDelivery.order_date.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
