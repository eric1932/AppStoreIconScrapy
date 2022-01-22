# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AppItem(scrapy.Item):
    name = scrapy.Field()
    version = scrapy.Field()
    icon_urls = scrapy.Field()
