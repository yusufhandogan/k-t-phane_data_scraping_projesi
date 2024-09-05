import requests
import json
from openlibrary import openLibraryKayit

def googleBook(koli):
    bulunamayan_isbnler =[]
    with open("isbnList.txt", "r", encoding="utf-8") as file:
        noList = file.read().splitlines()

    try:
        with open("library.json", "r", encoding="utf-8") as file:
            try:
                veri = json.load(file)
            except json.JSONDecodeError:
                veri = {"books": []}
    except FileNotFoundError:
        veri = {"books": []}
    for no in noList:
        hata = 0    
        API_KEY = 'AIzaSyDUeWAXXhE-LiTLXFvAX5fEIW4M9PeY3P0'
        ISBN = no
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + ISBN + "&key=" + API_KEY
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            continue

        try:
            new_url = data["items"][0]["selfLink"]
            response = requests.get(new_url).json()
        except:
            hata = 4

        try:
            book_name = response["volumeInfo"]["title"]
        except:
            book_name = "Bilgi Mevcut Değil"
            hata += 1

        try:
            book_author = response["volumeInfo"]["authors"][0]  
        except:
            book_author = "Bilgi Mevcut Değil"
            hata += 1

        try:
            book_publisher = response["volumeInfo"]["publisher"]
        except:
            book_publisher = "Bilgi Mevcut Değil"
            hata += 1

        try:
            book_page = response["volumeInfo"]["pageCount"]
        except:
            book_page = "Bilgi Mevcut Değil"
            hata += 1

        try:
            book_height = response["volumeInfo"]["dimensions"]["height"]
        except:
            book_height = None
            hata += 1

        try:
            book_width = response["volumeInfo"]["dimensions"]["width"]
        except:
            book_width = None
            hata += 1

        if hata < 3:
            book_data = {
                "ISBN": ISBN,
                "Koli No": koli,
                "Book Name": book_name,
                "Book Author": book_author,
                "Book Publisher": book_publisher,
                "Book Publish Date": response["volumeInfo"].get("publishedDate", "Bilgi Mevcut Değil"),
                "Book Page": book_page,
                "Book Height": book_height if book_height else "Bilgi Mevcut Değil",
                "Book Width": book_width if book_width else "Bilgi Mevcut Değil"
            }

            veri["books"].append(book_data)

            with open("library.json", "w", encoding="utf-8") as file:
                json.dump(veri, file, indent=4, ensure_ascii=False)

            print("Google Books: Kitap bilgileri başarıyla kaydedildi!")
        
        else:
            bulunamayan_isbnler.append(ISBN)

    if len(bulunamayan_isbnler) > 0:
        with open("open_Library_gönderilen.json", "w", encoding="utf-8") as file:
            json.dump(bulunamayan_isbnler, file, indent=4, ensure_ascii=False)
        
        openLibraryKayit(koli)

