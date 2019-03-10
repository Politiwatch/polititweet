from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)
    added_date = models.DateTimeField(auto_now_add=True)
    deleted_count = models.BigIntegerField(default=0) # big integer, b/c you never know
    flagged = models.BooleanField(default=False)

class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    hibernated = models.BooleanField(default=False)

    def text(self):
        if "extended_tweet" in self.full_data:
            return self.full_data["extended_tweet"]["full_text"]
        else:
            return self.full_data["text"]

    def day(self):
        return datetime.strptime(self.full_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y').date()