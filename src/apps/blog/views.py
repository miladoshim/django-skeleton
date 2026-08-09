from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from utils.enums import PublishStatusChoice
from .forms import CommentCreateForm
from .models import Category, Post

# from apps.blog.services import PostService
# from apps.blog.forms import PostForm


# @method_decorator(cache_page(60 * 15), name="dispatch")
class PostListView(ListView):
    model = Post
    queryset = Post.published.select_related("category", "author").order_by(
        "-created_at"
    )
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    paginate_by = 24

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


# class PostListView(View):
#     """نمایش لیست پستها"""

#     template_name = "posts/list.html"
#     service = PostService()

#     def get(self, request):
#         # استفاده از سرویس یکسان
#         result = self.service.list_posts(
#             user=request.user,
#             is_published=True,
#             search=request.GET.get("q"),
#             category=request.GET.get("category"),
#             page=request.GET.get("page", 1),
#             page_size=12,
#         )

#         return render(
#             request,
#             self.template_name,
#             {
#                 "posts": result["items"],
#                 "total": result["total"],
#                 "has_next": result["has_next"],
#                 "has_previous": result["has_previous"],
#                 "page": result["page"],
#                 "total_pages": result["total_pages"],
#             },
#         )


# class PostCreateView(LoginRequiredMixin, View):
#     """ایجاد پست جدید"""

#     service = PostService()

#     def get(self, request):
#         form = PostForm()
#         return render(request, "posts/create.html", {"form": form})

#     def post(self, request):
#         form = PostForm(request.POST)
#         if form.is_valid():
#             try:
#                 # استفاده از سرویس یکسان
#                 post = self.service.create_post(
#                     title=form.cleaned_data["title"],
#                     content=form.cleaned_data["content"],
#                     author=request.user,
#                     category_id=form.cleaned_data.get("category_id"),
#                     tags=form.cleaned_data.get("tags"),
#                 )
#                 messages.success(request, "پست با موفقیت ایجاد شد!")
#                 return redirect("post_detail", pk=post.pk)
#             except ValueError as e:
#                 form.add_error(None, str(e))

#         return render(request, "posts/create.html", {"form": form})


# class PostDetailView(View):
#     """نمایش جزئیات پست"""

#     service = PostService()

#     def get(self, request, pk):
#         post = self.service.get_post_detail(post_id=pk, user=request.user)

#         if not post:
#             raise Http404("پست پیدا نشد")

#         return render(
#             request,
#             "posts/detail.html",
#             {
#                 "post": post,
#                 "comments": post.comments.filter(is_approved=True),
#             },
#         )


# class PostUpdateView(LoginRequiredMixin, View):
#     """ویرایش پست"""

#     service = PostService()

#     def get(self, request, pk):
#         post = self.service.get(pk)
#         if not post or (post.author != request.user and not request.user.is_staff):
#             raise PermissionDenied()

#         form = PostForm(instance=post)
#         return render(request, "posts/update.html", {"form": form, "post": post})

#     def post(self, request, pk):
#         post = self.service.get(pk)
#         form = PostForm(request.POST, instance=post)

#         if form.is_valid():
#             try:
#                 # استفاده از سرویس یکسان
#                 updated_post = self.service.update_post(
#                     post=post, user=request.user, **form.cleaned_data
#                 )
#                 messages.success(request, "پست بهروزرسانی شد!")
#                 return redirect("post_detail", pk=updated_post.pk)
#             except PermissionDenied as e:
#                 raise
#             except ValueError as e:
#                 form.add_error(None, str(e))

#         return render(request, "posts/update.html", {"form": form, "post": post})
