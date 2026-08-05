from django.contrib import messages
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Value, IntegerField
from django.db.models.functions import Greatest
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_safe
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView
from apps.academy.models import Course
from apps.blog.models import Post
from apps.core.models import Banner, BannerSection
from apps.core.services.storage_service import storage_list_files
from apps.library.models import Book
from apps.shop.models import Brand, Product
from .forms import ContactForm, SearchForm
from .models import (
    CocoonedTeam,
    ContactSubject,
    CustomerComment,
    FaqGroup,
)


def test(request):
    result = storage_list_files()
    return result


class HomePageView(TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.published.all()[:8]
        context["courses"] = (
            Course.published.annotate(
                episode_count=Count("episodes"),
                chapter_count=Count("chapters"),
            )
            .select_related("category", "coach__profile")
            .order_by("created_at")[:8]
        )
        context["products"] = Product.published.all()[:8]
        context["books"] = Book.published.all()[:8]
        context["brands"] = Brand.objects.all()
        context["main_home_banners"] = Banner.objects.filter(
            section=Value(BannerSection.MAIN_HOME.value, output_field=IntegerField())
        ).all()
        context["sub_home_banners"] = Banner.objects.filter(
            section=Value(
                BannerSection.SUB_SLIDER_HOME.value, output_field=IntegerField()
            )
        ).all()
        return context


@method_decorator(cache_page(60 * 15), name="dispatch")
class ContactCreateView(CreateView):
    form_class = ContactForm
    template_name = "pages/contact.html"
    success_url = reverse_lazy("apps.pages:contact_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subjects"] = ContactSubject.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        post = super().post(request, *args, **kwargs)
        messages.success(request, "پیام شما دریافت شد با شما تماس خواهیم گرفت.")
        return post


@method_decorator(cache_page(60 * 15), name="dispatch")
class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = CustomerComment.objects.all()
        context["team"] = CocoonedTeam.objects.all()
        return context


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

        courses_result = (
            Course.published.annotate(search=search_vector, rank=search_rank)
            .filter(search=search_query)
            .order_by("-rank")
            .all()
        )

        books_result = (
            Book.published.annotate(search=search_vector, rank=search_rank)
            .filter(search=search_query)
            .order_by("-rank")
            .all()
        )

        products_result = (
            Product.published.annotate(search=search_vector, rank=search_rank)
            .filter(search=search_query)
            .order_by("-rank")
            .all()
        )
        context = {
            "query": query,
            "posts_result": posts_result,
            "courses_result": courses_result,
            "books_result": books_result,
            "products_result": products_result,
        }
        return TemplateResponse(request, "pages/search.html", context)


@require_safe
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


@method_decorator(cache_page(60 * 15), name="dispatch")
class MobileAppView(TemplateView):
    template_name = "pages/pwa.html"


@method_decorator(cache_page(60 * 15), name="dispatch")
class FaqView(ListView):
    model = FaqGroup
    template_name = "pages/faqs.html"
    context_object_name = "groups"
