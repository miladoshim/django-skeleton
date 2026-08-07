from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from taggit.serializers import TaggitSerializer, TagListSerializerField
from apps.core.services.tag_service import TagService

# class TagViewSet(ReadOnlyModelViewSet):

#     queryset = Tag.objects.all()
#     serializer_class = TaggitSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)


class TagViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    service = TagService()

    def list(self, request):
        result = self.service.list_tags(
            search=request.query_params.get("search"),
            page=int(request.query_params.get("page", 1)),
            page_size=int(request.query_params.get("page_size", 10)),
        )

        serializer = TaggitSerializer(result["items"], many=True)
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

        serializer = TaggitSerializer(tag, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        serializer = TaggitSerializer(data=request.data)
        if serializer.is_valid():
            try:
                tag = self.service.create_tag(
                    title=serializer.validated_data["title"],
                )
                return Response(
                    TaggitSerializer(tag).data,
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
        """ویرایش پست"""
        tag = self.service.get(pk)
        if not tag:
            return Response(
                {"detail": "پست پیدا نشد"}, status=status.HTTP_404_NOT_FOUND
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
                    {"detail": "شما اجازه ویرایش این پست را ندارید"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """حذف پست"""
        tag = self.service.get(pk)
        if not tag:
            return Response(
                {"detail": "پست پیدا نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        if tag.author != request.user and not request.user.is_staff:
            return Response(
                {"detail": "شما اجازه حذف این پست را ندارید"},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.service.delete(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)
