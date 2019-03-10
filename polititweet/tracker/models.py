from django.db import models
from django.contrib.postgres.fields import JSONField

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(default=1)
    flagged = models.BooleanField(default=False)

    def deleted_tweets(self):
        return Tweet.objects.filter(user=self, deleted=True)

class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    hibernated = models.BooleanField(default=False)