import scrapy
from scrapy.crawler import CrawlerProcess

# from nadir.nadir.items import NadirItem
from nadir.items import NadirItem as nadir_item
from nadir.items import KohaItem 
# from koha.koha.spiders.kohas import KohaSpider
# from koha.koha.items import KohaItem
import json
import subprocess
from scrapy import Request


class NadirKitap(scrapy.Spider):
    name = "nadir"

    def __init__(self, koli="0", *args, **kwargs):
        super(NadirKitap, self).__init__(*args, **kwargs)
        self.koli = koli
        self.bulunamayan_isbnler = []

    def start_requests(self):
        path = r"C:\Users\yusuf\OneDrive\Masaüstü\Kütüphane Kayıt\nadir\nadir.json".replace(
            "\\", "/"
        )
        with open(path, "r", encoding="utf-8") as file:
            isbnList = json.load(file)

        print(isbnList)
        for isbn in isbnList:
            yield scrapy.Request(
                url=f"https://www.nadirkitap.com/kitapara.php?ara=aramayap&ref=detayliara&satici=0&tip=kitap&kitap_Adi=&kategori=all&yazar=&yayin_Evi=&ceviren=&yayin_Yeri=&saticisec=all&dil=0&isbn={isbn}&eskiyeni=0&tarih1=&tarih2=&fiyat1=&fiyat2=&cilt=0&siralama=fiyatartan",
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "isbn": isbn,
                    "koli": self.koli,
                },
                callback=self.parse_links,
            )

    def parse_links(self, response):
        isbn = response.meta.get("isbn")
        koli = response.meta.get("koli")
        links = response.css("h4.break-work a::attr(href)").getall()
        try:
            var = links[0]
        except IndexError:
            links = None
        if links is not None:
            for link in links:
                if link is not None:
                    yield scrapy.Request(
                        url=link,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "koli": koli,
                            "link": link,
                        },
                        callback=self.parse_product,
                    )
                    break

        elif links is None:
            self.bulunamayan_isbnler.append(isbn)

    def parse_product(self, response):
        item = nadir_item()
        item["link"] = response.meta.get("link")
        koli = response.meta.get("koli")
        item["Book_Name"] = response.css("h1.a18::text").get()
        item["Book_Author"] = response.css("p.a14 a::text").get()
        item["Book_Publisher"] = response.xpath(
            "/html/body/div[3]/div/div[1]/div[2]/div[2]/div/ul[1]/li[10]/a[1]/text()"
        ).get()
        item["Book_Publish_Date"] = response.xpath(
            "/html/body/div[3]/div/div[1]/div[2]/div[2]/div/ul[1]/li[10]/a[2]/text()"
        ).get()

        try:
            aciklama = response.css("div.panel-body::text").get()
            aciklama = aciklama.split("cm")[0]
            sayfa = aciklama.split(". ")[0]
            size = aciklama.split(". ")[1].split("x")
            height = size[1]
            width = size[0]

            height = height + " cm" if "." in height else height + ".00 cm"
            width = width + " cm" if "." in width else width + ".00 cm"
        except:
            sayfa = "HATA"
            height = "HATA"
            width = "HATA"

        item["Book_Page"] = sayfa
        item["Book_Height"] = height
        item["Book_Width"] = width

        item["Koli"] = koli
        return item

    def closed(self, reason):
        if len(self.bulunamayan_isbnler) > 0:
            url = r"C:\Users\yusuf\OneDrive\Masaüstü\Kütüphane Kayıt\koha\koha\koha.json".replace(
                "\\", "/"
            )
            with open(url, "w", encoding="utf-8") as file:
                json.dump(self.bulunamayan_isbnler, file, ensure_ascii=False, indent=4)

            print("KOHA Çalışıyor....  ")
            process = CrawlerProcess()
            process.crawl(
                KohaSpider
            )  # Koha projesindeki spiderı alttaki KohaSpider Class yapısıyla buraya ekledim. Düz mantık burda direkt olarak başlatıyoruz.
            process.start()


class KohaSpider(scrapy.Spider):
    name = "koha"
    
    custom_settings = {'ITEM_PIPELINES': {'nadir.pipelines.KohaJsonWriterPipeline': 300}}
    print("KOHAAAAAA\n\n\n\n")
    path = (
        r"C:\Users\yusuf\OneDrive\Masaüstü\Kütüphane Kayıt\koha\koha\koha.json".replace(
            "\\", "/"
        )
    )
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
                    "playwright": True,
                    "playwright_include_page": True,
                    "isbn": isbn,
                },
                callback=self.parse_number,
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
                    "playwright": True,
                    "playwright_include_page": True,
                    "isbn": isbn,
                    "url": url_kitap,
                },
                callback=self.parse_veri,
            )
        else:
            veri = KohaItem()
            veri["Koli"] = self.koli
            veri["Book_isbn"] = response.meta.get("isbn")
            veri["Book_url"] = response.meta.get("url", response.url)

            veri["Book_Name"] = (
                response.css("h2.title::text").get(default="BİLGİ YOK").strip()
            )

            yazar = response.css('span[property="name"]::text').get()
            if yazar is None:
                veri["Book_Author"] = (
                    response.css("span.title_resp_stmt::text")
                    .get(default="BİLGİ YOK")
                    .strip()
                )
            else:
                veri["Book_Author"] = yazar.strip()

            veri["Book_Publisher"] = (
                response.css("span.publisher_name a::text")
                .get(default="BİLGİ YOK")
                .strip()
            )
            veri["Book_Publish_Date"] = (
                response.css("span.publisher_date::text")
                .get(default="BİLGİ YOK")
                .strip()
            )

            description = response.css('span[property="description"]::text').get(
                default="BİLGİ YOK"
            )
            if description != "BİLGİ YOK":
                parts = description.split("s.")
                sayfa = parts[0].strip()
                height = (
                    parts[2].strip()
                    if len(parts) > 2 and "res" in description
                    else parts[1].strip()
                )
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

        veri["Book_Name"] = (
            response.css("h2.title::text").get(default="BİLGİ YOK").strip()
        )

        yazar = response.css('span[property="name"]::text').get()
        if yazar is None:
            veri["Book_Author"] = (
                response.css("span.title_resp_stmt::text")
                .get(default="BİLGİ YOK")
                .strip()
            )
        else:
            veri["Book_Author"] = yazar.strip()

        veri["Book_Publisher"] = (
            response.css("span.publisher_name a::text").get(default="BİLGİ YOK").strip()
        )
        veri["Book_Publish_Date"] = (
            response.css("span.publisher_date::text").get(default="BİLGİ YOK").strip()
        )

        description = response.css('span[property="description"]::text').get(
            default="BİLGİ YOK"
        )
        if description != "BİLGİ YOK":
            parts = description.split("s.")
            sayfa = parts[0].strip()
            height = (
                parts[2].strip()
                if len(parts) > 2 and "res" in description
                else parts[1].strip()
            )
            veri["Book_Page"] = sayfa
            veri["Book_Height"] = height
        else:
            veri["Book_Page"] = "BİLGİ YOK"
            veri["Book_Height"] = "BİLGİ YOK"
        yield veri
