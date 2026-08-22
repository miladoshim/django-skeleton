# apps/accounts/services/session_service.py
from django.contrib.sessions.models import Session
from django.utils import timezone
from apps.accounts.models import UserSession


class SessionService:
    """مدیریت نشست‌های کاربر"""

    def __init__(self, user):
        self.user = user

    def get_sessions(self):
        return UserSession.objects.filter(user=self.user, is_active=True)

    def terminate(self, session_id):
        session = UserSession.objects.filter(
            user=self.user,
            id=session_id,
            is_active=True,
        ).first()

        if not session:
            return {"success": False, "message": "نشست یافت نشد"}

        if session.is_current:
            return {"success": False, "message": "نمی‌توانید نشست فعلی را ببندید"}

        session.terminate()
        return {"success": True, "message": "نشست پایان یافت"}

    def terminate_all(self, current_key=None):
        """پایان همه نشست‌ها به جز فعلی"""
        if not current_key:
            current = UserSession.objects.filter(
                user=self.user, is_current=True
            ).first()
            current_key = current.session_key if current else None

        sessions = UserSession.objects.filter(user=self.user, is_active=True).exclude(
            session_key=current_key
        )

        count = sessions.count()
        for s in sessions:
            s.terminate()

        return {"success": True, "message": f"{count} نشست پایان یافت"}

    def format(self, sessions):
        current_key = (
            UserSession.objects.filter(user=self.user, is_current=True)
            .values_list("session_key", flat=True)
            .first()
        )

        return [
            {
                "id": s.id,
                "device": {"mobile": "📱", "tablet": "📟", "desktop": "💻"}.get(
                    s.device, "❓"
                ),
                "browser": s.browser,
                "os": s.os,
                "ip": s.ip,
                "is_current": s.session_key == current_key,
                "last_login_at": s.last_login_at,
                "created_at": s.created_at,
                "duration": str(timezone.now() - s.created_at).split(".")[0],
            }
            for s in sessions
        ]
