from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from apps.blog.models import Post
from apps.core.services.bookmark_services import BookmarkService
from .forms import CommentReplyCreateForm, NewsletterSubscriberForm
from .models import Comment


def error404_handler(request, *args, **kwargs):
    return render(request, "errors/404.html", {})


def error500_handler(request, *args, **kwargs):
    return render(request, "errors/500.html", {})


@login_required
def bookmarks_toggle(request, content_type_id, object_id):
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    obj = get_object_or_404(model_class, id=object_id)

    is_bookmarked = BookmarkService.toggle(request.user, obj)

    if is_bookmarked:
        messages.success(request, "به بوکمارک‌های شما اضافه شد ✅")
    else:
        messages.info(request, "از بوکمارک‌های شما حذف شد")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def bookmarks_remove(request, bookmark_id):
    """حذف بوکمارک از صفحه لیست"""
    bookmark = get_object_or_404(Bookmark, id=bookmark_id, user=request.user)
    bookmark.delete()
    messages.success(request, "از بوکمارک‌ها حذف شد")
    return redirect("bookmark:list")


def newsletter_subscribe(request):
    if request.method == "POST":
        form = NewsletterSubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()
            context = {"subscriber": subscriber}
            # send thanks email with gift to subscriber

            return render(request, "index.html", context)
    else:
        form = NewsletterSubscriberForm()
    return render(request, "index.html", {"form": form})


# @require_POST
def comment_reply(request, *args, **kwargs):
    object_id = kwargs.get("object_id")
    object_type = kwargs.get("object_type")
    object_ = None

    if object_type == "a":
        object_ = get_object_or_404(Post, id=object_id)
    else:
        return HttpResponse("model not found")

    if request.method == "POST":
        form = CommentReplyCreateForm(request.POST)
        if form.is_valid():
            reply = form.data.get("reply")
            pid = form.data.get("pid")
            parent = get_object_or_404(Comment, id=pid)
            Comment.objects.create(
                user=request.user,
                comment=reply,
                parent=parent,
                content_object=object_,
            )
            messages.success(
                request, "پاسخ شما ثبت شد بعد از تایید مدیریت نمایش داده می شود."
            )
            return HttpResponseRedirect(object_.get_absolute_url())
        else:
            print(form.errors.as_data())
            messages.error(request, "خطا در ثبت دیدگاه")
            return HttpResponseRedirect(object_.get_absolute_url())


class RobotsTxtView(TemplateView):
    template_name = "robots.txt"
