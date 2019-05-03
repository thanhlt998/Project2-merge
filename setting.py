import re
import os
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

MODEL_DIR = 'models'
STANDARD_ATTRIBUTES_FN = os.path.join(DIR_PATH, 'utils/attributes.json')
WEIGHT_MODEL_FN = os.path.join(DIR_PATH, 'utils/weight.json')
MAX_NO_SAMPLES = 20
SCRAPY_CONFIG = {
    'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    'DEPTH_PRIORITY': 1,
    'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
    'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
    'FEED_EXPORT_ENCODING': 'utf-8',
}

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'recruitment_information'
MONGO_COLLECTION = 'job_information1'

STANDARD_ATTRIBUTES = [
    "title",
    "description",
    "jobBenefits",
    "skills",
    "qualifications",
    "experienceRequirements",
    "datePosted",
    "validThrough",
    "employmentType",
    "hiringOrganization_name",
    "jobLocation_address_addressRegion",
    "jobLocation_address_addressCountry",
    "jobLocation_address_addressLocality",
    "baseSalary_currency",
    "baseSalary_minValue",
    "baseSalary_maxValue",
    "baseSalary_unitText",
    "occupationalCategory"
]

MAPPING_LABEL_NUM = {
    "title": '0.0',
    "hiringOrganization_name": '1.0',
    "datePosted": '2.0',
    "validThrough": '3.0',
    "jobLocation_address_addressRegion": '4.0',
    "other": '5.0',
    "occupationalCategory": '6.0',
    "jobBenefits": '7.0',
    "description": '8.0',
    "skills": '9.0',
    "experienceRequirements": '12.0',
    "": '13.0',
    "qualifications": '14.0',
    "employmentType": '15.0',
    "gender": '16.0',
    "age": '17.0',
    "jobLocation_address_addressCountry": '18.0',
    "jobLocation_address_addressLocality": '19.0'
}

MAPPING_NUM_LABEL = {num: label for label, num in MAPPING_LABEL_NUM.items()}


def get_schema_file(domain):
    return os.path.join(DIR_PATH, f'schema/{domain}_schema.json')


def get_context_file(domain):
    return os.path.join(DIR_PATH, f'schema/{domain}_context.json')


def get_domain(url):
    search_result = re.search(r'(?<=://www\.)\w+', url)
    if search_result is not None:
        domain = search_result.group(0)
    else:
        search_result = re.search(r'(?<=://)\w+', url)
        if search_result is not None:
            domain = search_result.group(0)
        else:
            domain = 'default'
    return domain

