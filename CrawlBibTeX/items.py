# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlbibtexItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BibTeXScriptItem(scrapy.Item):
    SeqNum = scrapy.Field()
    BibTeX = scrapy.Field()