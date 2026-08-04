import uuid
import logging
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from django.urls import reverse


class HtmxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header = request.headers.get("HX-Request") or None

        if header:
            request.htmx = header == "true"
        else:
            request.htmx = False

        response = self.get_response(request)
        return response


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE:
            logging.warning("Application is in maintenance mode!!!")

        response = self.get_response(request)

        return response


class IsCoachMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if not user.is_coach:
            return HttpResponseRedirect(reverse("apps.pages:home_view"))

        response = self.get_response(request)

        return response


class PlusAccountIsActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        response = self.get_response(request)

        if request.user.is_authenticated:
            vip = request.user.vip_subscriptions.filter(
                is_active=True, end_at__gte=timezone.now()
            ).first()
            request.is_vip = bool(vip)
            request.vip_plan = vip.plan if vip else None
            return response


class SEOMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        response["X-Content-Type-Options"] = "nosniff"

        response["X-Frame-Options"] = "DENY"

        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


class JWTTokenCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get("access_token")

        if access_token:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

        return self.get_response(request)


class APICacheMiddleware(MiddlewareMixin):
    CACHE_TIMEOUT = 60 * 15

    def process_response(self, request, response):
        if request.method != "GET":
            return response

        if response.status_code != 200:
            return response

        if not request.path.startswith("/api/"):
            return response

        cache_key = f"api_cache_{request.path}_{request.GET.urlencode()}"

        cache.set(cache_key, response.content, self.CACHE_TIMEOUT)

        return response

    def process_request(self, request):
        if request.method != "GET":
            return None

        if not request.path.startswith("/api/"):
            return None

        cache_key = f"api_cache_{request.path}_{request.GET.urlencode()}"
        cached_content = cache.get(cache_key)

        if cached_content:
            from django.http import HttpResponse

            return HttpResponse(cached_content, content_type="application/json")

        return None


class RequestIdMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "X-Request-ID" in request.META:
            request_id = request.META["X-Request-ID"]
        else:
            request_id = uuid.uuid4().hex

        request.request_id = request_id

        response = self.get_response(request)

        if response is not None:
            response["X-Request-ID"] = request_id
            response["X-Request-Timestamp"] = timezone.now().isoformat()

        return response
