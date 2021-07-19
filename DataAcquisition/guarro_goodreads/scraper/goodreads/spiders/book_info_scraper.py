import scrapy
from scrapy_splash import SplashRequest
# import shadow_useragent
from string import Template

from SQLiteHelper import SQLiteHelper

import logging
import pathlib

import base64

logger = logging.getLogger('book_info_scraper')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

custom_log_path = pathlib.Path().absolute() / "Log" / "custom.log"
print(custom_log_path)
file_handler = logging.FileHandler(custom_log_path, 'a', 'utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def escapeLuaChars(s):
    return s.translate(str.maketrans({"\\": r"\\",
                                        "'":  r"\'",
                                        "\"":  r"\"",
                                        "'":  r"\'"}))

class BookInfoScraperSpider(scrapy.Spider):
    name = 'book_info_scraper'
    allowed_domains = ['www.goodreads.com']
    url = 'https://www.goodreads.com/search?utf8=%E2%9C%93&query='

    template = Template("""
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(0.5))

            input_box = assert(splash:select('#search_query_main'))
            input_box:focus()
            input_box:send_text("$searchquery")
            input_box:send_keys("<Enter>")
            assert(splash:wait(2)) 

            did_enter = false
            
            if (not (splash:evaljs("document.querySelectorAll('table.tableList > tbody > tr:nth-of-type(1) a.bookTitle')[0]") == nil)) then
                did_enter = true
                
                href = splash:evaljs("document.querySelectorAll('table.tableList > tbody > tr:nth-of-type(1) a.bookTitle')[0].href")
                assert(splash:go(href))
                assert(splash:wait(2))
                
                if not splash:evaljs("document.querySelectorAll('div#description a')[0]") == nil then
                    splash:runjs("document.querySelectorAll('div#description a')[0].click()")
                end
            end

            assert(splash:wait(0.7))
            return {
                html = splash:html()
            }
        end
    """)

    def __init__(self):
        self.lastExecScript = ""
        self.download_delay = 2
        self.sqlite = SQLiteHelper()
        self.count = 0
        print("ayyy:", self.name)

    def start_requests(self):
        for i in range(5):
            # access db to fetch a book title / author
            rec = self.sqlite.getNext()
            print("yung rec ", rec)
            book_id = rec[0]

            book_title = rec[2].replace('\r\n', '\n').replace('\n', '\r').replace('\r', ' ')
            author_lname = rec[1]
            if author_lname:
                author_lname = rec[1].split(',')[0]

            search_q = book_title + ' ' + author_lname if author_lname else book_title 
            search_q = escapeLuaChars(search_q)
            # print('author_lname:', author_lname)

            print("yung sq: " + search_q)
            self.logger.info("scraping goodreads info with search query: " + search_q)
            script = self.template.substitute(searchquery = search_q)
            self.lastExecScript = script
            
            # self.lastExecScript = script
            yield SplashRequest(url=self.url, callback=self.parse, endpoint="execute", 
                args={
                    'lua_source': script
                },
                meta={'book_id': book_id, 'Book Title': book_title},
                errback = self.logerror,
                dont_filter = True
            )


    def parse(self, response):
        # to save a screenshot: self.saveImageForDebug(response.data['img'])
        # get goodreads_rating, num_ratings, goodreads_blurb, num_pages
        book = response.xpath("//div[@id='metacol']")
        genre_box = response.xpath("//div[@class='stacked']//div[@class='bigBoxBody']/div//div[contains(@class, 'elementList ')]")
        if book:
            genres = genre_box.xpath(".//div[@class='left']/a/text()").getall()
            num_votes = genre_box.xpath(".//div[@class='right']/a/text()").getall()
            self.count += 1
            yield {
                'goodreads_rating': book.xpath(".//span[@itemprop='ratingValue']/text()").get(),
                'num_ratings': book.xpath(".//a[@class='gr-hyperlink']/meta/@content").get(),
                'goodreads_blurb': book.xpath("string(.//div[@id='description']/span[2])").get(),
                'num_pages': book.xpath(".//span[@itemprop='numberOfPages']/text()").get(),
                'published_info': book.xpath(".//div[@id='details']/div[@class='row'][last()]/text()").get(),
                'title_gr': book.xpath("//div[@id='metacol']/h1[@id='bookTitle']/text()").get(),
                'author_gr': book.xpath("//div[@id='metacol']//span[@itemprop='name']/text()").get(),
                'pg_id': response.meta['book_id'],
                'genres': genres,
                'num_votes': num_votes
            }
        else:
            self.sqlite.mark_no_gr_found(response.meta['book_id'])
            # self.saveImageForDebug(response.data['img'])
            self.logger.error("NO BOOK FOUND")

        rec = self.sqlite.getNext()
        if rec:
            # access db to fetch a book title / author
            print("yung rec ", rec)
            book_id = rec[0]

            book_title = rec[2].replace('\r\n', '\n').replace('\n', '\r').replace('\r', ' ')
            author_lname = rec[1]
            if author_lname:
                author_lname = rec[1].split(',')[0]

            search_q = book_title + ' ' + author_lname if author_lname else book_title 
            search_q = escapeLuaChars(search_q)

            self.logger.info("scraping goodreads info with search query: " + search_q)
            script = self.template.substitute(searchquery = search_q)
            self.lastExecScript = script
            
            # self.lastExecScript = script
            yield SplashRequest(url=self.url, callback=self.parse, endpoint="execute", 
                args={
                    'lua_source': script
                },
                meta={'book_id': book_id, 'Book Title': book_title},
                errback = self.logerror,
                dont_filter = True
            )



    def logerror(self, failure):
        self.logger.error("FAILED WITH THIS SCRIPT: " + self.lastExecScript)
        rec = self.sqlite.getNext()
        if rec:
            # access db to fetch a book title / author
            print("yung rec ", rec)
            book_id = rec[0]

            book_title = rec[2].replace('\r\n', '\n').replace('\n', '\r').replace('\r', ' ')
            author_lname = rec[1]
            if author_lname:
                author_lname = rec[1].split(',')[0]

            search_q = book_title + ' ' + author_lname if author_lname else book_title 
            search_q = escapeLuaChars(search_q)

            self.logger.info("scraping goodreads info with search query: " + search_q)
            script = self.template.substitute(searchquery = search_q)
            self.lastExecScript = script
            
            # self.lastExecScript = script
            yield SplashRequest(url=self.url, callback=self.parse, endpoint="execute", 
                args={
                    'lua_source': script
                },
                meta={'book_id': book_id, 'Book Title': book_title},
                errback = self.logerror,
                dont_filter = True
            )

    # def saveImageForDebug(self, img):
    #     imgdata = base64.b64decode(img)
    #     filename = './Screenshots/' + self.name + '_error.png'
    #     with open(filename, 'wb') as f:
    #         f.write(imgdata)
    #         self.logger.info("saved screenshot of failure")

    def closed(self, reason):
        self.logger.info("closing after finding info for " + str(self.count) + " books")
        self.logger.info("last script executed: " + self.lastExecScript)
        self.logger.info("closed with reason: " + reason)



    # def navigate_to_book_page(self, response):
    #     top_search_result = response.xpath("(//table[@class='tableList']/tbody/tr)[1]").getall()
    #     link = top_search_result.xpath("//a[@class='bookTitle']/@href").get()

    #     full_link = 'https://www.goodreads.com' + link

    #     if (link):
    #         yield SplashRequest(url=full_link, callback = self.parse, endpoint="execute", 
    #             args={
    #                 'lua_source': 
    #             })


    # def makeLogger(self, name):
        # logger = logging.getLogger(name)
        # logger.setLevel(logging.INFO)

        # formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

        # custom_log_path = pathlib.Path().absolute() / "Log" / "custom.log"
        # file_handler = logging.FileHandler(custom_log_path, 'a', 'utf-8')
        # file_handler.setFormatter(formatter)

        # logger.addHandler(file_handler)
        # return logger