from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField
from .util import first_or_none, similarity

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True, db_index=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    added_date = models.DateTimeField(auto_now_add=True, db_index=True)
    deleted_count = models.BigIntegerField(default=0, db_index=True) # big integer, b/c you never know
    flagged = models.BooleanField(default=False)
    monitored = models.BooleanField(default=True)

class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True, db_index=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    hibernated = models.BooleanField(default=False)
    full_text = models.CharField(default=None, blank=True, null=True, max_length=400, db_index=True)

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
        return first_or_none(Tweet.objects.filter(
        user=self.user, tweet_id__gt=self.tweet_id).order_by("tweet_id"))

    @property
    def preceding(self):
        return first_or_none(Tweet.objects.filter(
        user=self.user, tweet_id__lt=self.tweet_id).order_by("-tweet_id"))

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

    def day(self):
        return datetime.strptime(self.full_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y').date()