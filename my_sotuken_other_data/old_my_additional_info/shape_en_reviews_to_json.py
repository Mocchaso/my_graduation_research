# coding: utf-8

import json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

similar_product_urls = "./similar_product_urls.txt"
similar_product_yens = "./similar_product_yens.txt"
reviews_path = Path("./en")
en_reviews_files = list(reviews_path.iterdir())

def yen_to_dollar(yen):
    """
    2019年1月13日時点で、1ドル = 108.55円
    """
    converted = Decimal(yen / 108.55)
    result = converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(result)

def shape_en_reviews():
    """
    想定しているJSONの構造
    {
        "billy_ikea1" : {
            "brand": "...",
            "price_yen": ...,
            "price_dollar": ...,
            "reviews": ["review", "review", ...]
            "url": "...",
        },
        ...
    }
    """

    urls_data = []
    with open(similar_product_urls, "r", encoding="utf-8-sig") as f:
        # BOM(Byte Order Mark)付きになっているっぽいので、BOMを考慮したエンコーディング指定にする
        # 各行の末尾の改行文字を取り除きつつ、類似商品ごとのURLを取得してくる
        urls_data = [(line.split("\t")[0], line.split("\t")[1].rstrip("\n")) for line in f]
    
    price_yens_data = []
    with open(similar_product_yens, "r", encoding="utf-8-sig") as f:
        # BOM(Byte Order Mark)付きになっているっぽいので、BOMを考慮したエンコーディング指定にする
        # 各行の末尾の改行文字を取り除きつつ、類似商品ごとのURLを取得してくる
        price_yens_data = [(line.split("\t")[0], int(line.split("\t")[1].rstrip("\n"))) for line in f]

    result = {}
    for en_review in en_reviews_files:
        txt_name = en_review.stem # 拡張子無しのtxtファイル名の文字列(ex: "billy_ikea1")

        brand = "" # 銘柄のデータを記録するのに使う変数
        if "ikea" in txt_name:
            brand = "IKEA"
        elif "nitori" in txt_name:
            brand = "NITORI"
        elif "muji" in txt_name:
            brand = "MUJI"
        
        # 現在見ている類似商品に紐づいた価格情報とURLを取得
        price_yen = [price_yen_data[1] for price_yen_data in price_yens_data if price_yen_data[0] == txt_name][0]
        url = [url_data[1] for url_data in urls_data if url_data[0] == txt_name][0]
        
        with en_review.open("r", encoding="utf-8") as f:
            reviews = [line.rstrip("\n") for line in f]
            result[txt_name] = {
                    "brand": brand, # "IKEA" or "NITORI" or "MUJI"
                    "price_yen": price_yen,
                    "price_dollar": yen_to_dollar(price_yen),
                    "reviews": reviews,
                    "url": url
            }
    
    json_path = "./en_similar_products_info.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent = 4)

if __name__ == "__main__":
    shape_en_reviews()