from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# from .views import (UserRegisterView, UserLoginView, AccountView, AccountSettingView, AccountPaymentView,
#                     AccountOrderView, AccountAddressView,
#                     PasswordChangeView, PasswordChangeDoneView, user_logout)


app_name = "apps.accounts"

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    #     path('register/', UserRegisterView.as_view(), name='register_view'),
    #     path('login/', UserLoginView.as_view(), name='login_view'),
    #     path('logout/', user_logout, name='logout'),
    #     path('', AccountView.as_view(), name='account_index'),
    #     path('setting/', AccountSettingView.as_view(), name='account_setting'),
    #     path('password_change/', PasswordChangeView.as_view(),
    #          name='password_change_view'),
    #     path('password_change/done', PasswordChangeDoneView.as_view(),
    #          name='password_change_done_view'),
]
