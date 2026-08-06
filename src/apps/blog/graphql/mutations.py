import strawberry
from typing import List, Optional
from strawberry.types import Info
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.blog.models import Post, Category, Tag, Comment
from apps.blog.graphql.types import PostType, CategoryType, TagType, CommentType
from apps.blog.validators import PostValidators


@strawberry.input
class PostInput:
    """Input برای ایجاد/ویرایش پست"""

    title: str
    content: str
    category_id: Optional[str] = None
    tag_ids: Optional[List[str]] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


@strawberry.type
class PostMutation:
    """Mutation های CRUD پست"""

    # ---------- CREATE ----------
    @strawberry.mutation
    def create_post(self, info: Info, input: PostInput) -> PostType:
        """ایجاد پست جدید"""

        user = info.context.request.user
        if not user.is_authenticated:
            raise ValueError("ابتدا وارد شوید")

        # اعتبارسنجی
        try:
            PostValidators.validate_title(input.title)
            PostValidators.validate_content(input.content)
            if input.excerpt:
                PostValidators.validate_excerpt(input.excerpt)
        except ValidationError as e:
            raise ValueError(str(e))

        with transaction.atomic():
            # ایجاد پست
            post = Post.objects.create(
                title=input.title,
                content=input.content,
                excerpt=input.excerpt or "",
                author=user,
                featured_image=input.featured_image or "",
                meta_title=input.meta_title or input.title[:200],
                meta_description=input.meta_description or input.excerpt or "",
            )

            # افزودن دسته‌بندی
            if input.category_id:
                category = Category.objects.filter(id=input.category_id).first()
                if category:
                    post.category = category

            # افزودن برچسب‌ها
            if input.tag_ids:
                tags = Tag.objects.filter(id__in=input.tag_ids)
                post.tags.set(tags)

            post.save()

        return post

    # ---------- READ ----------
    @strawberry.field
    def get_post(self, info: Info, id: str) -> Optional[PostType]:
        """دریافت یک پست"""

        post = Post.objects.filter(id=id).first()

        # بررسی دسترسی
        if not post:
            raise ValueError("پست پیدا نشد")

        if not post.is_published:
            user = info.context.request.user
            if not user.is_authenticated or (post.author != user and not user.is_staff):
                raise ValueError("پست پیدا نشد")

        # افزایش بازدید
        post.increment_views()

        return post

    @strawberry.field
    def get_post_by_slug(self, info: Info, slug: str) -> Optional[PostType]:
        """دریافت پست با اسلاگ"""

        post = Post.objects.filter(slug=slug, is_published=True).first()

        if not post:
            raise ValueError("پست پیدا نشد")

        # افزایش بازدید
        post.increment_views()

        return post

    @strawberry.field
    def list_posts(
        self,
        info: Info,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        category_slug: Optional[str] = None,
        tag_slug: Optional[str] = None,
        author_username: Optional[str] = None,
    ) -> List[PostType]:
        """لیست پست‌ها با فیلتر"""

        queryset = Post.objects.filter(is_published=True)

        # جستجو
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search)
                | models.Q(content__icontains=search)
                | models.Q(excerpt__icontains=search)
            )

        # فیلتر دسته‌بندی
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # فیلتر برچسب
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # فیلتر نویسنده
        if author_username:
            queryset = queryset.filter(author__username=author_username)

        # صفحه‌بندی
        offset = (page - 1) * limit
        return queryset[offset : offset + limit]

    # ---------- UPDATE ----------
    @strawberry.mutation
    def update_post(
        self,
        info: Info,
        id: str,
        input: Optional[PostInput] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> PostType:
        """ویرایش پست"""

        user = info.context.request.user
        if not user.is_authenticated:
            raise ValueError("ابتدا وارد شوید")

        post = Post.objects.filter(id=id).first()
        if not post:
            raise ValueError("پست پیدا نشد")

        # بررسی دسترسی
        if post.author != user and not user.is_staff:
            raise ValueError("شما اجازه ویرایش این پست را ندارید")

        with transaction.atomic():
            # به‌روزرسانی فیلدها
            if input:
                if input.title:
                    post.title = input.title
                if input.content:
                    post.content = input.content
                if input.excerpt is not None:
                    post.excerpt = input.excerpt
                if input.featured_image:
                    post.featured_image = input.featured_image
                if input.meta_title:
                    post.meta_title = input.meta_title
                if input.meta_description:
                    post.meta_description = input.meta_description

                # آپدیت دسته‌بندی
                if input.category_id:
                    category = Category.objects.filter(id=input.category_id).first()
                    if category:
                        post.category = category
                elif input.category_id == "":
                    post.category = None

                # آپدیت برچسب‌ها
                if input.tag_ids is not None:
                    if input.tag_ids:
                        tags = Tag.objects.filter(id__in=input.tag_ids)
                        post.tags.set(tags)
                    else:
                        post.tags.clear()

            post.save()

        return post

    # ---------- DELETE ----------
    @strawberry.mutation
    def delete_post(self, info: Info, id: str) -> bool:
        """حذف پست"""

        user = info.context.request.user
        if not user.is_authenticated:
            raise ValueError("ابتدا وارد شوید")

        post = Post.objects.filter(id=id).first()
        if not post:
            raise ValueError("پست پیدا نشد")

        # بررسی دسترسی
        if post.author != user and not user.is_staff:
            raise ValueError("شما اجازه حذف این پست را ندارید")

        post.delete()
        return True

    # ---------- PUBLISH ----------
    @strawberry.mutation
    def publish_post(self, info: Info, id: str) -> PostType:
        """انتشار پست"""

        user = info.context.request.user
        if not user.is_authenticated or not user.is_staff:
            raise ValueError("شما مجوز انتشار پست را ندارید")

        post = Post.objects.filter(id=id).first()
        if not post:
            raise ValueError("پست پیدا نشد")

        post.publish()
        return post

    @strawberry.mutation
    def unpublish_post(self, info: Info, id: str) -> PostType:
        """لغو انتشار پست"""

        user = info.context.request.user
        if not user.is_authenticated or not user.is_staff:
            raise ValueError("شما مجوز لغو انتشار را ندارید")

        post = Post.objects.filter(id=id).first()
        if not post:
            raise ValueError("پست پیدا نشد")

        post.unpublish()
        return post

    # ---------- LIKE ----------
    @strawberry.mutation
    def like_post(self, info: Info, id: str) -> bool:
        """لایک/آنلایک پست"""

        user = info.context.request.user
        if not user.is_authenticated:
            raise ValueError("ابتدا وارد شوید")

        post = Post.objects.filter(id=id).first()
        if not post:
            raise ValueError("پست پیدا نشد")

        if user in post.likes.all():
            post.likes.remove(user)
            return False
        else:
            post.likes.add(user)
            return True
