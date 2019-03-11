import tweepy
import random

from django.core.management.base import BaseCommand, CommandError
from ...models import Tweet, User
from django.conf import settings

from twython import TwythonStreamer


class Command(BaseCommand):
    help = 'Update database entries of all followed users'

    def add_arguments(self, parser):
        parser.add_argument(
                '--infinite',
                action='store_true',
                dest='repeat',
                help='Just keep updating forever',
            )

    def handle(self, *args, **options):
        def scan():
            self.stdout.write("Connecting to Twitter...")
            auth = tweepy.OAuthHandler(
                settings.TWITTER_CREDENTIALS["consumer_key"], settings.TWITTER_CREDENTIALS["consumer_secret"])
            auth.set_access_token(
                settings.TWITTER_CREDENTIALS["access_token"], settings.TWITTER_CREDENTIALS["access_secret"])
            api = tweepy.API(auth, wait_on_rate_limit=True,
                            wait_on_rate_limit_notify=True)
            following = api.friends_ids()
            self.stdout.write("Connected to Twitter.")

            self.stdout.write("Starting update on %s users..." %
                            str(len(following)))
            completed = 0
            flagged_accounts = [user.user_id for user in User.objects.filter(flagged=True)]
            random.shuffle(following)  # shuffle order to get even coverage
            for id in flagged_accounts + [id for id in following if id not in flagged_accounts]:
                try:
                    user_data = None
                    try:
                        user_data = api.get_user(id)
                    except tweepy.error.TweepError as e:
                        self.stderr.write(str(e))
                        continue  # important to continue, and to _not_ mark all tweets as deleted
                    try:
                        user = User.objects.get(user_id=id)
                        self.stdout.write(
                            "User @%s already exists; updating record..." % user_data.screen_name)
                        user.full_data = user_data._json
                        user.deleted_count = Tweet.objects.filter(user=user, deleted=True).count()
                        user.save()
                        upsertTweets(api.user_timeline(
                            user_id=user.user_id, count=200), user)
                    except User.DoesNotExist as e:  # does not exist; TODO: use more specific error
                        self.stdout.write(
                            "User @%s does not exist; creating record..." % user_data.screen_name)
                        user = User(user_id=id, full_data=user_data._json)
                        user.save()
                        upsertTweets(getAllStatuses(api, user), user)
                    if hasAccountDeletedTweet(api, user, user_data):
                        self.stdout.write(
                            "Also checking @%s for deleted tweets..." % user_data.screen_name)
                        deleted_count = scanForDeletedTweet(api, user)
                        self.stdout.write(self.style.SUCCESS("Found %s new deleted tweets for @%s" % (
                            str(deleted_count), user_data.screen_name)))
                        user.flagged = False
                        user.save()
                    completed += 1
                except Exception as e:
                    self.stderr.write("Encountered an error while scanning %s: %s" % (str(id), str(e)))
                    continue
                self.stdout.write(self.style.SUCCESS("Successfully updated @%s (%s/%s)." %
                                                    (user_data.screen_name, str(completed), str(len(following)))))
            self.stdout.write(self.style.SUCCESS(
                "Finished refreshing %s accounts." % str(len(following))))
        scan()
        while options["repeat"]:
            scan()


def hasAccountDeletedTweet(api, user_db, user_data):
    if user_db.flagged:
        return True
    if user_data.statuses_count < user_db.full_data["statuses_count"]:
        return True
    latest_known_status = 0
    try:
        latest_known_status = user_db.full_data["status"]["id"]
    except: # not the prettiest...
        pass
    tweets_since = getAllStatuses(
        api, user_db, since=latest_known_status)
    return user_data.statuses_count - len(tweets_since) < user_db.full_data["statuses_count"]


def upsertTweets(tweets, user):
    for tweet in tweets:
        try:
            tweet_db = Tweet.objects.get(tweet_id=tweet.id)
            tweet_db.full_data = tweet._json
            tweet_db.save()
        except Tweet.DoesNotExist:
            tweet_db = Tweet(tweet_id=tweet.id,
                             full_data=tweet._json, user=user)
            tweet_db.save()


def getAllStatuses(api, user, since=None):
    tweets = []
    new_tweets = api.user_timeline(
        user_id=user.user_id, count=200, since_id=since)
    tweets.extend(new_tweets)
    while len(new_tweets) > 0:
        oldest = tweets[-1].id - 1
        new_tweets = api.user_timeline(
            user_id=user.user_id, count=200, max_id=oldest)
        tweets.extend(new_tweets)
    return tweets


def scanForDeletedTweet(api, user):
    known_tweets = Tweet.objects.filter(user=user, hibernated=False)
    found_tweets = sorted(getAllStatuses(api, user), key=lambda k: k.id)
    found_ids = [tweet.id for tweet in found_tweets]
    minimum_id = found_tweets[0].id
    total_deleted = 0
    for tweet in known_tweets:
        if tweet.tweet_id < minimum_id:
            if not tweet.hibernated:
                tweet.hibernated = True
                tweet.save()
            continue
        if tweet.tweet_id not in found_ids and not tweet.deleted:
            try:
                api.get_status(tweet.tweet_id)
            except Exception as e:
                tweet.deleted = True
                tweet.save()
                print("Found deleted tweet: %s by @%s" %
                      (str(tweet.tweet_id), user.full_data["screen_name"]))
                total_deleted += 1
        else:
            if tweet.deleted:
                tweet.deleted = False
                tweet.save()
    return total_deleted
