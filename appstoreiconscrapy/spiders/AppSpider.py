from typing import List, Union

import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import SelectorList

from appstoreiconscrapy.items import AppItem


class AppSpider(scrapy.Spider):
    name = "apps"

    def start_requests(self):
        urls = [
            'https://apps.apple.com/us/app/id387682726',  # Taobao
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        # page = response.url.split("/")[-2]
        # filename = f'quotes-{page}.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log(f'Saved file {filename}')

        url = response.url
        # self.log(f"{url}")

        title: str = response.css("title::text").re(r"\s+\u200e?(.*)\s+on the App[\s|\xa0]Store")[0]
        # self.log(f'{title}')

        picture_urls: SelectorList = response.css("div.l-row > div > picture.we-artwork > source::attr(srcset)")
        # self.log(picture_urls.getall())

        version: Union[str, None] = x[1] if (
            x := response.css("div.l-row > p.l-column::text").re(r"(Version|版本)\s+(.*)")
        ) else None
        # self.log(version)

        ref_links: List[str] = response.css("a.we-lockup::attr(href)").getall()
        # self.log(ref_links)

        yield AppItem(
            name=title,
            version=version,
            icon_urls=[x.strip() for x in picture_urls.get().split(',')],
        )

        for x in ref_links:
            yield scrapy.Request(url=x, callback=self.parse)
