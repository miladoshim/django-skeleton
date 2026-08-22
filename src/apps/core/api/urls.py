from django.urls import include, path
from rest_framework import routers
from apps.core.api.views import TagViewSet

router = routers.DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
    #   path('api/like/<str:model_name>/<uuid:object_id>/', ToggleLikeAPIView.as_view(), name='api_like'),
    # path('api/bookmark/<str:model_name>/<uuid:object_id>/', ToggleBookmarkAPIView.as_view(), name='api_bookmark'),
    # path('api/bookmarks/<str:model_name>/', BookmarkListAPIView.as_view(), name='api_bookmarks'),
    # path('api/interaction/<str:model_name>/<uuid:object_id>/', InteractionStatusAPIView.as_view(), name='api_interaction')
]
