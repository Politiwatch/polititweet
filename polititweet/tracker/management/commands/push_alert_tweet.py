import tweepy

from django.core.management.base import BaseCommand, CommandError
from ...models import Tweet, User
from django.conf import settings
from django.utils import timezone
from django.shortcuts import reverse
import sys
import re

def _clean_tweet(string):
    string = re.sub(r'(https?):\/\/[^\s$.?#].[^\s]*', '(url)', string)
    string = string.replace("@", "﹫").replace("\n", " ")
    return string

class Command(BaseCommand):
    help = "Publish a deleted tweet to the alert account"

    def add_arguments(self, parser):
        parser.add_argument("since", type=int, help="lastd n minutes to consider")

    def handle(self, *args, **options):
        self.stdout.write("Finding the best tweet to publish...")
        since = options["since"]
        tweet = Tweet.get_current_top_deleted_tweet(since=options["since"], use_cache=False, fallback=False)
        if tweet is None:
            self.stdout.write("Unable to find viable tweet, halting...")
            return
        push_contents = f'{tweet.user.full_data["name"]} deleted: "{_clean_tweet(tweet.full_data["text"])}" https://polititweet.org/tweet?account={tweet.user.user_id}&tweet={tweet.tweet_id}'
        self.stdout.write("Authenticating with Twitter...")
        auth = tweepy.OAuthHandler(settings.ALERT_TWITTER_CREDENTIALS["consumer_key"], settings.ALERT_TWITTER_CREDENTIALS["consumer_secret"])
        auth.set_access_token(settings.ALERT_TWITTER_CREDENTIALS["access_token"], settings.ALERT_TWITTER_CREDENTIALS["access_secret"])
        api = tweepy.API(auth_handler=auth)
        api.update_status(push_contents)
        self.stdout.write("Published tweet: " + push_contents)

