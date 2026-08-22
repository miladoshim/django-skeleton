from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from apps.api.renderers import CommonRenderer
from apps.blog.models import Post
from apps.core.api.serializers import TagSerializer
from apps.core.services.bookmark_service import BookmarkService
from apps.core.services.like_service import LikeService
from apps.core.services.tag_service import TagService


class TagViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    renderer_classes = [CommonRenderer]

    service = TagService()

    def list(self, request):
        result = self.service.list_tags(
            search=request.query_params.get("search"),
            page=int(request.query_params.get("page", 1)),
            page_size=int(request.query_params.get("page_size", 10)),
        )

        serializer = TagSerializer(result["items"], many=True)
        return Response(
            {
                "items": serializer.data,
                "pagination": {
                    "total": result["total"],
                    "page": result["page"],
                    "page_size": result["page_size"],
                    "total_pages": result["total_pages"],
                    "has_next": result["has_next"],
                    "has_previous": result["has_previous"],
                },
            }
        )

    def retrieve(self, request, pk=None):
        tag = self.service.get_tag_detail(tag_id=pk)

        if not tag:
            return Response(
                {"detail": "برچسب پیدا نشد"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TagSerializer(tag, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "شما اجازه ایجاد برچسب را ندارید"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            try:
                tag = self.service.create_tag(
                    name=serializer.validated_data["name"],
                )
                return Response(
                    TagSerializer(tag).data,
                    status=status.HTTP_201_CREATED,
                )
            except ValueError as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, pk=None):
        tag = self.service.get(pk)
        if not tag:
            return Response(
                {"detail": "برچسب پیدا نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_staff:
            return Response(
                {"detail": "شما اجازه ویرایش این برچسب را ندارید"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                updated_tag = self.service.update_tag(
                    tag=tag, user=request.user, **serializer.validated_data
                )
                return Response(TagSerializer(updated_tag).data)
            except PermissionDenied:
                return Response(
                    {"detail": "شما اجازه ویرایش این برچسب را ندارید"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        tag = self.service.get(pk)
        if not tag:
            return Response(
                {"detail": "برچسب پیدا نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_staff:
            return Response(
                {"detail": "شما اجازه حذف این برچسب را ندارید"},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.service.delete(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)


def GlobalSearch(APIView):

    def get(self, request, *args, **kwargs):
        query = request.POST.get("q")
        if query:
            query_for_search = SearchQuery(query)
            search_vector = SearchVector("title", weight="A") + SearchVector(
                "body", weight="B"
            )
            search_rank = SearchRank(search_vector, query_for_search)
            posts = (
                Post.objects.published.annotate(search=search_vector, rank=search_rank)
                .filter(search=query_for_search)
                .order_by("-rank")
            )
            return Response({"posts": posts})


class ToggleLikeAPIView(APIView):
    """لایک - API"""

    permission_classes = [IsAuthenticated]

    def post(self, request, model_name, object_id):
        obj = get_object_or_404(self._get_model(model_name), id=object_id)
        result = LikeService(request.user).toggle(obj)
        return Response(result)

    def _get_model(self, name):
        from apps.blog.models import Post

        models = {"post": Post}
        return models[name]


class ToggleBookmarkAPIView(APIView):
    """بوکمارک - API"""

    permission_classes = [IsAuthenticated]

    def post(self, request, model_name, object_id):
        obj = get_object_or_404(self._get_model(model_name), id=object_id)
        note = request.data.get("note", "")
        result = BookmarkService(request.user).toggle(obj, note)
        return Response(result)

    def _get_model(self, name):
        from apps.blog.models import Post

        return {"post": Post}[name]


class BookmarkListAPIView(APIView):
    """لیست بوکمارک‌ها - API"""

    permission_classes = [IsAuthenticated]

    def get(self, request, model_name):
        from apps.blog.models import Post

        model = {"post": Post}[model_name]

        items = BookmarkService(request.user).get_bookmarked_ids(model)
        return Response({"ids": list(items)})


class InteractionStatusAPIView(APIView):
    """وضعیت تعامل - API"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, model_name, object_id):
        from apps.blog.models import Post

        obj = get_object_or_404(Post, id=object_id)

        if not request.user.is_authenticated:
            return Response({"liked": False, "bookmarked": False})

        return Response(
            {
                "liked": LikeService(request.user).is_liked(obj),
                "bookmarked": BookmarkService(request.user).is_bookmarked(obj),
                "likes_count": obj.likes_count,
            }
        )
