# https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
# from channels.routing import ProtocolTypeRouter, URLRouter
# import apps.notifications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skeleton.environments.development')

asgi_application = get_asgi_application()

# websocket_urlpatterns = []
# websocket_urlpatterns += apps.notifications.routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    'http' : asgi_application,
    # 'websocket' : AuthMiddlewareStack({
    #     URLRouter(
    #         websocket_urlpatterns
    #     ),
    # })
})