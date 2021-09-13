from django.core.management.base import BaseCommand
from ...models import Tweet, User


class Command(BaseCommand):
    help = "Updates search indices and metadata"

    def handle(self, *args, **options):
        self.stdout.write("Updating Tweet search indices...")
        Tweet.update_search_index()
        self.stdout.write(self.style.SUCCESS("Search index update complete!"))

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
