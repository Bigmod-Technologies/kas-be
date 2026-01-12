from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User, Group

from .serializers import StaffSerializer, GroupSerializer
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
