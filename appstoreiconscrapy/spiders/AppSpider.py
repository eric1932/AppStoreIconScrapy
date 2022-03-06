import os
import re
from enum import Enum
from io import BytesIO
from typing import List, Dict, Any, Tuple
from urllib.request import urlopen

import scrapy
from PIL import Image
from itemloaders import ItemLoader
from scrapy.http import HtmlResponse

from appstoreiconscrapy.items import AppItem
from appstoreiconscrapy.settings import IMG_DOWNLOAD_PATH
from util_types import Region, Chart, RankingResult
from utils import get_top_ranking_apps


class AppSpider(scrapy.Spider):
    name = "apps"

    # icon download related
    reg_size_dot = re.compile(r"[0-9]+x0w\.")
    reg_extension = re.compile(r"(jpg|jpeg|png|webp)$")
    reg_url_tail = re.compile(r"[0-9]+x0w\.(jpg|jpeg|png|webp)$")
    upper_size = "102400x0w."
    target_extensions = [
        "png",
        "webp",
    ]

    class ParseOptions(str, Enum):
        NO_DISCOVER = 'terminate'
        DOWNLOAD_ICON = 'download_icon'

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
            # Custom
            [
                RankingResult(url="https://apps.apple.com/us/app/chowbus-asian-food-delivery/id1053160529"),  # Chowbus
            ],

            # test
            # get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_FREE, result_limit=1),

            # get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_FREE, result_limit=200),
            # get_top_ranking_apps(region=Region.CN, chart=Chart.TOP_PAID, result_limit=50),
            get_top_ranking_apps(region=Region.US, chart=Chart.TOP_FREE, result_limit=200),
            get_top_ranking_apps(region=Region.US, chart=Chart.TOP_PAID, result_limit=200),
        ]:
            for each_result in each_query:
                yield scrapy.Request(url=each_result.url, callback=self.parse, cb_kwargs={
                    # self.ParseOptions.NO_DISCOVER: True,  # default False
                    self.ParseOptions.DOWNLOAD_ICON: True,  # default False
                })

    def parse(self, response: HtmlResponse, **kwargs: Dict[ParseOptions, Any]):
        loader = ItemLoader(item=AppItem(), selector=response)
        loader.add_value("bundle_id", response.url, re=r"(id[0-9]+)")
        loader.add_css("name", "header.product-header.app-header > h1::text")
        loader.add_css("icon_urls", "div.l-row > div > picture.we-artwork > source::attr(srcset)")
        loader.add_css("version", "div.l-row > p.l-column::text", re=r"(?:Version|版本)\s+(.*)")
        item = loader.load_item()
        yield item

        if not kwargs.get(self.ParseOptions.NO_DISCOVER, False):
            ref_links: List[str] = response.css("a.we-lockup::attr(href)").getall()
            for x in ref_links:
                yield scrapy.Request(url=x, callback=self.parse)

        if kwargs.get(self.ParseOptions.DOWNLOAD_ICON, False):
            img_url_orig = item['icon_urls'][0][:-3]
            img_bin_max: bytes = urlopen(re.sub(self.reg_size_dot, self.upper_size, img_url_orig)).read()
            img_pixel_size: Tuple[int, int] = Image.open(BytesIO(img_bin_max)).size
            out_size = f"{img_pixel_size[0]}x0w"

            for each_ext in self.target_extensions:
                url = re.sub(self.reg_url_tail, f"{out_size}.{each_ext}", img_url_orig)
                filename = f"{item['name']}_{item['version']}_{out_size}.{each_ext}"
                with open(os.path.join(IMG_DOWNLOAD_PATH, filename), 'wb') as f:
                    f.write(urlopen(url).read())
