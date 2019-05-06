import numpy as np
from random import randint
import os
import json
from .settings import *
import pickle
from .processFile import FileReader, FileStore
from .preProcessData import FeatureExtraction, NLP
from pyvi import ViTokenizer
from sklearn.svm import LinearSVC
from gensim import corpora, matutils
from sklearn.metrics import classification_report


class XpathMapping:
    def __init__(self, list_xpath_content, list_mismatch_attribute):
        self.list_xpath_content = list_xpath_content
        self.list_mismatch_attribute = list_mismatch_attribute

        with open(SVM_MODEL, 'rb') as f:
            self.classifier = pickle.load(f)
            f.close()

        with open(VECTOR_EMBEDDING, 'rb') as f:
            self.vectorizer = pickle.load(f)
            f.close()

    def get_xpath_mapping(self):
        data_features = []
        result1 = []
        j = 0
        for i in range(len(self.list_xpath_content)):
            data_features.append(' '.join(NLP(text=self.list_xpath_content[i][1]).get_words_feature()))
            features = self.vectorizer.transform(data_features)
            result_label = self.classifier.predict(features)
            xpath = self.list_xpath_content[i][0]
            if result_label[j] in self.list_mismatch_attribute:
                result1.append([result_label[j], xpath])
            j += 1
        print(result1)
        result = self.combine_xpath(result1)
        return result

    @staticmethod
    def is_different_position(array, string_need_compare, position, attr):
        for i in array:
            if string_need_compare != i[attr][position]:
                return True
        return False

    @staticmethod
    def get_same_string(strings):
        result = ''
        if len(strings) > 0:
            last_position = -1
            first_string = strings[0]
            for s in strings:
                if len(s) < len(first_string):
                    first_string = s

            for i in range(len(first_string)):
                for s in strings:
                    if s[i] != first_string[i]:
                        last_position = i
                        break
            if last_position > -1:
                result = first_string[:last_position]
                result = result.replace('[', '')
        return result

    def combine_xpath(self, list_xpath):
        result = {}
        labels = ['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0',
                  '14.0', '15.0', '16.0', '17.0', '18.0', '19.0']
        for label in labels:
            xpaths = []
            for item in range(len(list_xpath)):
                if list_xpath[item][0] == label:
                    index = next((j for j, it in enumerate(xpaths) if it['xpath'] == list_xpath[item][1]), -1)
                    if index == -1:
                        xpath_items = list_xpath[item][1].split('/')
                        xpath_items = [x for x in xpath_items if x.strip()]
                        xpaths.append({
                            'xpath': list_xpath[item][1],
                            'xpathItems': xpath_items
                        })
            if len(xpaths) > 1:
                combine_xpath = ''
                min_length = min([len(i['xpathItems']) for i in xpaths])
                for i in range(min_length):
                    string_need_compare = xpaths[0]['xpathItems'][i]
                    if self.is_different_position(xpaths, string_need_compare, i, 'xpathItems'):
                        different_position = i
                        break
                if different_position != -1:
                    for i in range(different_position):
                        combine_xpath = combine_xpath + '/' + xpaths[0]['xpathItems'][i]
                    last_strings = []
                    if different_position < min_length:
                        for xpath in xpaths:
                            last_strings.append(xpath['xpathItems'][different_position])
                        same_string = self.get_same_string(last_strings)
                        if same_string != '':
                            combine_xpath = combine_xpath + '/' + same_string
                result[label] = combine_xpath
            if len(xpaths) == 1:
                result[label] = xpaths[0]['xpath']

        return result
