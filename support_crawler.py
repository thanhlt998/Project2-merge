from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from lxml import etree
import json
from pyMicrodata import pyMicrodata
import os
import re
import pymongo

from utils.utils import parse_json
from utils.detect_schema import JobSchemaDetection
from utils.model import NaiveBayesModel, DecisionTreeModel, LogisticRegressionModel
from utils.preprocess import FeaturesTransformer
from utils.job_normalization import normalize_job
from utils.utils import flatten_dict
from utils.remove_similar_data.remove_similar_data import DataReduction
from wrapper.xpath_mapping import XpathMapping
from setting import *


class SchemaCrawler(Spider):
    name = "schema_crawler"
    microdata = pyMicrodata()
    schema = None
    get_job_sample = None
    samples = []
    selectors = {
        # 'job_url': "//*[@id='box-job-result']/div[1]/div/div/div[2]/h4/a",
        # 'next_page': "//*[@id='box-job-result']/div[2]/ul/li[last()]/a",
    }
    # start_url = 'https://www.topcv.vn/viec-lam/moi-nhat.html?utm_source=click-search-job&utm_medium=page-job&utm_campaign=tracking-job'
    context = {}
    domain = None

    def __init__(self, name=None, **kwargs):
        self.start_url = kwargs.get('start_url')
        self.selectors['job_url'] = kwargs.get('job_url')
        self.selectors['next_page'] = kwargs.get('next_page')
        self.domain = kwargs.get('domain')
        super(SchemaCrawler, self).__init__(name, **kwargs)

    def start_requests(self):
        self.context['start_url'] = self.start_url
        self.context['domain'] = self.domain
        if not os.path.exists(get_context_file(self.domain)):
            if not os.path.exists(STANDARD_ATTRIBUTES_FN):
                raise Exception('Not exist standard file: ' + STANDARD_ATTRIBUTES_FN)
            yield Request(url=self.start_url, callback=self.get_data_format)

    def parse(self, response):
        pass

    def get_data_format(self, response):
        sample_job_url = response.xpath(self.selectors['job_url'] + '/@href').get()
        yield Request(url=sample_job_url, callback=self.decide_data_format)

    def decide_data_format(self, response):
        can_crawl = True
        if self.is_data_json_format(response):
            self.get_job_sample = self.get_job_sample_json
            self.context['data_format'] = 'json+ld'
        elif self.is_data_microdata_format(response):
            self.get_job_sample = self.get_job_sample_microdata
            self.context['data_format'] = 'microdata'
        else:
            print('Cannot crawl')
            can_crawl = False

        if can_crawl:
            yield Request(url=self.start_url, callback=self.get_job_url_samples)

    def get_job_url_samples(self, response):
        job_urls = response.meta.setdefault('job_urls', [])
        next_page = response.xpath(self.selectors['next_page'] + '/@href').get()
        job_urls += response.xpath(self.selectors['job_url'] + '/@href').getall()

        if next_page is not None and len(job_urls) < MAX_NO_SAMPLES:
            yield Request(url=next_page, callback=self.get_job_url_samples, meta={'job_urls': job_urls})
        else:
            yield Request(url=job_urls[0], callback=self.get_job_sample, meta={'job_urls': job_urls[1:MAX_NO_SAMPLES]})

    def decide_schema(self):
        schema = JobSchemaDetection(self.samples, MODEL_DIR, STANDARD_ATTRIBUTES_FN,
                                    WEIGHT_MODEL_FN).get_mapping_schema()
        self.context['schema'] = schema
        self.context['selectors'] = self.selectors
        self.context['is_finished'] = False
        with open(get_context_file(self.domain), mode='w', encoding='utf8') as f:
            json.dump(self.context, f)
            f.close()

    def get_job_sample_json(self, response):
        samples = response.meta.setdefault('samples', [])
        job_urls = response.meta['job_urls']
        samples += self.get_json_from_response_json(response)

        if len(job_urls) > 0:
            yield Request(url=job_urls[0], callback=self.get_job_sample_json,
                          meta={'samples': samples, 'job_urls': job_urls[1:]})
        else:
            self.samples = samples
            self.decide_schema()

    def get_job_sample_microdata(self, response):
        samples = response.meta.setdefault('samples', [])
        job_urls = response.meta['job_urls']
        samples.append(self.get_json_from_response_microdata(response))

        if len(job_urls) > 0:
            yield Request(url=job_urls[0], callback=self.get_job_sample_microdata,
                          meta={'samples': samples, 'job_urls': job_urls[1:]})
        else:
            self.samples = samples
            self.decide_schema()

    def is_data_json_format(self, response):
        return len(self.get_json_from_response_json(response)) > 0

    def is_data_microdata_format(self, response):
        return len(self.get_json_from_response_microdata(response)) > 0

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


class XpathCrawler(Spider):
    name = "xpath_crawler"
    context = None
    mismatch_attributes = None

    def __init__(self, name=None, **kwargs):
        self.domain = kwargs.get('domain')
        super(XpathCrawler, self).__init__(name=name, **kwargs)

    def start_requests(self):
        if os.path.exists(get_context_file(self.domain)):
            with open(get_context_file(self.domain), mode='r', encoding='utf-8') as f:
                self.context = json.load(f)
                f.close()

            self.mismatch_attributes = self.get_mismatch_attributes()
            yield Request(url=self.context['start_url'], callback=self.get_job_sample_url)
        else:
            raise Exception('Not exist context file: ' + get_context_file(self.domain))

    def parse(self, response):
        pass

    def get_mismatch_attributes(self):
        matched_attributes = self.context['schema'].values()
        mismatch_attributes = []

        for attribute in STANDARD_ATTRIBUTES:
            if attribute not in matched_attributes:
                mismatch_attributes.append(MAPPING_LABEL_NUM[attribute])

        return mismatch_attributes

    def get_job_sample_url(self, response):
        job_urls = response.xpath(self.context['selectors']['job_url'] + "/@href").getall()
        yield Request(url=job_urls[0], callback=self.get_job_sample_xpath_data, meta={'job_urls': job_urls[1:5]})

    def get_job_sample_xpath_data(self, response):
        data = self.get_xpath_content_data(response)
        data += response.meta.setdefault('data', [])
        job_urls = response.meta['job_urls']
        if len(job_urls) == 0:
            # map_xpath = module(self.mismatch_attributes, data)
            map_xpath = XpathMapping(data, self.mismatch_attributes).get_xpath_mapping()

            job_selectors = self.context['selectors'].setdefault('job_selectors', {})
            for attribute, xpath in map_xpath.items():
                job_selectors[MAPPING_NUM_LABEL[attribute]] = xpath

            self.context['is_finished'] = True

            self.save_context()
        else:
            yield Request(url=job_urls[0], callback=self.get_job_sample_xpath_data,
                          meta={'data': data, 'job_urls': job_urls[1:]})

    def save_context(self):
        with open(get_context_file(self.domain), mode='w', encoding='utf8') as f:
            json.dump(self.context, f)
            f.close()

    @staticmethod
    def get_xpath_content_data(response):
        tree = etree.HTML(response.body.decode('utf8'))
        data = []

        for node in tree.xpath('//head | //style | //script | //footer | //nav | //select | //form | //table'):
            node.getparent().remove(node)

        for node in tree.iter():
            if node.text is not None:
                data.append([node.getroottree().getpath(node), node.text])

        return data
