from scrapy import Spider, Request
import json
import os
import re
import pymongo
from pyMicrodata import pyMicrodata
from lxml import etree

from utils.utils import parse_json
from utils.job_normalization import normalize_job
from utils.utils import flatten_dict
from utils.remove_similar_data.remove_similar_data import DataReduction
from setting import *


class Crawler(Spider):
    name = "crawler"
    microdata = pyMicrodata()
    no_duplicated_items = 0
    context = None
    standard_sample = None
    map_schema = None
    data_reduction = None
    parse_job = None

    custom_settings = {
        # 'FEED_FORMAT': 'json',
        # 'FEED_URI': 'topcv.json',
        'ITEM_PIPELINES': {
            'pipelines.MongoPipeline': 300
        },
        'MONGO_URI': MONGO_URI,
        'MONGO_DATABASE': MONGO_DATABASE,
        'MONGO_COLLECTION': MONGO_COLLECTION
    }

    def __init__(self, name=None, **kwargs):
        self.domain = kwargs.get('domain')
        super(Crawler, self).__init__(name, **kwargs)

    def start_requests(self):
        if os.path.exists(get_context_file(self.domain)):
            with open(get_context_file(self.domain), mode='r', encoding='utf8') as f:
                self.context = json.load(f)
                f.close()
            if not self.context['is_finished']:
                raise Exception('Context file is not completed')
            else:
                if self.context['data_format'] == 'json+ld':
                    self.parse_job = self.parse_job_json
                else:
                    self.parse_job = self.parse_job_microdata

                self.standard_sample = self.get_standard_sample(STANDARD_ATTRIBUTES_FN)
                self.map_schema = self.get_map_schema(self.context['schema'])
                self.data_reduction = self.get_data_reduction(MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION)
        else:
            raise Exception('Context file name not existed: ' + get_context_file(self.domain))
        yield Request(url=self.context['start_url'], callback=self.parse)

    def parse(self, response):
        next_page = response.xpath(self.context['selectors']['next_page'] + '/@href').get()
        job_urls = response.xpath(self.context['selectors']['job_url'] + '/@href').getall()

        for job_url in job_urls:
            job_url = response.urljoin(job_url)
            yield Request(url=job_url, callback=self.parse_job)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(url=next_page, callback=self.parse)

    def parse_job_json(self, response):
        job_url = response.request.url
        jobs = self.get_json_from_response_json(response)
        job_selectors = self.context['selectors']['job_selectors']
        for job in jobs:
            job = self.change_to_right_form(job)
            for field, selector in job_selectors.items():
                job[field] = ','.join(
                    text.strip() for text in response.xpath(selector + '/text()').getall() if text is not None)
            job = self.normalize(job, job_url)
            yield job

    def parse_job_microdata(self, response):
        job_url = response.request.url
        jobs = self.get_json_from_response_microdata(response)
        job_selectors = self.context['selectors']['job_selectors']
        for job in jobs:
            job = self.change_to_right_form(job)
            for field, selector in job_selectors.items():
                job[field] = ','.join(
                    text.strip() for text in response.xpath(selector + '/text()').getall() if text is not None)
            job = self.normalize(job, job_url)
            yield job

    @staticmethod
    def get_json_from_response_json(response):
        result = []
        dom = etree.HTML(response.body.decode("utf8"))
        json_node = dom.xpath("//script[text()]")
        for node in json_node:
            try:
                job = json.loads(node.text, strict=False)
                if job['@type'] == 'JobPosting':
                    result.append(job)

            except (ValueError, TypeError):
                pass
        return result

    def get_json_from_response_microdata(self, response):
        raw_json = json.loads(self.microdata.rdf_from_source(response.body, 'json-ld').decode('utf8'))
        result = parse_json(raw_json)
        return result

    def change_to_right_form(self, job):
        norm_job = self.standard_sample.copy()
        flatten_job = flatten_dict(job)

        for key, value in self.map_schema.items():
            real_value = flatten_job.get(key)
            if real_value is None:
                continue
            else:
                attribute = norm_job
                for attribute_level in value[:-1]:
                    attribute = attribute.get(attribute_level)
                if type(real_value) is str:
                    attribute[value[-1]] = re.sub(r'<[^<>]*>', '', str(real_value))
                elif type(attribute[value[-1]]) == dict and type(real_value) == list:
                    attribute[value[-1]] = real_value[0]
                else:
                    attribute[value[-1]] = real_value

        return norm_job

    def normalize(self, job, url):
        result = normalize_job(job)
        result['url'] = url

        # Check duplicate
        if self.data_reduction.is_match(self.get_filter_data(job)):
            self.no_duplicated_items += 1
            result = None

        return result

    @staticmethod
    def get_standard_sample(file_name):
        if os.path.exists(file_name):
            with open(file_name, mode='r', encoding='utf8') as f:
                standard_sample = json.load(f)
                f.close()
        else:
            raise Exception('Not exist standard file: ' + file_name)

        return standard_sample

    @staticmethod
    def get_map_schema(schema):
        return {key: value.split('_') for key, value in schema.items()}

    def get_data_reduction(self, uri, database, collection):
        collection = pymongo.MongoClient(uri)[database][collection]
        jobs = list(collection.find({},
                                    {'title': 1, 'hiringOrganization.name': 1, 'jobLocation.address.addressRegion': 1,
                                     '_id': 0}))
        data = [self.get_filter_data(job) for job in jobs]

        data_reduction = DataReduction(3, data)
        return data_reduction

    @staticmethod
    def get_filter_data(job):
        title = job['title']
        hiring_organization_name = job['hiringOrganization']['name']
        if type(job['jobLocation']) is list:
            address_region = ','.join([location['address']['addressRegion'] for location in job['jobLocation']])
        else:
            address_region = job['jobLocation']['address']['addressRegion']

        return [title, hiring_organization_name, address_region]

    def close(self, spider, reason):
        print('Number of duplicated items: %d' % self.no_duplicated_items)
        print("Finished!")
