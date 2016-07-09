from datetime import datetime

import numpy as np
import tweepy as tw
from django.shortcuts import redirect
from sklearn import svm
from tweets.models import TweetModel, Autores

class TweetObject(object):
    autor_created_at = datetime.now()
    autor_name = ''
    autor_id = 0
    autor_favourites_count = 0
    autor_followers_count = 0
    autor_friends_count = 0
    autor_lang = ''
    created_at = datetime.now()
    text = 0
    media = False
    type_media = ''
    url_media = ''
    url = ''
    tweet_id = 0
    n_rt = 0
    n_fav = 0

    def __init__(self,autor_name,autor_lang,autor_id,autor_created_at,autor_favourites_count,autor_followers_count,autor_friends_count,text,created_at,media,type_media,url_media,url,id,n_rt,n_fav):
        self.created_at = created_at
        self.autor_name = autor_name
        self.autor_id = autor_id
        self.autor_favourites_count = autor_favourites_count
        self.autor_followers_count = autor_followers_count
        self.autor_friends_count = autor_friends_count
        self.autor_created_at  = autor_created_at
        self.autor_lang = autor_lang
        self.text = text
        self.media = media
        if media:
            self.type_media = type_media
            self.url_media = url_media
        self.url = url
        self.tweet_id = id
        self.n_rt = n_rt
        self.n_fav = n_fav


def built_from_tweepy(tweet):
    author = tweet.author
    if 'media' in tweet.entities:
        media_ = tweet.entities.get('media')[0]
        tweet_object = TweetObject(author.name, author.lang, author.id, author.created_at, author.favourites_count,
                                   author.followers_count, author.friends_count, tweet.text, tweet.created_at, True, str(media_.get('type')),
                                   str(media_.get('media_url')),'',tweet.id,tweet.retweet_count,tweet.favorite_count)
    else:
        tweet_object = TweetObject(author.name, author.lang, author.id, author.created_at, author.favourites_count,
                                   author.followers_count, author.friends_count, tweet.text, tweet.created_at, False,
                                  '','', '', tweet.id, tweet.retweet_count,tweet.favorite_count)
    return tweet_object


def from_tweet_template_to_model(list_tweets):
    aux_list_tweets = np.array([built_from_tweepy(tweet) for tweet in list_tweets])
    return aux_list_tweets


class MethodUtils(object):
    def sort_list_by_second_parameter(self, trust_list, trust_sort):
        count = 1
        for i in trust_list:
            cand = i
            for x in trust_list[count:]:
                if cand[1] < x[1]:
                    cand = x
            aux = i
            index_value = trust_list.index(i)
            index_cand = trust_list.index(cand)

            trust_list[index_value] = cand
            trust_list[index_cand] = aux
            count = count + 1
        for i in trust_list[:5]:
            trust_sort.append(i[0])
        return trust_list

    def authentication(self,request):

        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        try:
            redirect_url = self.auth.get_authorization_url()
            request.session['request_token'] = self.auth.request_token
            return redirect_url

        except tw.TweepError:
            print 'Error!'
        # auth.set_access_token('299655885-Bd42kEf0GEVFbqauX2fz1YOM7iY2WYYMXyfe2wgl',
        #                       'SKVFFbtGoLnYelTtedl5khWWPEsGQnDr081gQr0ZPF7yj')

    def verify (self,verify,request):
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        self.auth.request_token = request.session.get('request_token')
        try:
           access_token=self.auth.get_access_token(verify)
           return access_token
        except tw.TweepError:
            print 'Error! Failed to get access token.'

    def get_tweets(self, new_tweets):
        training_vector = []
        for i in range(3):
            if i > 0:
                training_vector.append(self.api.home_timeline(page=i + 1, count=100))
            else:
                training_vector.append(self.api.home_timeline(max_id=new_tweets.since_id, count=100))
        training_vector = self.from_tweet_api_to_model(training_vector)
        return training_vector

    def training(self, list_tweets):
        rt_vector = []
        tweet_vector = []
        trust_list = []
        self.trust_sort = []
        flag = True
        for i in list_tweets:
            for x in trust_list:
                if i[0] == x[0]:
                    x[1] += 1
                    flag = False
            if flag:
                trust_list.append([i[0], 1])
            flag = True
        self.sort_list_by_second_parameter(trust_list, self.trust_sort)
        for i in list_tweets:
            if i[2]:
                rt_vector.append(1)
                tweet_vector.append([i[0], i[1]])
            else:
                rt_vector.append(-1)
            # if i[0] in self.trust_sort:
            #     tweet_vector.append([i[0], i[1]])
            # else:
            #     tweet_vector.append([i[0], i[1]])
        tweet_vector = np.array(tweet_vector)
        rt_vector = np.array(rt_vector)
        clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1,tol=0.1)
        clf.fit(tweet_vector)

        return clf

    def recommend_tweets(self, recommender, tweets_parameter, tweets):

        tweet_show = []
        count = 0
        for i in tweets_parameter:
            predicted_vector = recommender.predict(i.reshape(1,-1))
            count += 1
            if predicted_vector == 1:
                index = np.where(tweets_parameter == i)
                tweet_show.append(tweets[count])

        return tweet_show

    def tweet_formatter(self, tweets):
        roi_prepare = []
        for i in tweets:
            roi_prepare.append([i.author.id, i.retweet_count])
        roi_prepare_aux = np.array(roi_prepare)
        return roi_prepare_aux

    def tweet_formatter_training(self, tweets):
        roi_prepare = []
        for i in tweets:
            roi_prepare.append([i.author_id, i.retweets,i.retweeted])
        roi_prepare_aux = np.array(roi_prepare)
        return roi_prepare_aux

    def from_tweet_api_to_model(self, list_tweets):
        aux_list_tweets = []
        for tweets in list_tweets:
            for tweet in tweets:
                tweet_model = TweetModel.objects.create(text=tweet.text, author_id=tweet.author.id,
                                                        author=tweet.author.name, tweet_id=tweet.id,
                                                        retweeted=tweet.retweeted, retweets=tweet.retweet_count,
                                                        favorite=tweet.favorited, favorites=tweet.favorite_count)
                aux_list_tweets.append(tweet_model)
        return aux_list_tweets


    def get_new_tweets(self):
        return self.api.home_timeline()

        # def get_roi(self):

        # count = 0
        # rt_count = 0
        # tweet_show = []
        # predicted_vector = clf.predict(roi_prepare)
        # for i in predicted_vector:
        #     if i==1:
        #         tweet_show.append(roi_vector[predicted_vector.index(i)])
        #     ind = np.where(predicted_vector == i)
        #     tweet =  roi_vector[ind]
        #     if i == 1 and tweet.retweeted == 1:
        #         count += 1
        #     if i.retweeted == 1:
        #         rt_count += 1
        # roi = count * 100 / rt_count



        #     ind = np.where(predicted_vector == i)
        #     tweet =  tweets[ind]
        #     if i == 1 and tweet.retweeted == 1:
        #         count += 1
        #     if i.retweeted == 1:
        #         rt_count += 1
        # roi = count * 100 / rt_count
