from friendship.models import Follow
from apps.accounts.models import User


def add_follower(user: User, follower: User):
    return Follow.objects.add_follower(user, follower)
