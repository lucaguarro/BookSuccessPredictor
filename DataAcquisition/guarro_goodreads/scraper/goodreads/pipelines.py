# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re

from SQLiteHelper import SQLiteHelper

class GoodreadsPipeline:

    def __init__(self, sqlite):
        self.sqlite = sqlite

    @classmethod
    def from_crawler(cls, crawler):
        print("From Crawler")
        # Here, you get whatever value was passed through the "table" parameter
        sqlite = crawler.spider.sqlite

        # Instantiate the pipeline with your table
        return cls(sqlite)

    def open_spider(self, spider):
        print("what it do baby")

    def clean_num_pages(self, num_pages_str):
        return int(re.search(r'\d+', num_pages_str).group(0))

    def clean_num_votes(self, num_votes_str_list):
        num_votes_list = []
        for num_votes_str in num_votes_str_list:
            num_votes_list.append(re.search(r'\d+', num_votes_str).group(0))
        return num_votes_list

    def clean_gr_rating(self, gr_rating):
        return gr_rating.strip()

    def clean_string_data(self, str_data):
        str_data = str_data if str_data else ''
        str_data = str_data.replace('\r\n', '\n').replace('\n', '\r').replace('\r', ' ')
        return str_data

    def process_item(self, item, spider):
        gr_rating = self.clean_gr_rating(item.get('goodreads_rating'))
        num_pages = self.clean_num_pages(item.get('num_pages')) if item.get('num_pages') else None
        goodreads_blurb = self.clean_string_data(item.get('goodreads_blurb'))
        published_info = self.clean_string_data(item.get('published_info'))
        title_gr = self.clean_string_data(item.get('title_gr'))
        author_gr = self.clean_string_data(item.get('author_gr'))

        task = (gr_rating, item.get('num_ratings'), goodreads_blurb, num_pages, published_info, title_gr, author_gr, item.get('pg_id'))
        self.sqlite.updateBook(task)

        if len(item.get('num_votes')):
            num_votes_list = self.clean_num_votes(item.get('num_votes'))
            self.sqlite.genre_multi_insert(item.get('pg_id'), item.get('genres'), num_votes_list)

