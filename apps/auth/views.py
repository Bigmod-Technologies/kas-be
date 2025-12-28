# auth
from dj_rest_auth.views import LoginView, PasswordChangeView
from rest_framework_simplejwt.views import TokenVerifyView
from dj_rest_auth.jwt_auth import get_refresh_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# utils
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Auth"])
class UserLoginView(LoginView):
    def login(self):
        return super().login()


@extend_schema(tags=["Auth"])
class UserTokenVerifyView(TokenVerifyView):
    pass


refresh_view_class = get_refresh_view()


@extend_schema(tags=["Auth"])
class UserRefreshTokenView(refresh_view_class):
    pass


@extend_schema(tags=["Auth"])
class UserPasswordChangeView(PasswordChangeView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
