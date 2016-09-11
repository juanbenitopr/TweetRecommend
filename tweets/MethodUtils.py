# -*- coding: utf8 -*-
from datetime import datetime
import time

import numpy as np
import tweepy as tw
from django.shortcuts import redirect
from sklearn import svm
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.grid_search import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm.classes import SVC

from tweets import text_mining
from tweets.models import TweetModel, Autores, Categorias, TextWord


# Este módulo tiene todos los métodos para sacar las features de los tweets, y clasificarlas
# La clase Tweet Object es una clase que agrupa todos los atributos que quiero mostrar en las vistas, en un solo objeto para que sea más fácil trabajar con él.
# además he hecho algunos métodos para guardar directamente este objeto en la base de datos

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

    # soy bastante nuevo utilizando objetos en python, mi experiencia anterior es con java así que no te asustes de este constructor
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


# este método es para pasar de un objeto status que te da tweepy a un TweetObject despues de haberlo guardado en la base de datos
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


# este método simplemente implementa un objeto TweetObject sin guardarlo previamente
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


# Comprueba que el tweet recuperado no existe previamente y que el tweet está en español
def from_tweet_template_to_model(list_tweets):
    aux_list_tweets = []
    for tweet in list_tweets:
        if tweet.lang == 'en': continue
        t_model = TweetModel.objects.filter(tweet_id=tweet.id).count()
        if t_model == 0:
            tweepy = built_from_tweepy(tweet)
            aux_list_tweets.append(tweepy)
        else:
            continue
    return aux_list_tweets


