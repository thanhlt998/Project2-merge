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
    def combineXpath(list_xpath):
        result = []
        labels = ['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0','14.0', '15.0', '16.0', '17.0', '18.0', '19.0']
        for label in labels:
            xpaths = [list_xpath[i][1] for i in range(len(list_xpath)) if list_xpath[i][0] == label]
            if len(xpaths) > 1:
                xpathMerge = ''
                xpathArray = []
                for xpath in xpaths:
                    xpathArray.append([x for x in str(xpath).split('/') if x.strip()])
                xpathMerge = mergeXpaths(xpathArray)
                result.append([label, xpathMerge])
            elif len(xpaths) ==1:
                result.append([label, xpaths[0]])
        return result
    @staticmethod
    def mergeXpaths(xpathArray):
        result = ''
        while len(xpathArray) > 0:
            tags = [i[0] for i in xpathArray if len(i) > 0]
            if len(tags) <= 1:
                break
            if len(tags) > 1:
                tagMostAppear = getMostAppear(tags)
                numberAppear = tags.count(tagMostAppear)
                if numberAppear > 1:
                    xpathArray = [i for i in xpathArray if len(i) > 0 and i[0] == tagMostAppear]
                    for x in xpathArray:
                        x.remove(tagMostAppear)
                    result = result + '/' + tagMostAppear
                else:
                    for x in xpathArray:
                        x.pop(0)
                    stringCompare = compareStrings(tags)
                    if stringCompare != '':
                        result = result + '/' + compareStrings(tags)
        return result
    @staticmethod
    def compareStrings(strings):
        result = ''
        if len(strings) <= 1:
            return result
        minLength = min([len(i) for i in strings])
        if minLength == 0:
            return result
        while len(strings) > 0:
            characters = [c[0] for c in strings if len(c) > 0]
            characterMostAppear = getMostAppear(characters)
            numberAppear = characters.count(characterMostAppear)
            if numberAppear <= 1:
                break
            strings = [i for i in strings if len(i) > 0 and i[0] == characterMostAppear]
            strings = [i[1:] for i in strings]
            result = result + characterMostAppear
        result = result.replace('[','')
        return result
    @staticmethod
    def getMostAppear(strings):
        result = max(strings, key = strings.count)
        return result
