from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import View
import tweepy as tw
import numpy as np
from MethodUtils import MethodUtils
from tweets.models import TweetModel


class MainTweet(MethodUtils,View):
    def get(self,request):
        self.authentication()
        new_tweets = self.api.home_timeline(count = 50)
        tweets = TweetModel.objects.all()
        if len(tweets) == 0:
            aux_tweet = self.get_tweets(new_tweets)
            tweets = aux_tweet
        recommender = self.training(tweets)
        tweets_format = self.tweet_formatter(new_tweets)
        tweets_recommends = self.recommend_tweets(recommender=recommender,tweets_parameter=tweets_format,tweets=new_tweets)
        context = {
            'tweets':tweets_recommends
        }
        return render(request=request,template_name='tweets/tweet_template.html',context=context)
