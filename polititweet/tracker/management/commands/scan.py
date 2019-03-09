import tweepy
import random

from django.core.management.base import BaseCommand, CommandError
from ...models import Tweet, User
from django.conf import settings

from twython import TwythonStreamer

class Command(BaseCommand):
    help = 'Update database entries of all followed users'

    def handle(self, *args, **options):
        self.stdout.write("Connecting to Twitter...")
        auth = tweepy.OAuthHandler(settings.TWITTER_CREDENTIALS["consumer_key"], settings.TWITTER_CREDENTIALS["consumer_secret"])
        auth.set_access_token(settings.TWITTER_CREDENTIALS["access_token"], settings.TWITTER_CREDENTIALS["access_secret"])
        api = tweepy.API(auth)
        following = api.friends_ids()
        self.stdout.write("Connected to Twitter.")

        self.stdout.write("Starting update on %s users..." % str(len(following)))
        completed = 0
        random.shuffle(following) # shuffle order to get even coverage
        for id in following:
            user_data = None
            try:
                user_data = api.get_user(id, wait_on_rate_limit=True)
            except tweepy.error.TweepError as e:
                self.stderr.write(str(e))
                continue
            try:
                user = User.objects.get(user_id=id)
                self.stdout.write("User @%s already exists; updating record..." % user_data.screen_name)
                user.full_data = user_data._json
                user.save()
            except Exception as e: # does not exist; TODO: use more specific error
                self.stdout.write("User @%s does not exist; creating record..." % user_data.screen_name)
                user = User(user_id=id, full_data=user_data._json)
                user.save()
            completed += 1
            self.stdout.write(self.style.SUCCESS("Successfully updated @%s (%s/%s)." % (user_data.screen_name, str(completed), str(len(following)))))
        self.stdout.write(self.style.SUCCESS("Finished refreshing %s accounts." % str(len(following))))