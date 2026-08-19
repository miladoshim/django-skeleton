import strawberry
import strawberry.django
from typing import Optional
from strawberry import auto
from datetime import datetime

from apps.accounts.models import User


@strawberry.django.type(User)
class UserType:
    id: strawberry.ID
    uuid: auto
    username: auto
    email: auto
    mobile: auto
    first_name: auto
    last_name: auto
    is_staff: bool
    is_active: bool
    created_at: auto

    @strawberry.field
    def full_name(self) -> str:
        return self.full_name

    @strawberry.field
    def posts_count(self) -> int:
        return self.posts.count()

    @strawberry.field
    def comments_count(self) -> int:
        return self.comments.count()


@strawberry.django.type(User)
class UserProfileType:
    id: strawberry.ID
    avatar: Optional[str]
    bio: Optional[str]
    banner: Optional[str]
