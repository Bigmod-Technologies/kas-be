from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from .serializers import StaffSerializer
from apps.core.utils import DefaultPagination

# utils
from drf_spectacular.utils import extend_schema


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
    Creates staff with both Salesman and Delivery man groups by default and generates random passwords by default.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    queryset = User.objects.select_related("profile").prefetch_related("groups").all()
    serializer_class = StaffSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name", "profile__phone_number"]
    filterset_fields = ["is_active", "groups"]
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["-date_joined"]
