import re
import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

MODEL_DIR = 'models'
STANDARD_ATTRIBUTES_FN = os.path.join(DIR_PATH, 'utils/attributes.json')
WEIGHT_MODEL_FN = os.path.join(DIR_PATH, 'utils/weight.json')
MAX_NO_SAMPLES = 20

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'recruitment_information'
MONGO_COLLECTION = 'job_information'

SCRAPY_CONFIG = {
    'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    'DEPTH_PRIORITY': 1,
    'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
    'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
    'FEED_EXPORT_ENCODING': 'utf-8',
    # 'ITEM_PIPELINES': {
    #     'pipelines.MongoPipeline': 300
    # },
    # 'MONGO_URI': MONGO_URI,
    # 'MONGO_DATABASE': MONGO_DATABASE,
    # 'MONGO_COLLECTION': MONGO_COLLECTION
}

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


WEB_LIST = {
    "vieclam24h": {
        "start_url": "https://vieclam24h.vn/tim-kiem-viec-lam-nhanh/?hdn_nganh_nghe_cap1=&hdn_dia_diem=&hdn_tu_khoa=&hdn_hinh_thuc=&hdn_cap_bac=",
        "next_page": "//ul[@class='pagination']/li[@class='next']/a",
        "job_url": "//*[@id='cols-right']/div[1]/div[1]/div/div[1]/div/div/div/div[2]/span[1]/a"
    }
    # "careerbuilder": {
    #     "start_url": "https://careerbuilder.vn/viec-lam/tat-ca-viec-lam-vi.html",
    #     "next_page": "//div[@class='paginationTwoStatus']/a[@class='right']",
    #     "job_url": "//div[contains(@class,'gird_standard')]//dd[contains(@class, 'brief')]/span[@class='jobtitle']/h3[@class='job']/a"
    # },
    # "vietnamworks": {
    #     "start_url": "https://www.vietnamworks.com/tim-viec-lam/tat-ca-viec-lam",
    #     "next_page": "//*[@id='pagination-container']/div/ul/li[last()]/a",
    #     "job_url": "//*[@id='job-list']/div[1]/div/div/div/div/div[2]/div/h3/a"
    # },
    # "careerlink": {
    #     "start_url": "https://www.careerlink.vn/vieclam/list?keyword_use=A",
    #     "next_page": "//div[contains(@class, 'search-result-paginator')]/nav/ul[@class='pagination']/li[@class='active']/following-sibling::li[1]/a",
    #     "job_url": "//div[@class='list-group list-search-result-group tlp headline']/div[contains(@class, 'list-group-item')]/h2[@class='list-group-item-heading']/a"
    # },
    # "timviecnhanh": {
    #     "start_url": "https://www.timviecnhanh.com/vieclam/timkiem?tu_khoa=&nganh_nghe%5B%5D=&tinh_thanh%5B%5D=",
    #     "next_page": "/html/body/section/div/div[1]/div/div/article[1]/table/tfoot/tr/td/div/a[last()]",
    #     "job_url": "/html/body/section/div/div/div/div/article[1]/table/tbody/tr/td[1]/a[1]"
    # },
    # "topcv": {
    #     "start_url": "https://www.topcv.vn/viec-lam/moi-nhat.html?utm_source=click-search-job&utm_medium=page-job&utm_campaign=tracking-job",
    #     "next_page": "//*[@id='box-job-result']/div[2]/ul/li[last()]/a",
    #     "job_url": "//*[@id='box-job-result']/div[1]/div/div/div[2]/h4/a"
    # },
    # "viectotnhat": {
    #     "start_url": "https://viectotnhat.com/viec-lam/tim-kiem?tu_khoa=&nganh_nghe=0&tinh_thanh=0&muc_luong=&loai_hinh=&kinh_nghiem=&trinh_do=&gioi_tinh=",
    #     "next_page": "//*[@id='main-content']/div/div/div/div[1]/div[2]/nav/ul/li[last()]/a",
    #     "job_url": "//*[@id='main-content']/div/div/div/div[1]/div[1]/div[2]/div/div[1]/h3/a"
    # },
    # "mywork": {
    #     "start_url": "https://mywork.com.vn/tuyen-dung",
    #     "next_page": "//*[@id='idJobNew']/div/div[2]/section/ul/li[last()]/a",
    #     "job_url": "//*[@id='idJobNew']/div/div[1]/section/div/div[1]/div/div/p/a"
    # },
    # "Itviec.com": {
    #     "start_url": "https://itviec.com/it-jobs",
    #     "next_page": "//*[@id='show_more']/a",
    #     "job_url": "//*[contains(@id, 'job_')]/div/div[2]/div[1]/div/h2/a"
    # },
    # "Topdev.vn": {
    #     "start_url": "https://topdev.vn/it-jobs",
    #     "next_page": "//*[@id='job-search']/div/div/div[1]/div[1]/div/div[3]/ul/li[last()]/a",
    #     "job_url": "//*[@id='job-list']/div/div/div/div/div/div[2]/div/h3/a"
    # },
    # "Intership.edu.vn": {
    #     "start_url": "https://www.internship.edu.vn/?post_type=noo_job&s=",
    #     "next_page": "//*[contains(@id, 'scroll')]/div[3]/a[contains(@class, 'next')]",
    #     "job_url": "//*[contains(@id, 'scroll')]/div[2]/div/article/a"
    # },
    # "Iconicjob.vn": {
    #     "start_url": "https://iconicjob.vn/tim-viec-lam/",
    #     "next_page": "//*[@id='job-blocks']/div[2]/div[1]/div/div[14]/ul/li/a[@rel='next']",
    #     "job_url": "//*[@id='job-blocks']/div[2]/div[1]/div/div/div/div[2]/div[1]/div[1]/a"
    # },
    # "Jobsgo.vn": {
    #     "start_url": "https://jobsgo.vn/viec-lam.html",
    #     "next_page": "//*[@id='page-content']/div[12]/ul/li[@class='next']/a",
    #     "job_url": "//*[@id='page-content']/div/div/div/div/div[2]/span/a[1]"
    # },
    # "Hoteljob.vn": {
    #     "start_url": "https://www.hoteljob.vn/tim-viec?keyword=&city_id=&career_id=",
    #     "next_page": "//*[@id='no-more-tables']/tbody/tr[32]/td/nav/ul/li[@class='next']/a",
    #     "job_url": "//*[@id='no-more-tables']/tbody/tr/td[2]/p[1]/a"
    # },
    # "Enworld.com.vn": {
    #     "start_url": "https://www.enworld.com.vn/job-search?utf8=%E2%9C%93&search%5Bquery%5D=&selected_locations=&search%5Bradius%5D=50.0&disciplines=",
    #     "next_page": "//*[@id='body']/section/div[2]/div[3]/nav/span[@class='next']/a",
    #     "job_url": "//*[@id='body']/section/div[2]/ul/li/div/div[1]/div[2]/div[1]/a"
    # },
    # "Tuyencongnhan.vn": {
    #     "start_url": "https://tuyencongnhan.vn/tim-viec",
    #     "next_page": "//*[@id='no-more-tables']/div[2]/div/div/div[2]/div[2]/div/ul/li[contains(@class, 'next')]/a",
    #     "job_url": "//*[@id='result-search-job']/article/div/div[2]/div/p[1]/a"
    # },
    # "Anphabe.com": {
    #     "start_url": "https://www.anphabe.com/big-jobs/search/",
    #     "next_page": "//*[@id='block-system-main']/div/div/div/div/div/div[3]/ul/li[@class='pager-next']/a",
    #     "job_url": "//*[@id='block-system-main']/div/div/div/div/div/div[2]/div/ul/li/div/div/div[2]/h2/a"
    # }
}


def get_correct_url(url, response):
    if "http" in url:
        return url
    else:
        return response.urljoin(url)
