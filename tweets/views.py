# -*- coding: utf8 -*-
from nltk.stem.snowball import SnowballStemmer
from pandas import json

from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
import tweepy as tw
import numpy as np
from MethodUtils import MethodUtils
from tweets.MethodUtils import from_tweet_template_to_model
from tweets.models import TweetModel, Categorias, TextWord

#Vista de login para twitter esta vista la he implementado porque tenía como objetivo que fuese multiusuario aunque lo fui desechando poco a poco
from tweets.text_mining import save_special_word, get_non_words


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

#Vista para taggear tweets en las diferentes categorías
#El get muestra los tweets con las categorías
#El post guarda los tweets taggeados
class TrainningTweets(MethodUtils,View):
    def get(self,request):
        token = request.session.get('access_token')
        if not token:
            return redirect('login')
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        self.auth.set_access_token(token[0], token[1])
        self.api = tw.API(self.auth)
        new_tweets = self.api.home_timeline(count=20)
        tweets_format = from_tweet_template_to_model(new_tweets)
        categorias = Categorias.objects.all()
        context = {
            'tweets': tweets_format,
            'categorias':categorias
        }
        return render(request=request, template_name='tweets/tweet_template.html', context=context)

    def post(self,request):
        data_send = str(request.POST.get('data_send'))
        json_data = json.loads(data_send)
        non_words = get_non_words()
        snow_stem = SnowballStemmer('spanish')
        for data in json_data:
            tweet = TweetModel.objects.get(tweet_id=data.get('tweet_id'))
            if 'retweeted' in data:
                tweet.retweeted = data.get('retweeted')
                tweet.save()
            elif 'category_id' in data :
                tweet.categoria.add(Categorias.objects.get(pk = data.get('category_id')))
                tweet.save()
        for data in json_data:
            tweet = TweetModel.objects.get(tweet_id=data.get('tweet_id'))
            save_special_word(non_words, snow=snow_stem, tweet=tweet)
        return HttpResponse('Conseguido')

#Muestra los tweets clasificados en cada categoría con la precisión que nos da este clasificador
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
        tweets_format = self.tweet_formatter(new_tweets)
        recommender,accuracy = self.training_tweets_categories()
        tweets_recommends = self.recommend_tweets(recommender=recommender,tweets_parameter=tweets_format,tweets=new_tweets)
        context = {
            'tweets':tweets_recommends,
            'accuracy':accuracy
        }
        return render(request=request,template_name='tweets/tweet_classifier.html',context=context)

#Muestra lo mismo que la anterior pero utilizando técnicas de text-mining, en estructura es básicamente igual que la anterior
class TextMining(MethodUtils,View):
    def get(self, request):
        token = request.session.get('access_token')
        if not token:
            return redirect('login')
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        access_token = request.session.get('access_token')
        self.auth.set_access_token(access_token[0], access_token[1])
        self.api = tw.API(self.auth)
        new_tweets = self.api.home_timeline(count=100)
        tweets_format = self.tweet_formatter_text_mining(new_tweets)
        recommender, accuracy = self.training_tweets_categories_text_mining()
        tweets_recommends = self.recommend_tweets_text_mining(recommender=recommender, tweets_parameter=tweets_format,
                                                  tweets=new_tweets)
        context = {
            'tweets': tweets_recommends,
            'accuracy': accuracy
        }
        return render(request=request, template_name='tweets/tweet_classifier.html', context=context)

class SuperTextMining(MethodUtils,View):
    def get(self,request):
        token = request.session.get('access_token')
        if not token:
            return redirect('login')
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        access_token = request.session.get('access_token')
        self.auth.set_access_token(access_token[0], access_token[1])
        self.api = tw.API(self.auth)
        new_tweets = self.api.home_timeline(count=100)
        tweets_format = self.tweet_formatter_super_text(new_tweets)
        recommender, accuracy = self.training_tweets_categories_super_text()
        tweets_recommends = self.recommend_tweets_super_text(recommender=recommender, tweets_parameter=tweets_format,
                                                  tweets=new_tweets)
        context = {
            'tweets': tweets_recommends,
            'accuracy': accuracy
        }
        return render(request=request, template_name='tweets/tweet_classifier.html', context=context)

class MetricsView(MethodUtils,View):
    def get(self,request):
        accuracy = self.get_best_metrics()
        context = {
            'accuracy': accuracy

        }
        return render(request=request, template_name='tweets/tweet_metrics.html', context=context)