from django.core.management.base import BaseCommand
from video_meeting_app.models import User


class Command(BaseCommand):
    help = "Create random users"

    def add_arguments(self, parser):
        parser.add_argument(
            "total", type=int, help="Indicates the number of users to be created"
        )

    def handle(self, *args, **kwargs):
        total = kwargs["total"]
        for i in range(total):
            User.objects.create(name=f"user{i+1}")
        self.stdout.write(self.style.SUCCESS(f"{total} users were created!"))
