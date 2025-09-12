from django.db import models
from apps.core.models import BaseModel
from django.utils.translation import gettext_lazy as _


class Tag(BaseModel):
    title = models.CharField(max_length=255, unique=True,
                            verbose_name=_('عنوان'))
    slug = models.SlugField(max_length=255, unique=True,
                            verbose_name=_('اسلاگ'), blank=True)

    class Meta:
        db_table = 'tags'
        verbose_name = _("برچسب")
        verbose_name_plural = _("برچسب ها")

    def __str__(self) -> str:
        return self.title
