from django.db import models

class Visit(models.Model):
    ip = models.GenericIPAddressField()
    time = models.DateTimeField(auto_now_add=True)
    url = models.TextField()