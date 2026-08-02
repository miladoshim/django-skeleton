from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from .models import Faq


class HomePageView(TemplateView):
    TemplateView = "core/index.html"

class RobotsTxtView(TemplateView):
    template_name = "robots.txt"

class FaqsListView(ListView):
    template_name = "core/faqs.html"
    model = Faq


def error404_handler(request, *args, **argv):
    return render(request, "errors/404.html", {})


def mark_notification_as_read(request):
    if request.method == "POST":
        notification = Notification.objects.filter(user=request.user, is_read=False)
        notification.update(is_read=True)
        return JsonResponse({"status": "success"})
    return HttpResponseForbidden()


def clear_all_notification(request):
    if request.method == "POST":
        notification = Notification.objects.filter(user=request.user)
        notification.delete()
        return JsonResponse({"status": "success"})
    return HttpResponseForbidden()
