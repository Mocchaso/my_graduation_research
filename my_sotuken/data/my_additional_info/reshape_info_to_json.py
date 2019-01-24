# coding: utf-8

import json

products = ["billy", "erik", "malm", "kullen", "millberget"]
info_orig_path = "similar_products.txt"

all_info = {}
json_path = "./similar_products_info.json"

for product in products:
    info_path = product + "_" + info_orig_path
    print(product)
    product_infos = [] # 交渉で扱う商品の類似商品の情報たち
    with open(info_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 1: # 最初の行を飛ばす
                line = line.split("\t")
                price_yen = float(line[0])
                product_name = line[1]
                print(product_name)
                brand = line[2]
                selling_rank = line[3]
                review1 = {"ja": line[4], "en": line[5]}
                review2 = {"ja": line[6], "en": line[7]}
                review3 = {"ja": line[8], "en": line[9]}
                review4 = {"ja": line[10], "en": line[11]}
                review5 = {"ja": line[12], "en": line[13]}
                reviews = [review1, review2, review3, review4, review5]
                if "\n" in line[14]: # 改行文字を含んでいたら排除
                    shorten_url = line[14].rstrip("\n")
                else:
                    shorten_url = line[14]

                # 類似商品1つに関する情報
                a_similar_product_info = {
                    "price_yen": price_yen, "product_name": product_name, "brand": brand,
                    "selling_rank": selling_rank, "reviews": reviews, "shorten_url": shorten_url
                }
                product_infos.append(a_similar_product_info) # 交渉で扱う商品の類似商品の情報たちを記録していく
    
    # 交渉で扱う商品それぞれの複数の類似商品の情報を、全体の辞書に記録
    all_info[product] = product_infos

# 全体の辞書をJSONに出力
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(all_info, f, ensure_ascii=False, indent=4)