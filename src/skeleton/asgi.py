"""
ASGI config for skeleton project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skeleton.environments.development')

application = get_asgi_application()



# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djshop.envs.development')

# asgi_application = get_asgi_application()

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter

# import apps.notifications.routing

# websocket_urlpatterns = []
# websocket_urlpatterns += apps.notifications.routing.websocket_urlpatterns

# application = ProtocolTypeRouter({
#     'http' : asgi_application,
#     'websocket' : AuthMiddlewareStack({
#         URLRouter(
#             websocket_urlpatterns
#         ),
#     })
# })