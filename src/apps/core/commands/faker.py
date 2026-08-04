from apps.academy.factories import CourseFactory
from apps.accounts.factories import UserFactory
from apps.blog.factories import PostFactory, TagFactory
from apps.library.factories import BookFactory

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Seed the database with initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--amount",
            type=int,
            help="The amount of data to seed",
            default=100,
        )

        parser.add_argument(
            "--model",
            type=str,
            help="The model to faker and seed",
        )

    def _generate_posts(self, amount: int):
        for _ in range(amount):
            PostFactory(user=UserFactory())

    def _generate_users(self, amount: int):
        for _ in range(amount):
            UserFactory.create_batch(amount)

    def _generate_books(self, amount: int):
        for _ in range(amount):
            BookFactory.create_batch(amount)

    def _generate_courses(self, amount: int):
        for _ in range(amount):
            CourseFactory.create_batch(amount)

    def _generate_tags(self, amount: int):
        for _ in range(amount):
            TagFactory.create_batch(amount)

    def handle(self, *args, **options):
        amount = options.get("amount")

        model = options.get("model")

        if model == "user":
            print(f"Generating {amount} users...")
            self._generate_users(amount)
        elif model == "post":
            print(f"Generating {amount} posts...")
            self._generate_posts(amount)
        elif model == "book":
            print(f"Generating {amount} books...")
            self._generate_books(amount)
        elif model == "course":
            print(f"Generating {amount} courses...")
            self._generate_courses(amount)
        elif model == "tag":
            print(f"Generating {amount} tags...")
            self._generate_tags(amount)

        else:
            self.stderr.write(
                self.style.ERROR("Enter a model for generating -> --model=... ")
            )
