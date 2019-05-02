import os
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
FEATURES_TEST = os.path.join(DIR_PATH, 'feature_extraction/feature_test_full.pkl')
FEATURES_TRAIN = os.path.join(DIR_PATH, 'feature_extraction/feature_train_full.pkl')
VECTOR_EMBEDDING = os.path.join(DIR_PATH, 'vector_embedding/vector_embedding_full.pkl')
STOP_WORDS = os.path.join(DIR_PATH, 'stopwords-nlp-vi.txt')
SPECIAL_CHARACTER = '0123456789%@$.,=+-!;/()*"&^:#|\n\t\''
DICTIONARY_PATH = 'dictionary.txt'
LOGISTIC_MODEL = os.path.join(DIR_PATH, 'trained_model/logistic_model.pk')