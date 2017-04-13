# coding: utf-8

from leancloud import Engine
from leancloud import LeanEngineError

from app import app

from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from multiprocessing import Process
from spiders.QuotesSpider import QuotesSpider


engine = Engine(app)


class CrawlerScript(Process):
    def __init__(self, spider):
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider.__class__, settings)
        self.crawler.signals.connect(reactor.stop, signals.spider_closed)
        self.spider = spider

    def run(self):
        self.crawler.crawl(self.spider)
        reactor.run()


@engine.define
def hello(**params):
    if 'name' in params:
        return 'Hello, {}!'.format(params['name'])
    else:
        return 'Hello, LeanCloud!'


@engine.define
def crawl(**params):
    spider = QuotesSpider()
    crawler = CrawlerScript(spider)
    crawler.start()
    crawler.join()


@engine.before_save('Todo')
def before_todo_save(todo):
    content = todo.get('content')
    if not content:
        raise LeanEngineError('内容不能为空')
    if len(content) >= 240:
        todo.set('content', content[:240] + ' ...')
