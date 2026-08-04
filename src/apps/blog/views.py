from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView
from django_filters.views import FilterView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from apps.core.models import Comment
from utils.enums import PublishStatusChoice
from .filters import PostFilter
from .forms import CommentCreateForm
from .models import Category, Post


# @method_decorator(cache_page(60 * 15), name="dispatch")
class PostListView(FilterView):
    model = Post
    queryset = Post.published.select_related("category", "author").order_by(
        "-created_at"
    )
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    paginate_by = 24
    filterset_class = PostFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_count"] = Post.published.aggregate(count=Count("id"))
        context["categories"] = Post.published.values("category").annotate(
            category_count=Count("category")
        )
        # context['popular_tags'] = Post.objects.values("tags__name").annotate(total_view=Sum("viewCount")).order_by("-total_views")[:8]
        return context


# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page, vary_on_cookie
# class PostDetailView(HitCountDetailView):
#     count_hit = True
#     model = Post
#     slug_field = "slug"
#     template_name = "blog/blog_detail.html"
#     context_object_name = "blog"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         blog = self.get_object()
#         comment = blog.comments.all().order_by("-created_at")
#         context = {
#             "comments": comment,
#             "blog": blog,
#         }
#         return context

#     def post(self, request, slug):
#         if not request.user.is_authenticated:
#             return redirect("account:sign-in")
#         slug = unquote(slug)
#         blog = get_object_or_404(Post, slug=slug)
#         parent_id = request.POST.get("parent_id")
#         body = request.POST.get("body")
#         Comment.objects.create(
#             body=body, blog=blog, user=request.user, parent_id=parent_id
#         )
#         return redirect(reverse("blog:blog-detail", kwargs={"slug": slug}))


# @cache_page(60 * 15)
def post_detail(request, slug):
    # post = cache.get(f"post_{slug}")
    # if not post:
    #     post = get_object_or_404(Post, slug=slug, published_status=PublishStatusChoice.PUBLISHED)
    #     cache.set(f"post_{slug}", post, timeout=300)

    post = get_object_or_404(
        Post,
        slug=slug,
        published_status=PublishStatusChoice.PUBLISHED,
    )
    comments = post.comments.filter(is_approved=True, parent_id__isnull=True)

    if request.method == "POST":
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                content_object=post,
                comment=form.data.get("comment"),
                user=request.user,
            )
            messages.success(
                request, "دیدگاه ثبت شد بعد از تایید مدیریت نمایش داده می شود."
            )
            # post_url = request.build_absolute_uri(post.get_absolute_url())
            # return HttpResponseRedirect(post_url)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            print(form.errors.as_data())
            messages.error(request, "خطا در ثبت دیدگاه")
    else:
        hit_count = HitCount.objects.get_for_object(post)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)

        form = CommentCreateForm()

    context = {
        "post": post,
        "comments": comments,
        "form": form,
        "similar_posts": post.get_similar_posts,
        # 'similar_courses' : post.get_similar_courses,
    }
    return render(request, "blog/post_detail.html", context)


@method_decorator(cache_page(60 * 15), name="dispatch")
class CategoryListView(ListView):
    model = Category
    template_name = "blog/category_list.html"
    context_object_name = "categories"


@method_decorator(cache_page(60 * 15), name="dispatch")
class CategoryDetailView(DetailView):
    model = Category
    template_name = "blog/category_detail.html"
    context_object_name = "category"


def likePost(request, id):
    post = Post.objects.get(id=id)
    user = request.user
    if user in post.likes.all():
        return "you are like this post"
    post.likes.add(user)
    return ""
