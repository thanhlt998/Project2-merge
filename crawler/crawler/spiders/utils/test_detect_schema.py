from .detect_schema import JobSchemaDetection
from .model import DecisionTreeModel, NaiveBayesModel, LogisticRegressionModel
from .preprocess import FeaturesTransformer
from sklearn.metrics import accuracy_score
import json


def load_test_result(result_fn):
    with open(result_fn, mode='r', encoding='utf8') as f:
        result = json.load(f)
        f.close()
    return result


def main():
    test_result = load_test_result('job_crawl/job_crawl/spiders/schema/test.json')

    website_list = [
        'mywork',
        'vieclam24h',
        # 'viectotnhat'
    ]

    for website in website_list:
        with open(f'job_crawl/job_crawl/spiders/utils/test_data/{website}.json', mode='r', encoding='utf8') as f:
            jobs = json.load(f)
            f.close()

        d = JobSchemaDetection(jobs, 'job_crawl/job_crawl/spiders/models',
                               'job_crawl/job_crawl/spiders/utils/attributes.json',
                               'job_crawl/job_crawl/spiders/utils/weight_nb_dtree.json').get_mapping_schema()
        print(d)
        d_invert = {value: key for key, value in d.items()}
        result = test_result[website]
        predict = []
        for value in result.values():
            predict.append(d_invert.setdefault(value, ''))
        print(accuracy_score(list(result.keys()), predict))


if __name__ == '__main__':
    main()
