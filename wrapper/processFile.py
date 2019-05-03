import json
from gensim import corpora, matutils
import pickle


class DataLoader(object):
    def __init__(self, dataPath):
        self.dataPath = dataPath

    def get_json(self):
        data = []
        with open(self.dataPath, encoding='utf8', mode='r') as f:
            data_ = json.load(f)
            for item in data_["data"]:
                for cont in item["item"]:
                    if cont['label'] != "":
                        content = cont["content"]
                        label = cont['label']
                        xpath = cont['xpath']
                        data.append({
                            "content": content,
                            "label": label,
                            "xpath": xpath
                        })
        return data


class FileReader(object):
    def __init__(self, filePath, encoder=None):
        self.filePath = filePath
        self.encoder = encoder if encoder is not None else 'utf-8'

    def read_stopwords(self):
        with open(self.filePath, mode='r', encoding=self.encoder) as f:
            stopwords = set([w.strip().replace(' ', '_') for w in f.readlines()])
            f.close()
        return stopwords

    def load_dictionary(self):
        return corpora.Dictionary.load_from_text(self.filePath)


class FileStore(object):
    def __init__(self, filePath, data=None):
        self.filePath = filePath
        self.data = data

    def store_json(self):
        with open(self.filePath, 'w') as outfile:
            json.dump(self.data, outfile)

    def store_dictionary(self, dict_words):
        dictionary = corpora.Dictionary(dict_words)
        dictionary.filter_extremes(no_below=100, no_above=0.5)
        dictionary.save_as_text(self.filePath)

    def save_pickle(self, obj):
        outfile = open(self.filePath, 'wb')
        fastPickler = pickle.Pickler(outfile, pickle.HIGHEST_PROTOCOL)
        fastPickler.fast = 1
        fastPickler.dump(obj)
        outfile.close()
