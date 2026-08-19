from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from django.core.exceptions import PermissionDenied
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from apps.blog.models import Post
from apps.core.services.base_service import BaseService

User = get_user_model()


class PostService(BaseService):
    model = Post
    MAX_TITLE_LENGTH = 200
    MIN_CONTENT_LENGTH = 10

    def list_public_posts(
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
        posts = paginator.get_page(page)

        return {
            "items": posts.object_list,
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "has_next": posts.has_next(),
            "has_previous": posts.has_previous(),
        }

    def get_post_detail(
        self,
        request,
        post_slug: str,
    ) -> Optional[Post]:
        queryset = self.get_queryset()

        post = queryset.filter(slug=post_slug).first()
        if post:
            hit_count = HitCount.objects.get_for_object(post)
            HitCountMixin.hit_count(request, hit_count)

        return post

    def list_my_posts(
        self,
        user: Optional[User] = None,  # type: ignore
        is_published: Optional[bool] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        لیست پستها با فیلترهای مختلف
        استفاده مشترک در وب، API و GraphQL
        """
        queryset = self.get_queryset()

        # فیلتر بر اساس وضعیت انتشار
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published)

        # فیلتر بر اساس دسته
        if category:
            queryset = queryset.filter(category__slug=category)

        # جستجو
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        # اگر کاربر نویسنده نیست، فقط پستهای منتشر شده
        if user and not user.is_staff:
            queryset = queryset.filter(Q(is_published=True) | Q(author=user))

        # مرتبسازی
        queryset = queryset.order_by("-created_at")

        # صفحهبندی
        paginator = Paginator(queryset, page_size)
        posts = paginator.get_page(page)

        return {
            "items": posts.object_list,
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "has_next": posts.has_next(),
            "has_previous": posts.has_previous(),
        }

    @transaction.atomic
    def create_post(
        self,
        title: str,
        content: str,
        author: User,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Post:
        """ایجاد پست جدید با اعتبارسنجی"""

        # اعتبارسنجی طول عنوان
        if len(title) > self.MAX_TITLE_LENGTH:
            raise ValueError(
                f"عنوان نمیتواند بیشتر از {self.MAX_TITLE_LENGTH} کاراکتر باشد"
            )

        # اعتبارسنجی محتوا
        if len(content) < self.MIN_CONTENT_LENGTH:
            raise ValueError(f"محتوا حداقل باید {self.MIN_CONTENT_LENGTH} کاراکتر باشد")

        # ساخت اسلاگ یکتا
        from django.utils.text import slugify

        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # ایجاد پست
        post = self.model.objects.create(
            title=title,
            content=content,
            author=author,
            slug=slug,
            category_id=category_id,
        )

        # افزودن تگها
        if tags:
            post.tags.add(*tags)

        return post

    @transaction.atomic
    def update_post(self, post: Post, user: User, **validated_data) -> Post:
        """بهروزرسانی پست با بررسی دسترسی"""

        # بررسی دسترسی نویسنده
        if post.author != user and not user.is_staff:
            raise PermissionDenied("شما اجازه ویرایش این پست را ندارید")

        # اگر اسلاگ تغییر کرد
        if "title" in validated_data:
            validated_data["slug"] = slugify(validated_data["title"])

        return self.update(post, **validated_data)

    @transaction.atomic
    def publish_post(self, post: Post, user: User) -> Post:
        """انتشار پست"""
        if not user.has_perm("core.can_publish_post"):
            raise PermissionDenied("شما مجوز انتشار پست را ندارید")

        post.is_published = True
        post.published_at = timezone.now()
        post.save(update_fields=["is_published", "published_at"])
        return post

    @transaction.atomic
    def unpublish_post(self, post: Post, user: User) -> Post:
        """لغو انتشار پست"""
        if post.author != user and not user.is_staff:
            raise PermissionDenied("شما اجازه لغو انتشار را ندارید")

        post.is_published = False
        post.save(update_fields=["is_published"])
        return post

    def get_user_posts(self, user: User) -> QuerySet:
        """پستهای یک کاربر"""
        return self.get_queryset().filter(author=user)

    def get_popular_posts(self, limit: int = 5) -> QuerySet:
        """پستهای محبوب"""
        return (
            self.get_queryset()
            .filter(is_published=True)
            .order_by("-views_count", "-likes_count")[:limit]
        )

    def add_like(self, post: Post, user: User) -> bool:
        """افزودن لایک"""
        if user in post.likes.all():
            post.likes.remove(user)
            return False
        post.likes.add(user)
        return True
