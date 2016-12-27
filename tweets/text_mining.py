# -*- coding: utf-8 -*-
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from string import punctuation

# Este módulo simplemente tienes los métodos para usar las técnicas de text mining..., el tokenize, las stop_words etc...
from tweets.models import TextWord

def get_non_words():
    non_words = [unicode(l) for l in list(punctuation)]
    non_words.extend([u'¿', u'¡'])
    non_words.extend([unicode(i) for i in range(10)])
    return non_words

def save_special_word(non_words, snow, tweet):
    words = word_tokenize(tweet.text, language='spanish')
    tweet_categoria_all = tweet.categoria.all()
    for w in words:
        save_word_in_category(non_words, snow, tweet_categoria_all, w)


def save_word_in_category(non_words, snow, tweet_categoria_all, w):
    word_stem = snow.stem(w)
    if isGoodWord(non_words, w, word_stem):
        for cat in tweet_categoria_all:
            word_db, created = TextWord.objects.get_or_create(word=word_stem, categoria=cat)
            if not created:
                word_db.repeticiones += 1
                word_db.save()


def isGoodWord(non_words, w, word_stem):
    return w not in stopwords.words('spanish') and w not in non_words and word_stem not in stopwords.words('spanish')