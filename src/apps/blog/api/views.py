from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.api.renderers import CommonRenderer
from apps.blog.api.serializers import PostSerializer
from apps.blog.services.post_service import PostService


class PostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    service = PostService()
    renderer_classes = [CommonRenderer]

    def list(self, request):
        result = self.service.list_public_posts(
            category=request.query_params.get("category"),
            search=request.query_params.get("search"),
            page=int(request.query_params.get("page", 1)),
            page_size=int(request.query_params.get("page_size", 10)),
        )

        serializer = PostSerializer(result["items"], many=True)
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
        post = self.service.get_post_detail(
            request=request,
            post_slug=pk,
        )

        if not post:
            return Response(
                {"detail": "پست پیدا نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        """ایجاد پست جدید"""
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            try:
                post = self.service.create_post(
                    title=serializer.validated_data["title"],
                    content=serializer.validated_data["content"],
                    author=request.user,
                    category_id=serializer.validated_data.get("category_id"),
                    tags=serializer.validated_data.get("tags"),
                )
                return Response(
                    PostSerializer(post).data, status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """ویرایش پست"""
        post = self.service.get(pk)
        if not post:
            return Response(
                {"detail": "پست پیدا نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                updated_post = self.service.update_post(
                    post=post, user=request.user, **serializer.validated_data
                )
                return Response(PostSerializer(updated_post).data)
            except PermissionDenied:
                return Response(
                    {"detail": "شما اجازه ویرایش این پست را ندارید"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """حذف پست"""
        post = self.service.get(pk)
        if not post:
            return Response(
                {"detail": "پست پیدا نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        if post.author != request.user and not request.user.is_staff:
            return Response(
                {"detail": "شما اجازه حذف این پست را ندارید"},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.service.delete(post)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """انتشار پست"""
        post = self.service.get(pk)
        if not post:
            return Response({"detail": "پست پیدا نش"})
