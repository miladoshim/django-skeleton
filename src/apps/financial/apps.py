from django.apps import AppConfig


class FinancialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.financial'
    verbose_name = 'مالی'
    
    def ready(self):
        import apps.financial.signals
