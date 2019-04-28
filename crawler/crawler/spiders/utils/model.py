from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from .preprocess import FeaturesTransformer


class NaiveBayesModel(object):
    def __init__(self):
        self.clf = self._init_pipeline()

    @staticmethod
    def _init_pipeline():
        pipeline = Pipeline([
            ("features_transformer", FeaturesTransformer('vietnamese-stopwords/vietnamese-stopwords-dash.txt')),
            ('bow', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', MultinomialNB())
        ])
        return pipeline


class DecisionTreeModel(object):
    def __init__(self):
        self.clf = self._init_pipeline()

    @staticmethod
    def _init_pipeline():
        pipeline = Pipeline([
            ("features_transformer", FeaturesTransformer('vietnamese-stopwords/vietnamese-stopwords-dash.txt')),
            ('bow', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', DecisionTreeClassifier(max_features=10))
        ])
        return pipeline


class LogisticRegressionModel(object):
    def __init__(self):
        self.clf = self._init_pipeline()

    @staticmethod
    def _init_pipeline():
        pipeline = Pipeline([
            ("features_transformer", FeaturesTransformer('vietnamese-stopwords/vietnamese-stopwords-dash.txt')),
            ('bow', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', LogisticRegression())
        ])
        return pipeline
