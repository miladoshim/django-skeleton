from django.core.cache import cache
from apps.core.models import TopBarTimerMessage


def global_variables(request):
    topbar_messages = cache.get("topbar:messages")
    if topbar_messages is None:
        topbar_messages = TopBarTimerMessage.objects.order_by("-created_at")
        cache.set("topbar:messages", topbar_messages, timeout=60 * 30)
    return {"timer_messages": topbar_messages}
