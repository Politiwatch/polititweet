from django.db import models
from django.contrib.postgres.fields import JSONField

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)

class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)
    first_received_date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)