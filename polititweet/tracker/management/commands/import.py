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
                            if user == None:
                                try:
                                    user = User.objects.get(user_id=data["user"]["id"])
                                except User.DoesNotExist:
                                    self.stderr.write("Unable to find user %s in database... skipping...")
                                    skip = True
                                    continue
                            try:
                                tweet = Tweet(tweet_id=data["id"], full_data=data, user=user, deleted=deleted)
                                tweet.save()
                                total_imported += 1
                                user_imported += 1
                            except Exception as e:
                                self.stderr.write("Unable to write tweet at %s: %s" % (os.path.join(root, filename), str(e)))
                self.stdout.write(self.style.SUCCESS("Successfully imported %s tweets from @%s." % (str(user_imported), user.full_data["screen_name"])))
        self.stdout.write(self.style.SUCCESS("Successfully imported %s tweets!" % str(total_imported)))
