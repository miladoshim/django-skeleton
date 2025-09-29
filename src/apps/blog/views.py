from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from auditlog.mixins import LogAccessMixin
from .models import Category, Post
from .forms import CommentCreateForm


class PostListView(ListView):
    model = Post
    # queryset = Post.objects.select_related('category').all()
    queryset = Post.published.all()
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    paginate_by = 24

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_count'] = Post.objects.aggregate(count=Count('id'))
        context['categories'] = Post.objects.values("category").annotate(category_count=Count("category"))
        # context['popular_tags'] = Post.objects.values("tags__name").annotate(total_view=Sum("viewCount")).order_by("-total_views")[:8]
        return context


class PostDetailView(LogAccessMixin, FormMixin, DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    form_class = CommentCreateForm

    #     # def get_object(self, queryset):
    #     #     slug = self.kwargs.get('post_id')
    #     #     return get_object_or_404(Post.objects.published(), slug=slug)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context["form"] = CommentCreateForm(
            initial={"post": self.object, "user": self.request.user}
        )
        # context['related_posts'] = Post.published.all()
        context["comments"] = self.object.comments.filter(is_approved=True)
        return context


    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
        else:
            pass

    def form_valid(self, form):
        form.save()
        return super(PostDetailView, self).form_valid(form)


# class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Post
#     def test_func(self):
#         obj = self.get_object()
#         return obj.author == self.request.user

# def post_by_tag(request, slug):
#     posts = Post.objects.filter(tags__slug=slug)
#     context = {
#         'posts': posts
#     }
#     return render(request, "blog/post_list.html", context)


# class AuthorListView(ListView):
#     model = User
#     # queryset = Post.objects.all().select_related('posts')
#     # queryset = User.authors.all()
#     context_object_name = 'authors'
#     template_name = 'blog/author_list.html'
#     paginate_by = 24


# class AuthorDetailView(DetailView):
#     template_name = "blog/author_detail.html"
#     context_object_name = 'author'

#     def get_queryset(self):
#         if self.request.user.is_superuser:
#             return Post.objects.all()
#         else:
#             return Post.objects.filter(author=self.request.user)


class CategoryListView(ListView):
    model = Category
    template_name = "blog/category_list.html"
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = "blog/category_detail.html"
    context_object_name = 'category'


# class SearchListView(ListView):
#     pass


def likePost(request, id):
    post = Post.objects.get(id=id)
    user = request.user
    if user in post.likes.all():
        return "you are like this post"
    post.likes.add(user)
    return ""
