from django.urls import path

from .views import *

# auth
urlpatterns = [
    # URLs that do not require a session or valid token
    path("login/", UserLoginView.as_view(), name="login"),
    path("token/verify/", UserTokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", UserRefreshTokenView.as_view(), name="token_refresh"),
    # URLs that require a user to be logged in with a valid session / token.
    path("password/change/", UserPasswordChangeView.as_view(), name="password_change"),
]
