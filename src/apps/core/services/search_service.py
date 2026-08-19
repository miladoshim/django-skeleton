from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.db.models.functions import Greatest
from django.shortcuts import render

from apps.blog.models import Post
from apps.core.forms import SearchForm


class SearchService:
    def search_global(self, query):
        pass

    def search_posts(self, query):
        pass


def search(request):
    if request.method == "GET":
        query = request.GET.get("search")
        if query:
            request.session["query_ses"] = query
        else:
            try:
                query = request.session["query_ses"]
            except:
                query = ""
                pass

        search_query = SearchQuery(query)
        search_vector = SearchVector("title", weight="A")
        search_rank = SearchRank(search_vector, search_query)

        posts_result = (
            Post.published.annotate(search=search_vector, rank=search_rank)
            .filter(search=search_query)
            .order_by("-rank")
            .all
        )

        context = {
            "query": query,
            "posts_result": posts_result,
        }
        return TemplateResponse(request, "pages/search.html", context)


def search_posts_trgm(request):
    form = SearchForm()
    query = None

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.changed_data["query"]
            posts = (
                Post.published.annotate(
                    similarity=Greatest(
                        TrigramSimilarity("title", query),
                        TrigramSimilarity("body", query),
                    )
                )
                .filter(similarity__gt=0.1)
                .order_by("-similarity")
            )

            paginator = Paginator(posts, 8)
            page = request.GET.get("page")
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/search.html",
        {
            "form": form,
            "query": query,
            "posts": posts,
            "page": page,
        },
    )
