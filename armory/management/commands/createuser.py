from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a regular user"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("--email", type=str, default="")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]

        if User.objects.filter(username=username).exists():
            self.stderr.write(self.style.ERROR(f"User '{username}' already exists"))
            return

        user = User.objects.create_user(username, email, password)
        self.stdout.write(self.style.SUCCESS(f"User '{username}' created"))
