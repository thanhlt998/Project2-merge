from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging

from support_crawler import SchemaCrawler, XpathCrawler
from crawler import Crawler
from utils.model import NaiveBayesModel, DecisionTreeModel, LogisticRegressionModel
from utils.preprocess import FeaturesTransformer
from setting import SCRAPY_CONFIG, get_domain, WEB_LIST


@defer.inlineCallbacks
def crawl():
    # for web in WEB_LIST:
    #     start_url = web['start_url']
    #     job_url_selector = web['job_url']
    #     next_page_selector = web['next_page']
    #     domain = get_domain(start_url)
    yield runner.crawl(SchemaCrawler, name="schema_crawler", start_url=start_url, job_url=job_url_selector,
                            next_page=next_page_selector, domain=domain)
    yield runner.crawl(XpathCrawler, name="xpath_crawler", domain=domain)

    yield runner.crawl(Crawler, name="crawler", domain=domain)
    reactor.stop()


if __name__ == '__main__':

    # # setting = get_project_settings()
    # # for key, config in SCRAPY_CONFIG.items():
    # #     setting[key] = config
    # # configure_logging()
    # # runner = CrawlerRunner(setting)
    # # crawl()
    # # reactor.run()
    start_url = "https://careerbuilder.vn/viec-lam/tat-ca-viec-lam-vi.html"
    job_url_selector = "//div[contains(@class,'gird_standard')]//dd[contains(@class, 'brief')]/span[@class='jobtitle']/h3[@class='job']/a"
    next_page_selector = "//div[@class='paginationTwoStatus']/a[@class='right']"
    domain = get_domain(start_url)
    setting = get_project_settings()

    for key, config in SCRAPY_CONFIG.items():
        setting[key] = config

    configure_logging()
    runner = CrawlerRunner(setting)
    crawl()
    reactor.run()
