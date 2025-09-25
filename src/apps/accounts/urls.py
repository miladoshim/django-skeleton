from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
    user_logout,
)


app_name = "accounts"

urlpatterns = [
    #     path('', AccountView.as_view(), name='account_index'),
    #     path('setting/', AccountSettingView.as_view(), name='account_setting'),
    path("register/", UserRegisterView.as_view(), name="register_view"),
    path("login/", UserLoginView.as_view(), name="login_view"),
    path("logout/", user_logout, name="logout"),
    path("password_change/", PasswordChangeView.as_view(), name="password_change_view"),
    path(
        "password_change/done",
        PasswordChangeDoneView.as_view(),
        name="password_change_done_view",
    ),
    
    
    # path('auth/otp/request/', RequestOtpAPIView.as_view()),
    # path('auth/otp/verify/', VerifyOtpAPIView.as_view()),
]
