# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CrawlbibtexPipeline:
    def process_item(self, item, spider):
        if item['BibTeX']:
            return item
        else:
            return DropItem('Miss BibTex!')


class FilesavebibtexPipeline(object):
    def __init__(self, filename):
        self.file = open(filename, 'wb')
        self.item_list = list()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(filename=crawler.settings.get('BIBTEX_SAVE_FILENAME'))

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        self.item_list.append(item)

    def close_spider(self, spider):
        self.item_list = sorted(self.item_list, key=lambda x: x['SeqNum'])
        for item in self.item_list:
            self.file.write(item['BibTeX'].encode())
        self.file.close()
