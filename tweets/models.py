from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db.models.base import Model
from django.db.models.fields import CharField, IntegerField, NullBooleanField, DateTimeField
from django.db.models.fields.related import ForeignKey

class Person_interest(Model):
    id_person = IntegerField()
    name = CharField(max_length=150)
    position_list = IntegerField()
    def __unicode__(self):
        return self.name

class Autores(Model):
    id_autor = IntegerField()
    name = CharField(max_length=150)
    lang = CharField(max_length=10,default='es')
    friends_count = IntegerField()
    followers_count = IntegerField()
    favourites_count = IntegerField()
    position_list = IntegerField()
    def __unicode__(self):
        return self.name

class Categorias(Model):
    name = CharField(max_length=150)
    def __unicode__(self):
        return self.name

class TweetModel (Model):
    created_at = DateTimeField(auto_now_add=True,auto_created=True)
    created_at_object = DateTimeField()
    text = models.CharField(max_length=150)
    author = ForeignKey(Autores)
    tweet_id = models.IntegerField()
    retweeted = models.BooleanField()
    retweets = models.IntegerField()
    favorite = models.NullBooleanField()
    favorites = models.IntegerField(null=True)
    categoria = ForeignKey(Categorias,null=True)
    media = NullBooleanField()
    url = NullBooleanField()