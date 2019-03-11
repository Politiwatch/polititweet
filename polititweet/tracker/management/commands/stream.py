import tweepy

from django.core.management.base import BaseCommand, CommandError
from ...models import Tweet, User
from django.conf import settings

following = []

class Command(BaseCommand):
    help = 'Stream new tweets from monitored users into the database'

    def handle(self, *args, **options):
        global following
        self.stdout.write("Loading accounts to track...")
        users = User.objects.all()
        self.stdout.write("Loaded %s accounts to track." % str(len(users)))

        self.stdout.write("Connecting to Twitter...")
        auth = tweepy.OAuthHandler(settings.TWITTER_CREDENTIALS["consumer_key"], settings.TWITTER_CREDENTIALS["consumer_secret"])
        auth.set_access_token(settings.TWITTER_CREDENTIALS["access_token"], settings.TWITTER_CREDENTIALS["access_secret"])
        api = tweepy.API(auth)
        following = api.friends_ids()
        following.append(945391013828313088)
        self.stdout.write("Connected to Twitter.")

        self.stdout.write(self.style.SUCCESS("Launching stream...!"))
        stream = tweepy.Stream(auth = auth, listener=ArchiveStreamListener())
        # stream.filter(follow=[str(user.user_id) for user in users])
        stream.filter(follow=[str(id) for id in following])
        self.stdout.write("Exited!")

class ArchiveStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.id not in following:
            return
        try:
            user = User.objects.get(user_id=status.user.id)

            # Check for potential deleted tweet
            if user.full_data["statuses_count"] >= status.user.statuses_count:
                print("@%s likely deleted a tweet; flagging..." % status.user.screen_name)
                user.flagged = True
                user.save()

            # Update # of tweets field
            user.full_data["statuses_count"] = status.user.statuses_count
            user.save()

            # Archive tweet
            id = status.id
            tweet = Tweet(tweet_id=id, full_data=status._json, user=user)
            tweet.save()
            print("Archived tweet from from @%s (%s)." % (status.user.screen_name, status.user.id))
        except Exception as e:
            print("Error on %s: %s" % (str(status.id), str(e)))