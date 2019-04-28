import json


def load_dict(dict_name):
    if dict_name == 'address':
        dict_file_name = 'job_crawl/dict/address.json'
    elif dict_name == 'career':
        dict_file_name = 'job_crawl/dict/career.json'

    if dict_file_name is not None:
        with open(dict_file_name, encoding='utf-8-sig', mode='r') as f:
            dict = json.load(f)
            f.close()
        return dict
    return None
