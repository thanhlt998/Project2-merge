from pyvi import ViTokenizer
import re
from py_stringmatching.similarity_measure.soft_tfidf import SoftTfIdf
import math


class DataReduction:
    def __init__(self, no_fields, Y, jaccard_measure=0.8, similarity_threshold=0.9):
        self.no_fields = no_fields
        self.jaccard_measure = jaccard_measure
        self.similarity_threshold = similarity_threshold
        self.size = len(Y)

        # Split Y into tokens and normalize
        self.Y_normalize = []
        for y in Y:
            y_split = []
            for i in range(no_fields):
                y_split.append(self.word_nomalize(self.word_split(y[i])))
            self.Y_normalize.append(y_split)

        # Build index
        self.Y_index = []
        Y_fields = [[] for i in range(no_fields)]
        for y in self.Y_normalize:
            for i in range(no_fields):
                Y_fields[i].append(y[i])

        for i in range(no_fields):
            self.Y_index.append(self.invert_index(Y_fields[i]))

        # Soft TF/IDF models1
        self.soft_tf_idf = []
        for i in range(no_fields):
            self.soft_tf_idf.append(SoftTfIdf(Y_fields[i]))

    def is_match(self, x):
        # normalize x
        x_normalize = [self.word_nomalize(self.word_split(x_)) for x_ in x]

        # size filtering
        Y_size_filtering = self.size_filtering(x_normalize, self.Y_normalize)

        # position filtering
        Y_candidates = self.position_filtering(x_normalize, Y_size_filtering)

        # check match
        flag = False  # flag check x match in Y
        for y in Y_candidates:
            inner_flag = True
            for i in range(self.no_fields):
                if self.soft_tf_idf[i].get_raw_score(x_normalize[i], y[i]) < self.similarity_threshold:
                    inner_flag = False
                    break
            if inner_flag:
                flag = True

        return flag

    @staticmethod
    def word_split(text):
        return re.compile("[\\w_]+").findall(ViTokenizer.tokenize(text))

    @staticmethod
    def word_nomalize(text):
        return [word.lower() for word in text]

    @staticmethod
    def invert_index(str_list):
        inverted = {}
        for i, s in enumerate(str_list):
            for word in s:
                locations = inverted.setdefault(word, [])
                locations.append(i)
        return inverted

    def size_filtering(self, x, Y):
        up_bound = [len(x_) / self.jaccard_measure for x_ in x]
        down_bound = [len(x_) * self.jaccard_measure for x_ in x]
        Y_size_filtering = []

        for y in Y:
            flag = True
            for i in range(self.no_fields):
                flag &= down_bound[i] <= len(y[i]) <= up_bound[i]
            if flag:
                Y_size_filtering.append(y)

        return Y_size_filtering

    def calc_prefix(self, x, y):
        k = math.ceil((self.jaccard_measure / (self.jaccard_measure + 1)) * (len(x) + len(y)))
        if len(x) >= k and len(y) >= k:
            return y, k
        return None

    def position_filtering(self, x, Y):
        # Calc an array of tuple (y, prefix) of Y
        Y_prefix = []
        ids = []

        for i, y in enumerate(Y):
            flag_choose = True
            prefix = []
            for j in range(self.no_fields):
                p = self.calc_prefix(x[j], y[j])
                prefix.append(p)
                if p is None:
                    flag_choose = False
            if flag_choose:
                Y_prefix.append(prefix)
                ids.append(i)

        # Calculate array of y' = y[len(y) - prefix_filtering + 1] sorted by frequency and min_prefix
        Y_ = []
        min_prefix = [10000 for i in range(self.no_fields)]
        for y in Y_prefix:
            y_ = []
            for i in range(self.no_fields):
                y_.append(self.sort_by_frequency(self.Y_index[i], y[i][0])[:len(y[i][0]) - y[i][1] + 1])
                if y[i][1] < min_prefix[i]:
                    min_prefix[i] = y[i][1]

            Y_.append(y_)

        # Build inverted index of y' (Y_)
        Y_index = []
        for i in range(self.no_fields):
            Y_index.append(self.invert_index([y[i] for y in Y_]))

        # Sort x by frequency
        x_ = []
        for i in range(self.no_fields):
            x_.append(self.sort_by_frequency(self.Y_index[i], x[i]))

        # Ids of y_ satisfied
        Y_filtered_id = []

        for i in range(self.no_fields):
            y_filter_id = []
            for x_i in x_[i][:len(x_[i]) - min_prefix[i] + 1]:
                id_match = Y_index[i].get(x_i)
                if id_match is not None:
                    y_filter_id += id_match
            Y_filtered_id.append(y_filter_id)

        # set of ids y_ satisfied
        Y_set_id = set(Y_filtered_id[0])
        for y_filter_id in Y_filtered_id[1:]:
            Y_set_id.intersection_update(y_filter_id)

        return [Y[ids[i]] for i in Y_set_id]

    @staticmethod
    def sort_by_frequency(inverted_index, arr):
        return sorted(arr,
                      key=lambda arr_i: len(inverted_index.get(arr_i) if inverted_index.get(arr_i) is not None else []))
