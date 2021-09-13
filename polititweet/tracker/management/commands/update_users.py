import tweepy

from django.core.management.base import BaseCommand
from ...models import Tweet, User
from django.conf import settings
import sys


class Command(BaseCommand):
    help = "Updates all the users' metadata based on their latest tweet"

    def handle(self, *args, **options):
        global following
        self.stdout.write("Loading accounts to update...")
        users = User.objects.all()
        self.stdout.write("Loaded %s accounts to update." % str(len(users)))

        for user in users:
            latest_tweet = user.latest_tweet()
            if latest_tweet is None: continue
            latest_tweet.update_user_metadata()
            self.stdout.write(f"{latest_tweet.full_data['user']}")
            
            user.refresh_from_db()
            self.stdout.write("...updated metadata for " + self.style.SUCCESS("@" + user.full_data["screen_name"]))

        self.stdout.write(self.style.SUCCESS("Update complete!"))
