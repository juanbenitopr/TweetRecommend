from datetime import datetime
import time

import numpy as np
import tweepy as tw
from django.shortcuts import redirect
from sklearn import svm
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm.classes import SVC

from tweets.models import TweetModel, Autores, Categorias


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

    def __init__(self, autor_name, autor_lang, autor_id, autor_created_at, autor_favourites_count,
                 autor_followers_count, autor_friends_count, text, created_at, media, type_media, url_media, url, id,
                 n_rt, n_fav):
        self.created_at = created_at
        self.autor_name = autor_name
        self.autor_id = autor_id
        self.autor_favourites_count = autor_favourites_count
        self.autor_followers_count = autor_followers_count
        self.autor_friends_count = autor_friends_count
        self.autor_created_at = autor_created_at
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
    autor_aux = Autores.objects.filter(id_autor=author.id)
    autor = autor_aux[0] if len(autor_aux) == 1 else Autores.objects.create(id_autor=author.id, name=author.name,
                                                                            lang=author.lang,
                                                                            friends_count=author.friends_count,
                                                                            followers_count=author.followers_count,
                                                                            favorites_count=author.favourites_count)
    if 'media' in tweet.entities:
        media_ = tweet.entities.get('media')[0]
        TweetModel.objects.create(created_at_object=tweet.created_at, text=tweet.text, autor=autor, tweet_id=tweet.id,
                                  retweeted=False, retweets=tweet.retweet_count, favorite=False,
                                  favorites=tweet.favorite_count, media=True, url=None)
        tweet_object = TweetObject(author.name, author.lang, author.id, author.created_at, author.favourites_count,
                                   author.followers_count, author.friends_count, tweet.text, tweet.created_at, True,
                                   str(media_.get('type')),
                                   str(media_.get('media_url')), '', tweet.id, tweet.retweet_count,
                                   tweet.favorite_count)
    else:
        TweetModel.objects.create(created_at_object=tweet.created_at, text=tweet.text, autor=autor, tweet_id=tweet.id,
                                  retweeted=False, retweets=tweet.retweet_count, favorite=False,
                                  favorites=tweet.favorite_count, media=False, url=None)
        tweet_object = TweetObject(author.name, author.lang, author.id, author.created_at, author.favourites_count,
                                   author.followers_count, author.friends_count, tweet.text, tweet.created_at, False,
                                   '', '', '', tweet.id, tweet.retweet_count, tweet.favorite_count)
    return tweet_object

def build_from_tweepy_without_save(tweet):
    author = tweet.author
    if 'media' in tweet.entities:
        media_ = tweet.entities.get('media')[0]
        tweet_object = TweetObject(author.name, author.lang, author.id, author.created_at, author.favourites_count,
                                   author.followers_count, author.friends_count, tweet.text, tweet.created_at, True,
                                   str(media_.get('type')),
                                   str(media_.get('media_url')), '', tweet.id, tweet.retweet_count,
                                   tweet.favorite_count)
    else:
        tweet_object = TweetObject(author.name, author.lang, author.id, author.created_at, author.favourites_count,
                                   author.followers_count, author.friends_count, tweet.text, tweet.created_at, False,
                                   '', '', '', tweet.id, tweet.retweet_count, tweet.favorite_count)
    return tweet_object

def from_tweet_template_to_model(list_tweets):
    aux_list_tweets = []
    for tweet in list_tweets:
        if tweet.author.lang == 'en': continue
        t_model = TweetModel.objects.filter(tweet_id=tweet.id).count()
        if t_model == 0:
            tweepy = built_from_tweepy(tweet)
            aux_list_tweets.append(tweepy)
        else:
            continue
    return aux_list_tweets


