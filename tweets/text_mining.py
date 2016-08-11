import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.data import load
from nltk.stem import SnowballStemmer
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm.classes import SVC


def get_stop_words():
    return stopwords.words('spanish')


def get_non_words():
    non_words = list(punctuation)
    non_words.extend(['¿', '¡'])
    non_words.extend([str(i) for i in range(10)])
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
    vectorize = CountVectorizer(analyzer='word',tokenizer=tokenize,lowercase=True,stop_words=spanish_stopwords)
    pipeline = Pipeline([
        ('vectorize',vectorize)
        ('onevsall',OneVsRestClassifier(SVC(kernel='linear',C = 100)))
    ])
    return pipeline



