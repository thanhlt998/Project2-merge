from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging

from support_crawler import SchemaCrawler, XpathCrawler
from crawler import Crawler
from utils.model import NaiveBayesModel, DecisionTreeModel, LogisticRegressionModel
from utils.preprocess import FeaturesTransformer
from setting import SCRAPY_CONFIG, get_domain


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SchemaCrawler, name="schema_crawler", start_url=start_url, job_url=job_url_selector,
                       next_page=next_page_selector, domain=domain)
    yield runner.crawl(XpathCrawler, name="xpath_crawler", domain="domain")

    yield runner.crawl(Crawler, name="crawler", domain=domain)
    reactor.stop()


if __name__ == '__main__':
    start_url = 'https://www.topcv.vn/viec-lam/moi-nhat.html?utm_source=click-search-job&utm_medium=page-job&utm_campaign=tracking-job'
    job_url_selector = "//*[@id='box-job-result']/div[1]/div/div/div[2]/h4/a"
    next_page_selector = "//*[@id='box-job-result']/div[2]/ul/li[last()]/a"
    domain = get_domain(start_url)
    setting = get_project_settings()

    for key, config in SCRAPY_CONFIG.items():
        setting[key] = config

    configure_logging()
    runner = CrawlerRunner(setting)
    crawl()
    reactor.run()
