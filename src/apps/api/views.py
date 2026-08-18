from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.blog.models import Post
from apps.pages.models import ContactUsSubject, FaqGroup


class FaqGroupViewSet(ReadOnlyModelViewSet):
    """
    Return a list of all faq groups
    """

    queryset = FaqGroup.objects.all()
    # serializer_class = FaqGroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @method_decorator(cache_page(60 * 15, key_prefix="faq_group_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ContactSubjectViewSet(ReadOnlyModelViewSet):
    """
    Return a list of all contact us subjects
    """

    queryset = ContactUsSubject.objects.all()
    # serializer_class = ContactSubjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @method_decorator(cache_page(60 * 15, key_prefix="faq_group_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
