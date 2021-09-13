import tweepy

from django.core.management.base import BaseCommand
from ...models import Tweet, User
from django.conf import settings
import sys

following = []


class Command(BaseCommand):
    help = "Stream new tweets from monitored users into the database"

    def handle(self, *args, **options):
        global following
        self.stdout.write("Loading accounts to track...")
        users = User.objects.all()
        self.stdout.write("Loaded %s accounts to track." % str(len(users)))

        self.stdout.write("Connecting to Twitter...")
        auth = tweepy.OAuthHandler(
            settings.TWITTER_CREDENTIALS["consumer_key"],
            settings.TWITTER_CREDENTIALS["consumer_secret"],
        )
        auth.set_access_token(
            settings.TWITTER_CREDENTIALS["access_token"],
            settings.TWITTER_CREDENTIALS["access_secret"],
        )
        api = tweepy.API(auth)
        following = api.friends_ids()
        following.append(945391013828313088)
        self.stdout.write("Connected to Twitter.")

        self.stdout.write(self.style.SUCCESS("Launching stream...!"))
        stream = tweepy.Stream(auth=auth, listener=ArchiveStreamListener())
        stream.filter(follow=[str(id) for id in following])
        self.stdout.write("Exited!")


class ArchiveStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.id not in following:
            return
        try:
            user = None
            try:
                user = User.objects.get(user_id=status.user.id)
            except User.DoesNotExist:
                return

            # Update # of tweets field
            user.full_data["statuses_count"] = status.user.statuses_count
            user.save()

            # Archive tweet
            id = status.id
            tweet = Tweet(tweet_id=id, full_data=status._json, user=user)
            tweet.save()

            # Update user metadata
            tweet.update_user_metadata()

            print(
                "Archived tweet from from @%s (%s)."
                % (status.user.screen_name, status.user.id)
            )
        except Exception as e:
            print("Error on %s: %s" % (str(status.id), str(e)))
            sys.exit(1)

    def on_delete(self, status_id, user_id):
        try:
            tweet = Tweet.objects.get(tweet_id=status_id)
            tweet.deleted = True
            tweet.save()
            print("Got deleted tweet from #%s." % (user_id))
        except Exception as e:
            print("Error on %s: %s" % (str(status_id), str(e)))
