from typing import List

import scrapy
from itemloaders import ItemLoader
from scrapy.http import HtmlResponse

from appstoreiconscrapy.items import AppItem


class AppSpider(scrapy.Spider):
    name = "apps"

    def start_requests(self):
        urls = [
            'https://apps.apple.com/us/app/id387682726?l=zh',  # Taobao
            'https://apps.apple.com/us/app/wechat/id414478124?l=zh',  # WeChat
            # # 国区
            'https://apps.apple.com/cn/app/wechat/id414478124?l=zh',  # 微信
            # Test
            # 'https://apps.apple.com/us/app/spam-guard-text-call-block/id1534657013',  # No Version
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        loader = ItemLoader(item=AppItem(), selector=response)
        # loader.add_value("bundle_id", re.search(self.re_bundle_id, response.url))
        loader.add_value("bundle_id", response.url, re=r"(id[0-9]+)")
        loader.add_css("name", "header.product-header.app-header > h1::text")
        loader.add_css("icon_urls", "div.l-row > div > picture.we-artwork > source::attr(srcset)")
        loader.add_css("version", "div.l-row > p.l-column::text", re=r"(?:Version|版本)\s+(.*)")

        ref_links: List[str] = response.css("a.we-lockup::attr(href)").getall()

        yield loader.load_item()

        for x in ref_links:
            yield scrapy.Request(url=x, callback=self.parse)
