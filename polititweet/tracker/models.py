from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.core.cache import cache
from .util import first_or_none, similarity
import pytz


class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True, db_index=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    added_date = models.DateTimeField(auto_now_add=True, db_index=True)
    deleted_count = models.BigIntegerField(
        default=0, db_index=True
    )  # big integer, b/c you never know
    flagged = models.BooleanField(default=False)
    monitored = models.BooleanField(default=True)


class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True, db_index=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    hibernated = models.BooleanField(default=False)
    full_text = models.CharField(
        default=None, blank=True, null=True, max_length=400, db_index=True
    )

    class Meta:
        indexes = [models.Index(fields=["user", "deleted", "-modified_date"])]

    @classmethod
    def get_current_top_deleted_tweet(cls, since=30, use_cache=True):
        if use_cache:
            tweet = cache.get("top_deleted_tweet")
            if tweet != None:
                return tweet
        tweets = sorted(
            filter(
                lambda k: not (k.full_text.startswith("RT @") or k.datetime() < timezone.now() - timezone.timedelta(days=1)),
                cls.objects.filter(
                    deleted=True,
                    hibernated=False,
                    modified_date__gt=timezone.now() - timezone.timedelta(minutes=since),
                ),
            ),
            key=lambda k: k.full_data["user"]["followers_count"],
            reverse=True,
        )
        tweet = None
        for i in range(len(tweets)):
            if tweets[i].likely_typo:
                continue
            tweet = tweets[i]
            break
        if tweet is None:
            tweet = (
                cls.objects.filter(deleted=True)
                .exclude(full_text__startswith="RT @")
                .order_by("-modified_date")
                .first()
            )
        cache.set("top_deleted_tweet", tweet, timeout=30*60)
        return tweet

    def save(self, *args, **kwargs):
        if self.full_text == None:
            self.full_text = self.text()
        super(Tweet, self).save(*args, **kwargs)

    def text(self):
        if self.full_text != None:
            return self.full_text
        if "extended_tweet" in self.full_data:
            return self.full_data["extended_tweet"]["full_text"]
        else:
            return self.full_data["text"]

    @property
    def following(self):
        return first_or_none(
            Tweet.objects.filter(user=self.user, tweet_id__gt=self.tweet_id).order_by(
                "tweet_id"
            )
        )

    @property
    def preceding(self):
        return first_or_none(
            Tweet.objects.filter(user=self.user, tweet_id__lt=self.tweet_id).order_by(
                "-tweet_id"
            )
        )

    @property
    def likely_typo(self):
        following = self.following
        if following == None:
            return False
        following_text = following.text()
        result = similarity(self.text(), following_text) > 0.85
        return result

    @property
    def is_retweet(self):
        return "retweeted_status" in self.full_data

    def datetime(self):
        return datetime.strptime(
            self.full_data["created_at"], "%a %b %d %H:%M:%S %z %Y"
        )

    def day(self):
        return self.datetime().date()

