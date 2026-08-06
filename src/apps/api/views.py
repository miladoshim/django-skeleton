from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.blog.models import Post
from apps.pages.models import ContactUsSubject, FaqGroup


def search(request):
    if request.method == "POST":
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
