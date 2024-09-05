# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import openpyxl
import json

class KohaJsonWriterPipeline:
    def __init__(self):
        self.items = []
    
    def open_spider(self, spider):
        # Çıktı dosyasını açın
        self.file = open('koha_library.json', 'w', encoding='utf-8')
        self.file.write('[\n')  # JSON dizisinin başlangıcı

    def close_spider(self, spider):
        # Dosyayı kapatırken dizinin sonuna kapama köşeli parantez ekleyin
        if self.items:
            # İlk öğeyi ekle
            self.file.write(json.dumps(self.items[0], ensure_ascii=False))
            # Diğer öğeleri ekle
            for item in self.items[1:]:
                self.file.write(',\n')
                self.file.write(json.dumps(item, ensure_ascii=False))
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        # Item'ı JSON formatında bir listeye ekleyin
        self.items.append(dict(item))
        return item


class BooksPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        varMi = adapter["Book_Author"].find(",")
        if varMi > 0:
            yazar = adapter["Book_Author"].split(",")
            adapter["Book_Author"] = f"{yazar[1]} {yazar[0]}"

        adapter["Book_Page"] = f"{adapter["Book_Page"]} sayfa"
        return item
    
class ExcelPipeline:
    def open_spider(self, spider):
        # Correct the class name to `Workbook` from `workbook`
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.sheet.title = "Books"
        self.sheet.append(["Book_isbn",
                          "Book_Name",
                          "Book_Author",
                          "Book_Publisher",
                          "Book_Publish_Date",
                          "Book_Page",
                          "Book_Height",
                          "Book_url",])

    def process_item(self, item, spider):
        self.sheet.append([item.get("Book_isbn"),
                           item.get("Book_Name"),
                           item.get("Bookk_Author"),
                           item.get("Book_Publisher"),
                           item.get("Book_Publish_Date"),
                           item.get("Book_Page"),
                           item.get("Book_Height"),
                           item.get("Book_url")])

    def close_spider(self, spider):
        self.workbook.save("BOOKLİBRARY.xlsx")
