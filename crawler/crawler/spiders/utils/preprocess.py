from pyvi.ViTokenizer import ViTokenizer
from sklearn.base import BaseEstimator, TransformerMixin
import re


def load_stop_words(fn):
    with open(fn, mode='r', encoding='utf8') as f:
        words = f.read()
        f.close()
    return words.split('\n')


class FileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self, is_contain_labels=True):
        with open(self.file_path, mode='r', encoding='utf8') as f:
            lines = f.readlines()
            f.close()
        if is_contain_labels:
            X, y = [], []
            for line in lines:
                line = line.strip()
                if line == '':
                    continue
                s = line.strip().split('\t')
                X.append(s[0])
                y.append(s[1])
            return X, y
        else:
            return lines


class FeaturesTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, stop_words_fn):
        self.tokenizer = ViTokenizer()
        self.SPECIAL_CHARACTER = '0123456789%@$.,=+-!;/()*"&^:#|\n\t\''
        self.STOP_WORDS = load_stop_words(stop_words_fn)

    def fit(self, *_):
        return self

    def remove_stop_words(self, text):
        return ' '.join([token for token in re.split('\\s+', text) if
                         token not in self.STOP_WORDS and token not in self.SPECIAL_CHARACTER])

    def transform(self, X, y=None, **fit_params):
        return [self.remove_stop_words(self.tokenizer.tokenize(x)) for x in X]
