from django.contrib import admin
from . import models

admin.register(models.Tweet, models.User)