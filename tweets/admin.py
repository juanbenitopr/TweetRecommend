from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import ModelAdmin

from tweets.models import TweetModel

class TweetAdmin(ModelAdmin):
    list_display = ('author','retweeted','retweets')
admin.site.register(TweetModel,TweetAdmin)