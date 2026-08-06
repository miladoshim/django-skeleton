from django.db.models import Q
import strawberry
from typing import List, Optional
from strawberry.types import Info
from apps.blog.models import Post, Category
from apps.blog.graphql.types import PostType, CategoryType, TagType, CommentType


@strawberry.type
class PostQuery:

    @strawberry.field
    def get_post(
        self, info: Info, id: Optional[str] = None, slug: Optional[str] = None
    ) -> Optional[PostType]:
        if id:
            post = Post.published.filter(id=id).first()
        elif slug:
            post = Post.published.filter(slug=slug).first()
        else:
            return None

        if not post:
            raise ValueError("پست پیدا نشد")

        # post.increment_views()

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
        order_by: str = "-published_at",
    ) -> List[PostType]:
        """لیست پست‌ها با فیلترهای مختلف"""

        queryset = Post.published.all()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(content__icontains=search)
                | Q(excerpt__icontains=search)
                | Q(tags__name__icontains=search)
            ).distinct()

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        if author_username:
            queryset = queryset.filter(author__username=author_username)

        if order_by.startswith("-"):
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by(order_by)

        # صفحه‌بندی
        offset = (page - 1) * limit
        return queryset[offset : offset + limit]

    @strawberry.field
    def search_posts(self, info: Info, query: str, limit: int = 10) -> List[PostType]:

        from django.db.models import Q

        return Post.objects.filter(
            Q(is_published=True)
            & (
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(excerpt__icontains=query)
                | Q(tags__name__icontains=query)
                | Q(category__name__icontains=query)
            )
        ).distinct()[:limit]

    @strawberry.field
    def popular_posts(self, info: Info, limit: int = 5) -> List[PostType]:
        return Post.published.all().order_by("-views_count")[:limit]

    @strawberry.field
    def latest_posts(self, info: Info, limit: int = 5) -> List[PostType]:

        return Post.objects.filter(is_published=True).order_by("-published_at")[:limit]

    @strawberry.field
    def my_posts(self, info: Info, include_drafts: bool = False) -> List[PostType]:
        """پست‌های من"""

        user = info.context.request.user
        if not user.is_authenticated:
            raise ValueError("ابتدا وارد شوید")

        queryset = Post.objects.filter(author=user)

        if not include_drafts:
            queryset = queryset.filter(is_published=True)

        return queryset

    @strawberry.field
    def related_posts(self, info: Info, post_id: str, limit: int = 3) -> List[PostType]:
        """پست‌های مرتبط"""

        post = Post.objects.filter(id=post_id, is_published=True).first()
        if not post:
            return []

        # بر اساس دسته‌بندی و برچسب‌ها
        related = Post.objects.filter(
            is_published=True,
            category=post.category,
        ).exclude(id=post.id)

        # اگر کمتر از limit بود، از برچسب‌ها هم اضافه کن
        if related.count() < limit:
            tag_posts = (
                Post.objects.filter(is_published=True, tags__in=post.tags.all())
                .exclude(id=post.id)
                .exclude(id__in=related.values("id"))
            )
            related = (related | tag_posts).distinct()

        return related[:limit]

    # ---------- Category Queries ----------
    @strawberry.field
    def list_categories(
        self, info: Info, include_counts: bool = True
    ) -> List[CategoryType]:
        """لیست همه دسته‌بندی‌ها"""

        return Category.objects.all().order_by("name")

    @strawberry.field
    def get_category(
        self, info: Info, id: Optional[str] = None, slug: Optional[str] = None
    ) -> Optional[CategoryType]:
        """دریافت یک دسته‌بندی"""

        if id:
            return Category.objects.filter(id=id).first()
        if slug:
            return Category.objects.filter(slug=slug).first()
        return None

    @strawberry.field
    def category_posts(
        self, info: Info, category_id: str, page: int = 1, limit: int = 10
    ) -> List[PostType]:
        """پست‌های یک دسته‌بندی"""

        offset = (page - 1) * limit
        return Post.objects.filter(category_id=category_id, is_published=True)[
            offset : offset + limit
        ]

    # ---------- Tag Queries ----------
    @strawberry.field
    def list_tags(self, info: Info, search: Optional[str] = None) -> List[TagType]:
        """لیست همه برچسب‌ها"""

        queryset = Tag.objects.all().order_by("name")

        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    @strawberry.field
    def get_tag(
        self, info: Info, id: Optional[str] = None, slug: Optional[str] = None
    ) -> Optional[TagType]:
        """دریافت یک برچسب"""

        if id:
            return Tag.objects.filter(id=id).first()
        if slug:
            return Tag.objects.filter(slug=slug).first()
        return None

    @strawberry.field
    def tag_posts(
        self, info: Info, tag_id: str, page: int = 1, limit: int = 10
    ) -> List[PostType]:
        """پست‌های یک برچسب"""

        offset = (page - 1) * limit
        return Post.objects.filter(tags__id=tag_id, is_published=True)[
            offset : offset + limit
        ]

    # ---------- Comment Queries ----------
    @strawberry.field
    def list_comments(
        self,
        info: Info,
        post_id: str,
        page: int = 1,
        limit: int = 20,
        only_approved: bool = True,
    ) -> List[CommentType]:
        """کامنت‌های یک پست"""

        queryset = Comment.objects.filter(post_id=post_id)

        if only_approved:
            queryset = queryset.filter(is_approved=True)

        offset = (page - 1) * limit
        return queryset[offset : offset + limit]

    # ---------- Stats ----------
    # @strawberry.field
    # def blog_stats(self, info: Info) -> BlogStatsType:
    #     """آمار کلی بلاگ"""

    #     return BlogStatsType(
    #         total_posts=Post.objects.filter(is_published=True).count(),
    #         total_categories=Category.objects.count(),
    #         total_tags=Tag.objects.count(),
    #         total_comments=Comment.objects.filter(is_approved=True).count(),
    #         total_users=User.objects.count(),
    #         total_views=Post.objects.aggregate(models.Sum("views_count"))[
    #             "views_count__sum"
    #         ]
    #         or 0,
    #     )
