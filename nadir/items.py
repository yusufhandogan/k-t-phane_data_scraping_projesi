# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NadirItem(scrapy.Item):
    link = scrapy.Field()
    Book_Name = scrapy.Field()
    Book_Author = scrapy.Field()
    Book_Publisher = scrapy.Field()
    Book_Publish_Date = scrapy.Field()
    Book_Page = scrapy.Field()
    Book_Height = scrapy.Field()
    Book_Width = scrapy.Field()
    Koli = scrapy.Field()

class KohaItem(scrapy.Item):
    Book_isbn = scrapy.Field()
    Book_Name = scrapy.Field()
    Book_Author = scrapy.Field()
    Book_Publisher = scrapy.Field()
    Book_Publish_Date = scrapy.Field()
    Book_Page = scrapy.Field()
    Book_Height = scrapy.Field()
    Book_url = scrapy.Field()
    Koli = scrapy.Field()