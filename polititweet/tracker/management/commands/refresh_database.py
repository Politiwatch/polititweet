from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand
from ...models import Tweet, User


class Command(BaseCommand):
    help = "Updates search indices and metadata"

    def handle(self, *args, **options):
        self.stdout.write("Loading accounts to update...")
        users = list(
            User.objects.all()
        )  # Do actually load everything from the database
        self.stdout.write("Loaded %s accounts to update." % str(len(users)))

        for i, user in enumerate(users):
            self.stdout.write(f"Updating metadata for user #{user.user_id}...")
            latest_tweet = user.latest_tweet()
            if latest_tweet is None:
                continue
            latest_tweet.update_user_metadata()

            user.refresh_from_db()
            self.stdout.write(
                "...updated metadata for "
                + self.style.SUCCESS("@" + user.full_data["screen_name"])
                + f" (#{i + 1}/{len(users)})"
            )

        self.stdout.write(self.style.SUCCESS("Update complete!"))
