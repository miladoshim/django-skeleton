from django.utils import timezone
from utils.helpers import get_user_agent, get_user_ip_address
from .models import UserSession


class SaveUserSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            self._save_session(request)

        return response

    def _save_session(self, request):
        session_key = request.session.session_key or self._create_session(request)

        UserSession.objects.filter(session_key=session_key).update(
            last_login_at=timezone.now()
        )

        if not UserSession.objects.filter(session_key=session_key).exists():
            ua = get_user_agent(request)

            UserSession.objects.create(
                user=request.user,
                session_key=session_key,
                ip=get_user_ip_address(request),
                device=self._get_device(ua),
                browser=self._get_browser(ua),
                os=self._get_os(ua),
                is_current=True,
            )

            # غیرفعال کردن نشست‌های قبلی
            # UserSession.objects.filter(user=request.user).exclude(
            #     session_key=session_key
            # ).update(is_current=False)

    def _create_session(self, request):
        request.session.save()
        return request.session.session_key

    def _get_device(self, ua):
        if "mobile" in ua or "android" in ua:
            return "mobile"
        if "tablet" in ua or "ipad" in ua:
            return "tablet"
        return "desktop"

    def _get_browser(self, ua):
        if "chrome" in ua and "edge" not in ua:
            return "Chrome"
        if "firefox" in ua:
            return "Firefox"
        if "safari" in ua and "chrome" not in ua:
            return "Safari"
        if "edge" in ua:
            return "Edge"
        return "Unknown"

    def _get_os(self, ua):
        if "windows" in ua:
            return "Windows"
        if "mac" in ua:
            return "MacOS"
        if "linux" in ua:
            return "Linux"
        if "android" in ua:
            return "Android"
        if "iphone" in ua or "ipad" in ua:
            return "iOS"
        return "Unknown"
