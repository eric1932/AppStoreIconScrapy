from typing import List

import scrapy
from itemloaders import ItemLoader
from scrapy.http import HtmlResponse

from appstoreiconscrapy.items import AppItem
from util_types import Region, Chart
from utils import get_top_ranking_apps


class AppSpider(scrapy.Spider):
    name = "apps"

    def start_requests(self):
        """

        :return:
        """

        ''' unused
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
        '''

        # default heuristic discovery
        # for each_query in [
        #     get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_FREE),
        #     get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_PAID),
        #     get_top_ranking_apps(region=Region.US, chart=Chart.TOP_FREE),
        #     get_top_ranking_apps(region=Region.US, chart=Chart.TOP_PAID),
        # ]:
        #     for each_result in each_query:
        #         yield scrapy.Request(url=each_result.url, callback=self.parse)

        # terminated top-100 ranking discovery
        for each_query in [
            # test
            # get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_FREE, result_limit=1),

            get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_FREE, result_limit=200),
            get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_PAID, result_limit=50),
            get_top_ranking_apps(region=Region.US, chart=Chart.TOP_FREE, result_limit=200),
            get_top_ranking_apps(region=Region.US, chart=Chart.TOP_PAID, result_limit=200),
        ]:
            for each_result in each_query:
                yield scrapy.Request(url=each_result.url, callback=self.parse_terminate)

    def parse_terminate(self, response: HtmlResponse, **kwargs):
        loader = ItemLoader(item=AppItem(), selector=response)
        loader.add_value("bundle_id", response.url, re=r"(id[0-9]+)")
        loader.add_css("name", "header.product-header.app-header > h1::text")
        loader.add_css("icon_urls", "div.l-row > div > picture.we-artwork > source::attr(srcset)")
        loader.add_css("version", "div.l-row > p.l-column::text", re=r"(?:Version|版本)\s+(.*)")

        yield loader.load_item()

    def parse(self, response: HtmlResponse, **kwargs):
        self.parse_terminate(response)

        ref_links: List[str] = response.css("a.we-lockup::attr(href)").getall()
        for x in ref_links:
            yield scrapy.Request(url=x, callback=self.parse)
