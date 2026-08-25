from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from apps.blog.models import Category
from apps.core.services.base_service import BaseService

User = get_user_model()


class CategoryService(BaseService):
    model = Category
    MAX_TITLE_LENGTH = 200
    MIN_CONTENT_LENGTH = 10

    def list_categories(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:

        queryset = self.get_queryset()

        if category:
            queryset = queryset.filter(category__slug=category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(short_description__icontains=search)
                | Q(body__icontains=search)
            )

        queryset = queryset.order_by("-created_at")

        paginator = Paginator(queryset, page_size)
        categorys = paginator.get_page(page)

        return {
            "items": categorys.object_list,
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "has_next": categorys.has_next(),
            "has_previous": categorys.has_previous(),
        }

    def get_category_detail(
        self,
        request,
        slug: str,
    ) -> Optional[Category]:
        queryset = self.get_queryset()

        category = queryset.filter(slug=slug).first()
        if category:
            hit_count = HitCount.objects.get_for_object(category)
            HitCountMixin.hit_count(request, hit_count)

        return category

    @transaction.atomic
    def create_category(
        self,
        title: str,
        content: str,
        author: User,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Category:

        if not author.is_staff:
            raise PermissionDenied("شما اجازه ویرایش این پست را ندارید")

        if len(title) > self.MAX_TITLE_LENGTH:
            raise ValueError(
                f"عنوان نمیتواند بیشتر از {self.MAX_TITLE_LENGTH} کاراکتر باشد"
            )

        if len(content) < self.MIN_CONTENT_LENGTH:
            raise ValueError(f"محتوا حداقل باید {self.MIN_CONTENT_LENGTH} کاراکتر باشد")

        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        category = self.model.objects.create(
            title=title,
            content=content,
            author=author,
            slug=slug,
            category_id=category_id,
        )

        if tags:
            category.tags.add(*tags)

        return category

    @transaction.atomic
    def update_category(
        self,
        category: Category,
        user: User,
        **validated_data,
    ) -> Category:

        if not user.is_staff:
            raise PermissionDenied("شما اجازه ویرایش این پست را ندارید")

        if "title" in validated_data:
            validated_data["slug"] = slugify(validated_data["title"])

        return self.update(category, **validated_data)
