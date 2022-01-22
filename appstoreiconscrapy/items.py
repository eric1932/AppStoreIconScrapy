# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


def keep_only_printable(input):
    return ''.join(filter(str.isprintable, input))


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AppItem(scrapy.Item):
    bundle_id = scrapy.Field(
        output_processor=TakeFirst(),
    )
    name = scrapy.Field(
        input_processor=MapCompose(str.strip, keep_only_printable),
        output_processor=TakeFirst(),
    )
    version = scrapy.Field(
        output_processor=TakeFirst(),
    )
    icon_urls = scrapy.Field()
