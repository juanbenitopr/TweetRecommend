from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db.models.base import Model


class TweetModel (Model):
    text = models.CharField(max_length=150)
    author_id = models.IntegerField()
    author = models.CharField(max_length=150)
    tweet_id = models.IntegerField()
    retweeted = models.BooleanField()
    retweets = models.IntegerField()
    favorite = models.NullBooleanField()
    favorites = models.IntegerField(null=True)