import json
import requests
import subprocess

bulunamayan_isbnler = []
def openLibraryKayit(koli):
    
    with open("open_Library_gönderilen.json","r",encoding="utf-8") as file:
        isbnList = json.load(file)
    for isbn in isbnList:
        hata = 0
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        headers = ["ISBN", "Koli No", "Book Name", "Book Author", "Book Publisher", "Book Publish Date", "Book Page"]

        try:
            with open("library.json", "r", encoding="utf-8") as file:
                try:
                    veri = json.load(file)
                except json.JSONDecodeError:
                    veri = {"books": []}
        except:
            veri = {"books": []}
        try:
            result = requests.get(url)
            veri_data = result.json()
        except requests.exceptions.JSONDecodeError:
            hata = 1

        if hata == 0:
            try:
                book_name = veri_data["title"]
            except KeyError:
                book_name = "Kitap İsmi Bulunamadı"
                hata += 1
            try:
                book_publisher = veri_data.get("publishers", ["Kitap Yayınevi Bilgisi Bulunamadı"])[0]
            except KeyError:
                book_publisher = "Kitap Yayınevi Bilgisi Bulunamadı"
                hata += 1

            try:    
                book_page = veri_data.get("number_of_pages", "Kitap Sayfası Bilgisi Bulunamadı")
            except KeyError:
                book_page = "Kitap Sayfası Bilgisi Bulunamadı"
                hata += 1

            try:
                book_publish_date = veri_data.get("publish_date", "Kitap Yayın Tarihi Bilgisi Bulunamadı")
            except KeyError:
                book_publish_date = "Kitap Yayın Tarihi Bilgisi Bulunamadı"
                hata += 1

            try:
                book_author_key = veri_data["authors"][0]["key"]
                book_author_url = f"https://openlibrary.org{book_author_key}.json"
                result = requests.get(book_author_url)
                result = result.json()
                book_author = result["name"]
            except KeyError:
                book_author = "Yazar Bilgisi Bulunamadı"
                hata += 1

            if isinstance(book_author, list):
                book_author = book_author[0]
            if isinstance(book_name, list):
                book_name = book_name[0]
            if isinstance(book_publisher, list):
                book_publisher = book_publisher[0]
            if isinstance(book_publish_date, list):
                book_publish_date = book_publish_date[0]
            if isinstance(book_page, list):
                book_page = book_page[0]

            if hata < 3:
                book_info = dict(zip(headers, [isbn, koli, book_name, book_author, book_publisher, book_publish_date, book_page]))
                veri["books"].append(book_info)

                with open("library.json", "w", encoding="utf-8") as file:
                    json.dump(veri, file, indent=4, ensure_ascii=False)

                print(f"Open Library: {isbn} numaralı kitap KAYDEDİLDİ")
            else:
                bulunamayan_isbnler.append(isbn)
        else:
            bulunamayan_isbnler.append(isbn)

        

    if len(bulunamayan_isbnler) > 0:
        with open("nadir/nadir.json", "w", encoding="utf-8") as file:
            json.dump(bulunamayan_isbnler, file, indent=4, ensure_ascii=False)

        run_scrapy()

def run_scrapy():
    subprocess.run("cd nadir && scrapy crawl nadir", shell=True)

if __name__ == "__main__":
    # Örnek bir çağrı
    openLibraryKayit(input("Barkod No:"), input("Koli No:"))