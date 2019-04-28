import re

MODEL_DIR = 'crawler/crawler/spiders/models'
STANDARD_ATTRIBUTES_FN = 'crawler/crawler/spiders/utils/attributes.json'
WEIGHT_MODEL_FN = 'crawler/crawler/spiders/utils/weight.json'
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


def get_schema_file(domain):
    return f'crawler/crawler/spiders/schema/{domain}_schema.json'


def get_context_file(domain):
    return f'crawler/crawler/spiders/schema/{domain}_context.json'


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
