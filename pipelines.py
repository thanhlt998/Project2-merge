import pymongo
import time


class MongoPipeline(object):
    start_time = None
    client = None
    no_items_added = 0
    db = None

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.no_items_added = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION')
        )

    def open_spider(self, spider):
        print(self.mongo_uri, self.mongo_db, self.mongo_collection)
        self.start_time = time.localtime()
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()
        print("Begin time: ", time.strftime("%H:%M:%S", self.start_time))
        print("End time: ", time.strftime("%H:%M:%S", time.localtime()))
        print("Added ", self.no_items_added, 'items')

    def process_item(self, item, spider):
        if type(item) is dict:
            self.db[self.mongo_collection].insert_one(item)
            self.no_items_added += 1
        return item
