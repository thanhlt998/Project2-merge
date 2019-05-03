from .settings import *
import os
from random import randint
from datetime import datetime
from .processFile import FileStore, FileReader, DataLoader
from pyvi import ViTokenizer
from gensim import corpora, matutils
from sklearn.feature_extraction.text import TfidfVectorizer


class NLP(object):
    def __init__(self, text=None):
        self.text = text
        self.__set_stopwords()

    def __set_stopwords(self):
        self.stopwords = FileReader(STOP_WORDS).read_stopwords()

    def segmentation(self):
        return ViTokenizer.tokenize(self.text)

    def split_words(self):
        text = self.segmentation()
        try:
            return [x.strip(SPECIAL_CHARACTER).lower() for x in text.split()]
        except TypeError:
            return []

    def get_words_feature(self):
        split_words = self.split_words()
        return [word for word in split_words if word.encode('utf-8') not in self.stopwords]


class FeatureExtraction(object):
    def __init__(self, data):
        self.data = data

    def __build_dictionary(self):
        print('Building dictionary')
        dict_words = []
        i = 0
        for text in self.data:
            i += 1
            print("Dictionary Step {} / {}".format(i, len(self.data)))
            words = NLP(text=text['content']).get_words_feature()
            dict_words.append(words)
        FileStore(filePath=DICTIONARY_PATH).store_dictionary(dict_words)

    def __load_dictionary(self):
        if os.path.exists(DICTIONARY_PATH) == False:
            self.__build_dictionary()
        self.dictionary = FileReader(DICTIONARY_PATH).load_dictionary()

    def __build_dataset(self):
        print('Building dataset')
        self.features = []
        self.labels = []
        i = 0
        for d in self.data:
            i += 1
            print("Step {} / {}".format(i, len(self.data)))
            self.features.append(self.get_dense(d['content']))
            self.labels.append(d['label'])

    def get_dense(self, text):
        # remove stopword
        words = NLP(text).get_words_feature()
        # Bag of words
        self.__load_dictionary()
        vec = self.dictionary.doc2bow(words)
        dense = list(matutils.corpus2dense([vec], num_terms=len(self.dictionary)).T[0])
        return dense

    # def build_tfidf(self,text):

    def get_data_and_label_tfidf(self):
        print('Building dataset')
        self.features = []
        self.labels = []
        i = 0
        for d in self.data:
            i += 1
            print("Step {} / {}".format(i, len(self.data)))
            content = ' '.join(NLP(d['content']).get_words_feature())
            print(content)
            print(d['label'])
            self.features.append(' '.join(NLP(d['content']).get_words_feature()))
            self.labels.append(d['label'])
        return self.features, self.labels

    def get_data_and_label_bow(self):
        self.__build_dataset()
        return self.features, self.labels

    def read_feature(self):
        return self.data['features'], self.data['labels']


def get_feature_dict(value_features, value_labels):
    return {
        "features": value_features,
        "labels": value_labels
    }


# if __name__ == '__main__':
#     print('Reading data raw... ', str(datetime.now()))
#     json_train = DataLoader(dataPath=DATA_TRAIN_JSON).get_json()
#     json_test = DataLoader(dataPath=DATA_TEST_JSON).get_json()
#     print('Load Data to JSON Done! ', str(datetime.now()))
#
#     # Feature Extraction
#     print('Featuring Extraction... ', str(datetime.now()))
#
#     # tf-idf
#     features_train, labels_train = FeatureExtraction(data=json_train).get_data_and_label_tfidf()
#     features_test, labels_test = FeatureExtraction(data=json_test).get_data_and_label_tfidf()
#     vectorizer = TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0, ngram_range=(1, 2))
#     features_train = vectorizer.fit_transform(features_train)
#     features_test = vectorizer.transform(features_test)
#     FileStore(filePath=VECTOR_EMBEDDING).save_pickle(obj=vectorizer)
#
#     print('Feature Extraction Done! ', str(datetime.now()))
#
#     # Save feature extraction
#     features_train_dict = get_feature_dict(value_features=features_train, value_labels=labels_train)
#     print(features_train_dict)
#     features_test_dict = get_feature_dict(value_features=features_test, value_labels=labels_test)
#     print(features_test_dict)
#     FileStore(filePath=FEATURES_TRAIN).save_pickle(obj=features_train_dict)
#     FileStore(filePath=FEATURES_TEST).save_pickle(obj=features_test_dict)
#
#     print("Store data DONE!")
