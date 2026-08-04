from django.urls import path
from .views import callback_gateway_view, go_to_gateway_view

app_name = 'apps.financial'

urlpatterns = [
    path('pay/', go_to_gateway_view, name='pay'),
    path('callback/', callback_gateway_view, name='callback_gateway'),
]
