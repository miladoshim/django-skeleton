from django.urls import path
from .views import (
    bookmarks_toggle,
    comment_reply,
    error404_handler,
    error500_handler,
)

app_name = "apps.core"

urlpatterns = [
    path("bookmarks/toggle/", bookmarks_toggle, name="bookmarks_toggle"),
    path("bookmarks/remove/", bookmarks_toggle, name="bookmarks_remove"),
    path(
        "comment/reply/<int:object_id>/<str:object_type>/",
        comment_reply,
        name="comment_reply",
    ),
]


handler404 = error404_handler
handler500 = error500_handler
