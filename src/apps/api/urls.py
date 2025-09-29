from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import (
    TagViewSet,
    PostViewSet,
    CategoryViewSet,
    UserForgotPasswordAPIView,
    UserPasswordResetAPIView,
    UserLogoutView,
    UserLoginView,
)

app_name='api'

router = routers.DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"posts", PostViewSet, basename="post")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
    
    # path('auth/register/', UserRegisterView.as_view()),
    path("auth/token/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path('auth/login/', UserLoginView.as_view()),
    path('auth/logout/', UserLogoutView.as_view()),
    
    path('auth/passwords/forgot/', UserForgotPasswordAPIView.as_view()),
    path('auth/passwords/reset/<uid>/<token>/', UserPasswordResetAPIView.as_view()),
    
    # path('auth/oauth/google/'),
    # path('auth/otp/request/', RequestOtpAPIView.as_view()),
    # path('auth/otp/verify/', VerifyOtpAPIView.as_view()),
    
    # path('account/password_change', UserChangePasswordAPIView.as_view()),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
