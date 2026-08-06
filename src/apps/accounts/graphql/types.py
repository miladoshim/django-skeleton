import strawberry
import strawberry.django
from typing import Optional
from strawberry import auto
from datetime import datetime

from apps.accounts import models


@strawberry.django.type(models.User)
class UserType:
    """Type کامل کاربر (برای خود کاربر)"""

    id: strawberry.ID
    email: auto
    username: auto
    first_name: auto
    last_name: auto
    bio: Optional[str]
    website: Optional[str]
    avatar: Optional[str]
    date_joined: datetime
    last_login: Optional[datetime]
    email_verified: bool
    is_staff: bool

    @strawberry.field
    def full_name(self) -> str:
        return self.full_name

    @strawberry.field
    def posts_count(self) -> int:
        return self.posts.count()

    @strawberry.field
    def comments_count(self) -> int:
        return self.comments.count()


@strawberry.django.type(models.User)
class UserPublicType:
    """Type عمومی کاربر (برای همه)"""

    id: strawberry.ID
    username: auto
    first_name: auto
    last_name: auto
    avatar: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    date_joined: datetime

    @strawberry.field
    def full_name(self) -> str:
        return self.full_name

    @strawberry.field
    def posts_count(self) -> int:
        return self.posts.filter(is_published=True).count()

    @strawberry.field
    def comments_count(self) -> int:
        return self.comments.filter(is_approved=True).count()
