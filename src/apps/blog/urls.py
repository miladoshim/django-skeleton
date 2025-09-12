from django.urls import path, include
from rest_framework import routers

app_name='apps.blog'

router = routers.DefaultRouter()
# router.register(r'tags', views.UserViewSet)
# router.register(r'posts', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]