# from django.core.cache import cache
# from django.db.models.signals import post_delete, post_save
# from django.dispatch import receiver
# from rest_framework.authtoken.models import Token
# from drf_api_logger import API_LOGGER_SIGNAL

# @receiver([post_delete, post_save], sender=Post)
# def invalidate_product_cache(sender, instance, **kwargs):
#     cache.delete_pattern('*post_list*')
# @receiver(post_save, sender=User)
# def create_auth_token(sender, instance, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)


# def log_to_file(**kwargs):
#     """Log API data to file"""
#     with open("api_logs.json", "a") as f:
#         json.dump(kwargs, f)
#         f.write("\n")


# def send_to_analytics(**kwargs):
#     """Send API data to analytics service"""
#     analytics_service.track_api_call(
#         url=kwargs["api"],
#         method=kwargs["method"],
#         status_code=kwargs["status_code"],
#         execution_time=kwargs["execution_time"],
#     )


# Subscribe to signals
# API_LOGGER_SIGNAL.listen += log_to_file
# API_LOGGER_SIGNAL.listen += send_to_analytics
# Unsubscribe when needed
# API_LOGGER_SIGNAL.listen -= log_to_file
