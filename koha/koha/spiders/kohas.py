import scrapy
from scrapy import Request
from koha.koha.items import KohaItem
import json

class KohaSpider(scrapy.Spider):
    name = "koha"
    print("KOHAAAAAA\n\n\n\n")
    path = r"C:\Users\yusuf\OneDrive\Masaüstü\Kütüphane Kayıt\koha\koha\koha.json".replace("\\","/")
    with open(path, "r", encoding="utf-8") as file:
        isbnList = json.load(file)
    
    def __init__(self, koli=None, *args, **kwargs):
        super(KohaSpider, self).__init__(*args, **kwargs)
        self.koli = koli
        self.bulunamayan_isbnler = []

    def start_requests(self):
        isbnList = self.isbnList 
        for isbn in isbnList:
            url = f"https://koha.ekutuphane.gov.tr/cgi-bin/koha/opac-search.pl?idx=nb&q={isbn}&branch_group_limit=&weight_search=1"
            yield Request(
                url=url,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'isbn': isbn
                },
                callback=self.parse_number
            )

    def parse_number(self, response):
        isbn = response.meta.get("isbn")

        url_kitap = response.css("div.title_summary a::attr(href)").get()
        if url_kitap:
            domain = "https://koha.ekutuphane.gov.tr"
            url_kitap = domain + url_kitap

            yield Request(
                url=url_kitap,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'isbn': isbn,
                    "url": url_kitap
                },
                callback=self.parse_veri
            )
        else:
            veri = KohaItem()
            veri["Koli"] = self.koli
            veri["Book_isbn"] = response.meta.get("isbn")
            veri["Book_url"] = response.meta.get("url", response.url)
            
            veri["Book_Name"] = response.css("h2.title::text").get(default="BİLGİ YOK").strip()
            
            yazar = response.css('span[property="name"]::text').get()
            if yazar is None:
                veri["Book_Author"] = response.css("span.title_resp_stmt::text").get(default="BİLGİ YOK").strip()
            else:
                veri["Book_Author"] = yazar.strip()
            
            veri["Book_Publisher"] = response.css("span.publisher_name a::text").get(default="BİLGİ YOK").strip()
            veri["Book_Publish_Date"] = response.css("span.publisher_date::text").get(default="BİLGİ YOK").strip()
            
            description = response.css('span[property="description"]::text').get(default="BİLGİ YOK")
            if description != "BİLGİ YOK":
                parts = description.split("s.")
                sayfa = parts[0].strip()
                height = parts[2].strip() if len(parts) > 2 and "res" in description else parts[1].strip()
                veri["Book_Page"] = sayfa
                veri["Book_Height"] = height
            else:
                veri["Book_Page"] = "BİLGİ YOK"
                veri["Book_Height"] = "BİLGİ YOK"
            yield veri

    def parse_veri(self, response):
        veri = KohaItem()
        veri["Book_isbn"] = response.meta.get("isbn")
        veri["Book_url"] = response.meta.get("url", response.url)
        
        veri["Book_Name"] = response.css("h2.title::text").get(default="BİLGİ YOK").strip()
        
        yazar = response.css('span[property="name"]::text').get()
        if yazar is None:
            veri["Book_Author"] = response.css("span.title_resp_stmt::text").get(default="BİLGİ YOK").strip()
        else:
            veri["Book_Author"] = yazar.strip()
        
        veri["Book_Publisher"] = response.css("span.publisher_name a::text").get(default="BİLGİ YOK").strip()
        veri["Book_Publish_Date"] = response.css("span.publisher_date::text").get(default="BİLGİ YOK").strip()
        
        description = response.css('span[property="description"]::text').get(default="BİLGİ YOK")
        if description != "BİLGİ YOK":
            parts = description.split("s.")
            sayfa = parts[0].strip()
            height = parts[2].strip() if len(parts) > 2 and "res" in description else parts[1].strip()
            veri["Book_Page"] = sayfa
            veri["Book_Height"] = height
        else:
            veri["Book_Page"] = "BİLGİ YOK"
            veri["Book_Height"] = "BİLGİ YOK"
        yield veri
