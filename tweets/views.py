from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
import tweepy as tw
import numpy as np
from MethodUtils import MethodUtils
from tweets.models import TweetModel

class LoginView(MethodUtils,View):
    def get(self,request):
        try:
            redirect_url = self.authentication(request)
            context = {
                'redirect_url': redirect_url
            }
            return render(request,'tweets/login.html',context=context)

        except tw.TweepError:
            print 'Error!'
        # auth.set_access_token('299655885-Bd42kEf0GEVFbqauX2fz1YOM7iY2WYYMXyfe2wgl',
        #                       'SKVFFbtGoLnYelTtedl5khWWPEsGQnDr081gQr0ZPF7yj')

    def post(self,request):
        if request.method == 'POST':
            verifier = request.POST.get('verifier')
            access_token = self.verify(verify=verifier,request=request)
            request.session['access_token'] = access_token
            return redirect('/')


class MainTweet(MethodUtils,View):
    def get(self,request):
        token = request.session.get('access_token')
        if not token:
            return redirect('login')
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        access_token = request.session.get('access_token')
        self.auth.set_access_token(access_token[0],access_token[1])
        self.api = tw.API(self.auth)
        new_tweets = self.api.home_timeline(count = 100)
        # tweets = self.api.home_timeline(count=100,page=1)
        tweets = TweetModel.objects.all()
        if len(tweets) == 0:
            aux_tweet = self.get_tweets(new_tweets)
            tweets = aux_tweet
        tweets = self.tweet_formatter_training(tweets)
        recommender = self.training(tweets)
        tweets_format = self.tweet_formatter(new_tweets)
        tweets_recommends = self.recommend_tweets(recommender=recommender,tweets_parameter=tweets_format,tweets=new_tweets)
        tweets_format = self.from_tweet_template_to_model(tweets_recommends)

        context = {
            'tweets':tweets_format
        }
        return render(request=request,template_name='tweets/tweet_template.html',context=context)

class NewTweets(MethodUtils,View):
    def get(self,request):
        token = request.session.get('access_token')
        if not token:
            return redirect('login')
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        access_token = request.session.get('access_token')
        self.auth.set_access_token(access_token[0], access_token[1])
        self.api = tw.API(self.auth)
        new_tweets = self.api.home_timeline(count=100)
        tweets_format = self.from_tweet_template_to_model(new_tweets)
        context = {
            'tweets': tweets_format
        }
        return render(request=request, template_name='tweets/tweet_template.html', context=context)
