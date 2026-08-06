from typing import List, Optional
from datetime import datetime
import strawberry
import strawberry.django
from strawberry import auto
from apps.blog import models
from apps.accounts.graphql.types import UserType, UserPublicType


@strawberry.django.type(models.Category)
class CategoryType:
    id: strawberry.ID
    name: auto
    slug: auto
    description: auto
    created_at: auto
    parent: Optional["CategoryType"]

    @strawberry.field
    def posts_count(self) -> int:
        return self.posts.filter(is_published=True).count()

    @strawberry.field
    def children_count(self) -> int:
        return self.children.count()


@strawberry.django.type(models.Tag)
class TagType:
    id: strawberry.ID
    name: auto
    slug: auto
    created_at: auto

    @strawberry.field
    def posts_count(self) -> int:
        return self.posts.filter(is_published=True).count()


@strawberry.django.type(models.Post)
class PostType:
    id: strawberry.ID
    title: auto
    slug: auto
    content: auto
    excerpt: auto
    featured_image: auto
    status: auto
    is_published: auto
    published_at: Optional[datetime]
    created_at: auto
    updated_at: auto
    views_count: int
    likes_count: int
    comments_count: int
    tag_list: str
    author: UserPublicType
    category: Optional[CategoryType]
    tags: List[TagType]

    @strawberry.field
    def formatted_date(self) -> str:
        return self.published_at or self.created_at

    @strawberry.field
    def formatted_content(self, limit: Optional[int] = None) -> str:
        if limit and len(self.content) > limit:
            return self.content[:limit] + "..."
        return self.content

    @strawberry.field
    def is_liked(self, info) -> bool:
        if not info.context.request.user.is_authenticated:
            return False
        return self.likes.filter(id=info.context.request.user.id).exists()


@strawberry.django.type(models.Comment)
class CommentType:
    id: strawberry.ID
    content: auto
    is_approved: bool
    created_at: auto
    author: UserPublicType
    post: PostType

    @strawberry.field
    def replies_count(self) -> int:
        return self.replies.filter(is_approved=True).count()


@strawberry.django.type(models.Post)
class PostListType(PostType):
    """Type ساده برای لیست پست‌ها (بدون محتوا کامل)"""

    content: strawberry.auto  # Override to hide in list