# Este objeto lo he implementado porque en principio proporciona todas las técnicas de autenticación,
class MethodUtils(object):
    # Métodos de autenticación para tweepy
    def authentication(self, request):

        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        try:
            redirect_url = self.auth.get_authorization_url()
            request.session['request_token'] = self.auth.request_token
            return redirect_url

        except tw.TweepError:
            print 'Error!'

    def verify(self, verify, request):
        self.auth = tw.OAuthHandler('BgTFskBMXHsPAIzmJ6GaAICPM', 'rH1nTBTAbd8JuVyjWdDdJ3wYxV38E3Zzjj3x1zmBQtRjxdqxJI')
        self.auth.request_token = request.session.get('request_token')
        try:
            access_token = self.auth.get_access_token(verify)
            return access_token
        except tw.TweepError:
            print 'Error! Failed to get access token.'

            # Fin de los métodos de autenticación
            #
            # Los siguientes métodos empece a incluirnos en el mismo objeto, aunque su misión no son la misma que los métodos anteriores
            # Más adelante irán a otro objeto con la función más definida, este objeto en principio tiene todos los métodos de utilidad variada

            # Estos métodos son para el entrenamiento descrito en el correo sin el uso e text-mining
            # Este método es para extraer las features de los nuevos tweets

    def tweet_formatter(self, tweets):
        for t in tweets:
            if Autores.objects.filter(id_autor=t.author.id).count() == 0:
                Autores.objects.create(id_autor=t.author.id, name=t.author.name, lang=t.author.lang,
                                       friends_count=t.author.friends_count, followers_count=t.author.friends_count,
                                       favorites_count=t.author.favourites_count)
        self.autores = [a.id_autor for a in Autores.objects.all().order_by('pk')]
        tweet_features = np.zeros((len(tweets), len(self.autores) + 3 + 1))
        count = 0
        for t in tweets:
            features = self.new_tweet_model_to_classifier(t)
            tweet_features[count, :] = features
            count += 1
        return tweet_features

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

    # Estos métodos son para extraer las features de los tweets de entrenamiento, y entrenar el clasificador
    def training_tweets_categories(self):
        self.autores = [a.id_autor for a in Autores.objects.all().order_by('pk')]
        tweets = TweetModel.objects.exclude(categoria=None)
        tweet_features = np.zeros((len(tweets), len(self.autores) + 3 + 1))
        categorias = Categorias.objects.all()
        tweet_label = np.zeros((len(tweets), len(categorias)))
        count = 0
        for t in tweets.select_related('autor'):
            features, label = self.tweet_model_to_predict_vector(t)
            tweet_features[count, :] = features
            tweet_label[count, :] = label
            count += 1
        clasif = OneVsRestClassifier(SVC(kernel='linear', C=200))
        scores = cross_val_score(clasif, tweet_features, tweet_label, cv=5, scoring='f1_weighted')
        accuracy = {'mean': scores.mean(), 'std': scores.std() * 2}
        clasif.fit(tweet_features, tweet_label)
        return clasif, accuracy

    # Este método concretamente es el que extrae las features de lo tweets ya guardados
    def tweet_model_to_predict_vector(self, tweet_model):
        autores = np.zeros(len(self.autores))
        autores[self.autores.index(tweet_model.autor.id_autor)] = 1
        rt_vector = np.zeros(3)
        rt_vector[
            0 if tweet_model.retweets < 20 else 1 if tweet_model.retweets < 50 else 2] = 1
        media = np.array([1 if tweet_model.media else 0])
        features_vector = np.concatenate((autores, rt_vector, media), axis=0)
        label = np.array(
            [1 if categ in tweet_model.categoria.all() else 0 for categ in Categorias.objects.all().order_by('pk')])
        return features_vector, label

    # Método para recomendar los nuevos tweets en función de sus features, este método se sirve del numpy.where para saber que tweets pertecenen a que categoría
    # de manera que las categorías puestas a 1 son las que se le asignan al tweet del índice al que pertenece
    def recommend_tweets(self, recommender, tweets_parameter, tweets):
        predicted_vector = recommender.predict(tweets_parameter)
        categorias = Categorias.objects.all().order_by('pk')
        tweets_classified = [{'tweet': build_from_tweepy_without_save(tweet), 'categorias': []} for tweet in tweets]
        index_categories = np.where(predicted_vector == 1)
        for label in xrange(len(index_categories[0])):
            aux = tweets_classified[index_categories[0][label]]['categorias']
            label_ = index_categories[1][label]
            categorias_ = categorias[int(label_)]
            aux.append(categorias_)
        return tweets_classified

    # Fin de la clasificación sin text-mining
    #
    # Empieza la clasificación con text-mining, estos métodos esencialmente hacen lo mismo que los anteriores, con la única diferencia
    # que estos utilizan lo que tu habías puesto en el post, lo del pipeline, tu clasificador y tal, hice pruebas con el mío pero los resulados eran muy parecidos
    # estos métodos simplemente extraen el texto de los tweets y se lo meten al pipeline para que lo entrene


    def tweet_formatter_text_mining(self, new_tweets):
        return np.array([t.text for t in new_tweets])

    def training_tweets_categories_text_mining(self):
        pipeline = text_mining.get_pipeline()
        tweets = TweetModel.objects.filter(autor__lang='es').exclude(categoria=None).order_by('pk')
        label = np.array(
            [[1 if categ in t.categoria.all() else 0 for categ in Categorias.objects.all().order_by('pk')] for t in
             tweets.select_related('autor')])
        tweet_features = tweets.values_list('text', flat=True)
        scores = cross_val_score(pipeline, tweet_features, label, cv=5)
        pipeline.fit(tweet_features, label)
        accuracy = {'mean': scores.mean(), 'std': scores.std() * 2}
        return pipeline, accuracy

    def recommend_tweets_text_mining(self, recommender, tweets_parameter, tweets):
        predicted_vector = recommender.predict(tweets_parameter)
        categorias = Categorias.objects.all().order_by('pk')
        tweets_classified = [{'tweet': build_from_tweepy_without_save(tweet), 'categorias': []} for tweet in tweets]
        index_categories = np.where(predicted_vector == 1)
        for label in xrange(len(index_categories[0])):
            aux = tweets_classified[index_categories[0][label]]['categorias']
            label_ = index_categories[1][label]
            categorias_ = categorias[int(label_)]
            aux.append(categorias_)
        return tweets_classified

    # Fin de los métodos de autenticación
    #
    # Los siguientes métodos empece a incluirnos en el mismo objeto, aunque su misión no son la misma que los métodos anteriores
    # Más adelante irán a otro objeto con la función más definida, este objeto en principio tiene todos los métodos de utilidad variada

    # Estos métodos son para el entrenamiento descrito en el correo sin el uso e text-mining
    # Este método es para extraer las features de los nuevos tweets

    def tweet_formatter_super_text(self, tweets):
        for t in tweets:
            if Autores.objects.filter(id_autor=t.author.id).count() == 0:
                Autores.objects.create(id_autor=t.author.id, name=t.author.name, lang=t.author.lang,
                                       friends_count=t.author.friends_count, followers_count=t.author.friends_count,
                                       favorites_count=t.author.favourites_count)
        self.autores = [a.id_autor for a in Autores.objects.all().order_by('pk')]
        tweet_features = np.zeros(
            (len(tweets), len(self.autores) + 3 + 1 + 30 * Categorias.objects.exclude(name="Social").count()))
        count = 0
        for t in tweets:
            features = self.new_tweet_model_to_classifier_super_text(t)
            tweet_features[count, :] = features
            count += 1
        return tweet_features

    def new_tweet_model_to_classifier_super_text(self, tweet_model):
        autores = np.zeros(len(self.autores))
        autores[self.autores.index(tweet_model.author.id)] = 1
        rt_vector = np.zeros(3)
        retweets = tweet_model.retweet_count
        rt_vector[
            0 if retweets < 20 else 1 if retweets < 50 else 2] = 1
        media = np.array([1 if 'media' in tweet_model.entities else 0])
        array_word_features = np.array([1 if word.word in unicode(tweet_model.text) else 0 for categoria in
                                        Categorias.objects.exclude(name="Social") for word in
                                        TextWord.objects.filter(categoria=categoria).exclude(word='https').exclude(
                                            word="rt").order_by('repeticiones')[:30]])
        # date = np.array([time.mktime(tweet_model.created_at.timetuple())])
        features_vector = np.concatenate((autores, rt_vector, media, array_word_features), axis=0)
        return features_vector

    # Estos métodos son para extraer las features de los tweets de entrenamiento, y entrenar el clasificador
    def training_tweets_categories_super_text(self):
        self.autores = [a.id_autor for a in Autores.objects.all().order_by('pk')]
        self.categorias = Categorias.objects.exclude(name="Social")
        tweets = TweetModel.objects.exclude(categoria=None).exclude(categoria__name="Social")
        tweet_features = np.zeros((len(tweets), len(self.autores) + 3 + 1 + 30 * self.categorias.count()))

        tweet_label = np.zeros((len(tweets), len(self.categorias)))
        count = 0
        for t in tweets.select_related('autor'):
            features, label = self.tweet_model_to_predict_vector_super_text(t)
            tweet_features[count, :] = features
            tweet_label[count, :] = label
            count += 1

        clasif = OneVsRestClassifier(SVC(kernel='rbf',C=100,gamma=0.001))
        clasif.fit(tweet_features, tweet_label)
        score = cross_val_score(clasif, tweet_features, tweet_label, cv=6, scoring='precision_weighted')
        accuracy= {'mean':score.mean(),'std':score.std() * 2}
        return clasif, accuracy


    def get_best_metrics(self):
        self.autores = [a.id_autor for a in Autores.objects.all().order_by('pk')]
        self.categorias = Categorias.objects.exclude(name="Social")
        tweets = TweetModel.objects.exclude(categoria=None).exclude(categoria__name="Social")
        tweet_features = np.zeros((len(tweets), len(self.autores) + 3 + 1 + 30 * self.categorias.count()))

        tweet_label = np.zeros((len(tweets), len(self.categorias)))
        count = 0
        for t in tweets.select_related('autor'):
            features, label = self.tweet_model_to_predict_vector_super_text(t)
            tweet_features[count, :] = features
            tweet_label[count, :] = label
            count += 1
        tuned_parameters = [{'estimator__kernel': ['rbf'], 'estimator__gamma': [1e-3, 1e-4],
                             'estimator__C': [1, 10, 100, 1000]},
                            {'estimator__kernel': ['linear'], 'estimator__C': [1, 10, 100, 1000]}]
        # scores = ['f1_weighted','f1_samples']
        scores = ['f1_weighted','f1_samples', 'precision_weighted','precision_samples', 'recall_weighted','recall_samples']

        accuracy = {}
        for sc in scores:
            clasif = GridSearchCV(OneVsRestClassifier(SVC(C=1)), tuned_parameters, cv=5, scoring=sc)
            clasif.fit(tweet_features, tweet_label)
            accuracy[sc] = {'params': clasif.best_params_, 'mean_' + sc: clasif.best_score_.mean(),
                        'std_' + sc: clasif.best_score_.std() * 2}
        return accuracy


    # Este método concretamente es el que extrae las features de lo tweets ya guardados
    def tweet_model_to_predict_vector_super_text(self, tweet_model):
        autores = np.zeros(len(self.autores))
        autores[self.autores.index(tweet_model.autor.id_autor)] = 1
        rt_vector = np.zeros(3)
        rt_vector[
            0 if tweet_model.retweets < 20 else 1 if tweet_model.retweets < 50 else 2] = 1
        media = np.array([1 if tweet_model.media else 0])
        array_word_features = np.array(
            [1 if word.word in tweet_model.text else 0 for categoria in self.categorias for word in
             TextWord.objects.filter(categoria=categoria).exclude(word='https').exclude(word='rt').order_by(
                 'repeticiones')[:30]])
        features_vector = np.concatenate((autores, rt_vector, media, array_word_features), axis=0)
        label = np.array(
            [1 if categ in tweet_model.categoria.all() else 0 for categ in self.categorias.order_by('pk')])
        return features_vector, label


    # Método para recomendar los nuevos tweets en función de sus features, este método se sirve del numpy.where para saber que tweets pertecenen a que categoría
    # de manera que las categorías puestas a 1 son las que se le asignan al tweet del índice al que pertenece
    def recommend_tweets_super_text(self, recommender, tweets_parameter, tweets):
        predicted_vector = recommender.predict(tweets_parameter)
        categorias = self.categorias.order_by('pk')
        tweets_classified = [{'tweet': build_from_tweepy_without_save(tweet), 'categorias': []} for tweet in tweets]
        index_categories = np.where(predicted_vector == 1)
        for label in xrange(len(index_categories[0])):
            aux = tweets_classified[index_categories[0][label]]['categorias']
            label_ = index_categories[1][label]
            categorias_ = categorias[int(label_)]
            aux.append(categorias_)
        return tweets_classified
