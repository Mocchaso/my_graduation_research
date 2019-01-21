# coding: utf-8

import requests
from bs4 import BeautifulSoup
import time

# 類似商品として扱うことにした商品のURLリスト
# BILLY
billy = [
    "https://www.nitori-net.jp/store/ProductDisplay?ptr=item&urlRequestType=Base&catalogId=10001&categoryId=11352&productId=797056&errorViewName=ProductDisplayErrorView&urlLangId=&langId=-10&top_category=11011&parent_category_rn=11011&storeId=10001",
    "https://www.nitori-net.jp/store/ProductDisplay?ptr=item&urlRequestType=Base&catalogId=10001&categoryId=11352&productId=895508&errorViewName=ProductDisplayErrorView&urlLangId=&langId=-10&top_category=11011&parent_category_rn=11011&storeId=10001",
    "https://www.nitori-net.jp/store/ja/ec/8841241s?ptr=item"
]

# ERIK
erik = [
    "https://www.nitori-net.jp/store/ja/ec/6200064s?ptr=item",
    "https://www.nitori-net.jp/store/ja/ec/6201361s?ptr=item",
    "https://www.nitori-net.jp/store/ja/ec/5631568s?ptr=item"
]

# MALM
malm = [
    "https://www.nitori-net.jp/store/ProductDisplay?ptr=item&urlRequestType=Base&catalogId=10001&categoryId=11175&productId=1078135&errorViewName=ProductDisplayErrorView&urlLangId=&langId=-10&top_category=11006&parent_category_rn=11006&storeId=10001",
    "https://www.nitori-net.jp/store/ja/ec/StorageRackDresser/ClothingCase/ClothingCaseLiving/8400321s?ptr=item",
    "https://www.nitori-net.jp/store/ja/ec/StorageRackDresser/ClothingCase/ClothingCaseLiving/8410471s?ptr=item"
]

# KULLEN
kullen = [
    "https://www.nitori-net.jp/store/ja/ec/5620144s?rc=set&ptr=item",
    "https://www.nitori-net.jp/store/ja/ec/TableChair/BedSideNightTable/2600131s?ptr=item",
    # 3品目のレビューがオンラインストアに無かったため、外部サイトの情報を手作業で保存する
    # "https://store.shopping.yahoo.co.jp/nitori-net/1510139.html",
    # "https://review.rakuten.co.jp/item/1/210615_10141866/1.1/"
]

# MILLBERGET
millberget = [
    "https://www.nitori-net.jp/store/ProductDisplay?ptr=item&urlRequestType=Base&catalogId=10001&categoryId=11349&productId=1431036&errorViewName=ProductDisplayErrorView&urlLangId=&langId=-10&top_category=42001&parent_category_rn=42001&storeId=10001",
    "https://www.nitori-net.jp/store/ProductDisplay?ptr=item&urlRequestType=Base&catalogId=10001&categoryId=11349&productId=904508&errorViewName=ProductDisplayErrorView&urlLangId=&langId=-10&top_category=42001&parent_category_rn=42001&storeId=10001",
    "https://www.nitori-net.jp/store/ProductDisplay?ptr=item&urlRequestType=Base&catalogId=10001&categoryId=&productId=1635586&errorViewName=ProductDisplayErrorView&urlLangId=&langId=-10&top_category=&parent_category_rn=&storeId=10001"
]

def scrape_review(target_url):
    """
    1つの商品に対するレビューを全て取得する
    参考サイト：
    https://qiita.com/itkr/items/513318a9b5b92bd56185
    http://kondou.com/BS4/
    """
    # WebページからHTMLソースを取得
    r = requests.get(target_url)
    r.raise_for_status()

    # HTMLソースから必要な情報を取得
    # item_review(id) -> review_parts(class) -> review_personal_bottom(class) -> text
    soup = BeautifulSoup(r.text, "lxml")
    item_review = soup.find("div", id="item_review")
    review_parts = item_review.find_all("div", class_="review_parts")
    review_personal_bottom = [review_part.find("div", class_="review_personal_bottom") for review_part in review_parts]
    review_comments = [review.text.replace("\n", "").replace("\t", "") for review in review_personal_bottom]
    return review_comments

def save_review(reviews, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(reviews)) # リストの要素ごとに改行して書き込む

if __name__ == "__main__":
    all_product_urls = [billy, erik, malm, kullen, millberget]
    lang = "ja/"

    for i, product_urls in enumerate(all_product_urls):
        if i == 0:
            file_orig_path = lang + "billy_nitori"
        elif i == 1:
            file_orig_path = lang + "erik_nitori"
        elif i == 2:
            file_orig_path = lang + "malm_nitori"
        elif i == 3:
            file_orig_path = lang + "kullen_nitori"
        elif i == 4:
            file_orig_path = lang + "millberget_nitori"
        
        for j, similar_product_url in enumerate(product_urls):
            file_path = file_orig_path + "{}.txt".format(j + 1)
            reviews = scrape_review(similar_product_url) # 類似商品1つのレビュー全てを取得
            save_review(reviews, file_path) # txtファイルに保存
            time.sleep(1) # サイトへの負荷を軽減
    
    print("all similar product's reviews has been stored.")