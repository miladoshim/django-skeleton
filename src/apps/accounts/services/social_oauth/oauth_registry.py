# apps/accounts/services/registry.py
from .oauth_github_service import GitHubService
from .oauth_google_service import GoogleService
from .oauth_gitlab_service import GitLabService
from .oauth_bitbucket_service import BitbucketService


class ServiceRegistry:
    _services = {
        "github": GitHubService,
        "google": GoogleService,
        "gitlab": GitLabService,
        "bitbucket": BitbucketService,
    }

    @classmethod
    def get_service(cls, provider):
        service_class = cls._services.get(provider)
        if not service_class:
            raise ValueError(f"سرویس {provider} پشتیبانی نمیشود")
        return service_class()

    @classmethod
    def register(cls, name, service_class):
        cls._services[name] = service_class

    @classmethod
    def get_available_providers(cls):
        return list(cls._services.keys())
