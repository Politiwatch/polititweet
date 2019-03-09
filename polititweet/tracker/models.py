from django.db import models
from django.contrib.postgres.fields import JSONField

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(default=1)
    flagged = models.BooleanField(default=False)

class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)