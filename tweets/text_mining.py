# -*- coding: utf-8 -*-
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.data import load
from nltk.stem import SnowballStemmer
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm.classes import SVC, LinearSVC

# Este módulo simplemente tienes los métodos para usar las técnicas de text mining..., el tokenize, las stop_words etc...
from tweets.models import TextWord


def get_stop_words():
    return stopwords.words('spanish')


def get_non_words():
    non_words = [unicode(l) for l in list(punctuation)]
    non_words.extend([u'¿', u'¡'])
    non_words.extend([unicode(i) for i in range(10)])
    return non_words


def stem_tokens(tokens, stemmer):
    stemmed = [stemmer.stem(item) for item in tokens]
    return stemmed


def tokenize(text):
    non_words = get_non_words()
    text = ''.join([c for c in text if c not in non_words])
    tokens = word_tokenize(text)

    try:
        stemmer = SnowballStemmer('spanish')
        stems = stem_tokens(tokens, stemmer)
    except Exception as e:
        print(e)
        print(text)
        stems = ['']
    return stems


def get_pipeline():
    spanish_stopwords = get_stop_words()
    vectorize = CountVectorizer(analyzer='word',
                                tokenizer=tokenize,
                                lowercase=True,
                                stop_words=spanish_stopwords,
                                min_df=50,
                                max_df=1.9,
                                ngram_range=(1, 1),
                                max_features=100000)
    pipeline = Pipeline([
        ('vectorize', vectorize),
        ('onevsall', OneVsRestClassifier(SVC(kernel='rbf',C=1)))
    ])
    return pipeline


def save_special_word(non_words, snow, tweet):
    words = word_tokenize(tweet.text, language='spanish')
    tweet_categoria_all = tweet.categoria.all()
    for w in words:
        save_word_in_category(non_words, snow, tweet_categoria_all, w)


def save_word_in_category(non_words, snow, tweet_categoria_all, w):
    word_stem = snow.stem(w)
    if isWgoodWord(non_words, w, word_stem):
        for cat in tweet_categoria_all:
            word_db, created = TextWord.objects.get_or_create(word=word_stem, categoria=cat)
            if not created:
                word_db.repeticiones += 1
                word_db.save()


def isWgoodWord(non_words, w, word_stem):
    return w not in stopwords.words('spanish') and w not in non_words and word_stem not in stopwords.words('spanish')