class MethodUtils(object):

    def authentication(self, request):

        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        try:
            redirect_url = self.auth.get_authorization_url()
            request.session['request_token'] = self.auth.request_token
            return redirect_url

        except tw.TweepError:
            print 'Error!'
            # auth.set_access_token('299655885-Bd42kEf0GEVFbqauX2fz1YOM7iY2WYYMXyfe2wgl',
            #                       'SKVFFbtGoLnYelTtedl5khWWPEsGQnDr081gQr0ZPF7yj')

    def verify(self, verify, request):
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        self.auth.request_token = request.session.get('request_token')
        try:
            access_token = self.auth.get_access_token(verify)
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

    def recommend_tweets(self, recommender, tweets_parameter, tweets):
        predicted_vector = recommender.predict(tweets_parameter)
        categorias  = Categorias.objects.all().order_by('pk')
        tweets_classified = [{'tweet':build_from_tweepy_without_save(tweet),'categorias':[]} for tweet in tweets]
        index_categories = np.where(predicted_vector == 1)
        for label in xrange(len(index_categories[0])):
            aux = tweets_classified[index_categories[0][label]]['categorias']
            label_ = index_categories[1][label]
            categorias_ = categorias[int(label_)]
            aux.append(categorias_)
        return  tweets_classified


    def tweet_formatter_training(self, tweets):
        roi_prepare = []
        for i in tweets:
            roi_prepare.append([i.author_id, i.retweets, i.retweeted])
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


    def training_tweets_categories(self):
        self.autores = [a.id_autor for a in Autores.objects.all().order_by('pk')]
        tweets = TweetModel.objects.exclude(categoria = None)
        tweet_features = np.zeros((len(tweets), len(self.autores) + 3 + 1 ))
        categorias = Categorias.objects.all()
        tweet_label = np.zeros((len(tweets), len(categorias)))
        count = 0
        for t in tweets.select_related('autor'):
            features, label = self.tweet_model_to_predict_vector(t)
            tweet_features[count, :] = features
            tweet_label[count, :] = label
            count+=1
        clasif = OneVsRestClassifier(SVC(kernel='linear',C=100))
        scores = cross_val_score(clasif,tweet_features,tweet_label,cv=5)
        accuracy = {'mean':scores.mean(),'std':scores.std()*2}
        clasif.fit(tweet_features, tweet_label)
        return clasif,accuracy

    def training_tweets_categories_text_minig(self):
        pipeline = Pipeline([

        ])

# Este metodo se puede refactorizar para que sea mas limpio, en lugar de concatenando al final creandolo de primeras con todas las posiciones en 0 e ir
# anadiendo lo necesario
    def tweet_model_to_predict_vector(self, tweet_model):
        autores = np.zeros(len(self.autores))
        autores[self.autores.index(tweet_model.autor.id_autor)] = 1
        rt_vector = np.zeros(3)
        rt_vector[
            0 if tweet_model.retweets < 20 else 1 if tweet_model.retweets < 50 else 2] = 1
        media = np.array([1 if tweet_model.media else 0])
        features_vector = np.concatenate((autores, rt_vector, media), axis=0)
        label = np.array([ 1 if categ in tweet_model.categoria.all() else 0for categ in Categorias.objects.all().order_by('pk')])
        return features_vector, label


    def new_tweet_model_to_classifier(self, tweet_model):
        autores = np.zeros(len(self.autores))
        autores[self.autores.index(tweet_model.author.id)] = 1
        rt_vector = np.zeros(3)
        retweets = tweet_model.retweet_count
        rt_vector[
            0 if retweets < 20 else 1 if retweets < 50 else 2] = 1
        media = np.array([1 if 'media' in tweet_model.entities else 0])
        # date = np.array([time.mktime(tweet_model.created_at.timetuple())])
        features_vector = np.concatenate((autores, rt_vector, media), axis=0)
        return features_vector


    def tweet_formatter(self, tweets):
        for t in tweets:
            if Autores.objects.filter(id_autor = t.author.id).count()==0:
                Autores.objects.create(id_autor = t.author.id,name=t.author.name,lang = t.author.lang,friends_count = t.author.friends_count,followers_count = t.author.friends_count,favorites_count = t.author.favourites_count)
        self.autores = [a.id_autor for a in Autores.objects.all().order_by('pk')]
        tweet_features = np.zeros((len(tweets), len(self.autores) + 3 + 1))
        count = 0
        for t in tweets:
            features = self.new_tweet_model_to_classifier(t)
            tweet_features[count, :] = features
            count +=1
        return tweet_features

    def text_mining(self,text):
        pass
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
