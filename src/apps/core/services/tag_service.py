from typing import Any, Dict, Optional
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from taggit.models import Tag, slugify
from apps.core.services.base_service import BaseService

User = get_user_model()


class TagService(BaseService):

    model = Tag
    MAX_TITLE_LENGTH = 200

    def list_tags(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:

        queryset = self.get_queryset()

        if search:
            queryset = queryset.filter(Q(title__icontains=search))

        paginator = Paginator(queryset, page_size)
        tags = paginator.get_page(page)

        return {
            "items": tags.object_list,
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "has_next": tags.has_next(),
            "has_previous": tags.has_previous(),
        }

    def get_tag_detail(self, tag_id: int) -> Optional[Tag]:
        queryset = self.get_queryset()
        tag = queryset.filter(id=tag_id).first()
        return tag

    @transaction.atomic
    def create_tag(
        self,
        name: str,
    ) -> Tag:

        if len(name) > self.MAX_TITLE_LENGTH:
            raise ValueError(
                f"عنوان نمیتواند بیشتر از {self.MAX_TITLE_LENGTH} کاراکتر باشد"
            )

        try:
            tag, _ = self.model.objects.get_or_create(name=name.lower().strip())
        except:
            pass

        return tag

    @transaction.atomic
    def update_tag(self, tag: Tag, user: User, **validated_data) -> Tag:

        if "name" in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])

        return self.update(tag, **validated_data)
