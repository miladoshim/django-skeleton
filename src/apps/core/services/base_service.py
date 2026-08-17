from typing import Any
from django.db import transaction
from django.db.models import QuerySet


class BaseService:
    model = None
    queryset = None

    def __init__(self, user=None, request=None):
        self.user = user
        self.request = request

    def get_queryset(self) -> QuerySet:
        if self.queryset is None:
            return self.model.objects.all()
        return self.queryset

    def list(self, **filters) -> QuerySet:
        qs = self.get_queryset()
        return qs.filter(**filters) if filters else qs

    def get(self, pk: int, **kwargs):
        try:
            return self.get_queryset().get(pk=pk, **kwargs)
        except self.model.DoesNotExist:
            return None

    def create(self, **data) -> Any:
        return self.model.objects.create(**data)

    def update(self, instance, **data) -> Any:
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    @transaction.atomic
    def delete(self, instance) -> bool:
        instance.delete()
        return True

    def get_or_create(self, **kwargs):
        return self.model.objects.get_or_create(**kwargs)

    def count(self, **filters) -> int:
        return self.get_queryset().filter(**filters).count()
