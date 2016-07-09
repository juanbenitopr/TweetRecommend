from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import ModelAdmin

from tweets.models import TweetModel, Categorias, Autores, Person_interest


class TweetAdmin(ModelAdmin):
    list_display = ('author','retweeted','retweets')
admin.site.register(TweetModel,TweetAdmin)
admin.site.register(Categorias)
admin.site.register(Autores)
admin.site.register(Person_interest)