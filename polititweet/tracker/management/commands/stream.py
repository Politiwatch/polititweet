from django.core.management.base import BaseCommand, CommandError
from ...models import Tweet, User
from django.conf import settings

class Command(BaseCommand):
    help = 'Stream new tweets from monitored users into the database'

    def handle(self, *args, **options):
        self.stdout.write("Loading accounts to track...")
        