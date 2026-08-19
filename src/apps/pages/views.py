from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from apps.blog.models import Post
from apps.pages.models import ContactUsSubject
from .forms import ContactForm


class HomePageView(TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.published.all()[:8]
        return context


class ContactUsView(CreateView):
    form_class = ContactForm
    template_name = "pages/contact.html"
    success_url = reverse_lazy("apps.pages:contact_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subjects"] = ContactUsSubject.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        post = super().post(request, *args, **kwargs)
        messages.success(request, "پیام شما دریافت شد با شما تماس خواهیم گرفت.")
        return post


class AboutView(TemplateView):
    template_name = "pages/about.html"
