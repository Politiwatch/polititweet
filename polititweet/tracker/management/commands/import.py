import json
import os
from django.core.management.base import BaseCommand, CommandError
from ...models import Tweet, User
from django.conf import settings

class Command(BaseCommand):
    help = 'Import tweets from a legacy PolitiTweet database'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    def handle(self, *args, **options):
        directory = options["directory"]
        self.stdout.write("Importing from `%s`..." % directory)
        total_imported = 0
        for root, dirs, files in os.walk(directory):
            skip = False
            if root.endswith("tweets"):
                user = None
                user_imported = 0
                user_deleted = 0
                to_batch_insert = []
                existing_ids = []
                for filename in files:
                    if skip:
                        break
                    if filename.endswith(".json"):
                        with open(os.path.join(root, filename), "r") as infile:
                            data = json.load(infile)
                            data["legacy_imported"] = True
                            deleted = False
                            if "deleted" in data and data["deleted"]:
                                deleted = True
                                user_deleted += 1
                            if user == None or user.user_id != data["user"]["id"]:
                                try:
                                    user = User.objects.get(user_id=data["user"]["id"])
                                    existing_ids = [tweet.tweet_id for tweet in Tweet.objects.filter(user=user)]
                                except User.DoesNotExist:
                                    self.stderr.write("Unable to find user %s in database... skipping..." % data["user"]["id"])
                                    skip = True
                                    continue
                            tweet = Tweet(tweet_id=data["id"], full_data=data, user=user, deleted=deleted)
                            tweet.full_text = tweet.text()[:300]
                            if tweet.tweet_id not in existing_ids:
                                to_batch_insert.append(tweet)
                                total_imported += 1
                                user_imported += 1
                if not skip and user != None:
                    Tweet.objects.bulk_create(to_batch_insert)
                    user.deleted_count = Tweet.objects.filter(user=user, deleted=True).count()
                    user.save()
                    self.stdout.write(self.style.SUCCESS("Successfully imported %s tweets from @%s, of which %s were deleted." % (str(user_imported), user.full_data["screen_name"], str(user_deleted))))
        self.stdout.write(self.style.SUCCESS("Successfully imported %s tweets!" % str(total_imported)))
