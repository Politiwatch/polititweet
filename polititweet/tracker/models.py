from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True, db_index=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    added_date = models.DateTimeField(auto_now_add=True, db_index=True)
    deleted_count = models.BigIntegerField(default=0, db_index=True) # big integer, b/c you never know
    flagged = models.BooleanField(default=False)

class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True, db_index=True)
    full_data = JSONField()
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    hibernated = models.BooleanField(default=False)
    full_text = models.CharField(default=None, blank=True, null=True, max_length=300, db_index=True)

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

    def day(self):
        return datetime.strptime(self.full_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y').date()