# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import os
# useful for handling different item types with a single interface
import re
from io import BytesIO
from typing import Tuple
from urllib.request import urlopen

import pymongo
from PIL import Image
from itemadapter import ItemAdapter

from appstoreiconscrapy.settings import IMG_DOWNLOAD_PATH


class TutorialPipeline:
    def process_item(self, item, spider):
        return item


class MongoPipeline:
    collection_name = 'app_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        self.db[self.collection_name].update_one({
            'bundle_id': item['bundle_id'],
            'version': item.get('version', None),  # in case of null version
        }, {
            '$set': ItemAdapter(item).asdict(),
        }, upsert=True)
        return item


class DownloadImagePipeline:
    reg_size_dot = re.compile(r"[0-9]+x0w\.")
    reg_extension = re.compile(r"(jpg|jpeg|png|webp)$")
    reg_url_tail = re.compile(r"[0-9]+x0w\.(jpg|jpeg|png|webp)$")
    upper_size = "102400x0w."
    target_extensions = [
        "png",
        "webp",
    ]

    def process_item(self, item, spider):
        img_url_orig = item['icon_urls'][0][:-3]
        img_bin_max: bytes = urlopen(re.sub(self.reg_size_dot, self.upper_size, img_url_orig)).read()
        img_pixel_size: Tuple[int, int] = Image.open(BytesIO(img_bin_max)).size
        out_size = f"{img_pixel_size[0]}x0w"

        down_list = []
        for each_ext in self.target_extensions:
            url = re.sub(self.reg_url_tail, f"{out_size}.{each_ext}", img_url_orig)
            down_list.append((f"{item['name']}_{item['version']}_{out_size}.{each_ext}", url))

        # download down_list
        # print(down_list)
        for each_filename, each_down_url in down_list:
            with open(os.path.join(IMG_DOWNLOAD_PATH, each_filename), 'wb') as f:
                f.write(urlopen(each_down_url).read())

        return item
