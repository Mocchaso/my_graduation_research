import json
import requests
from bs4 import BeautifulSoup
import time
import urllib
import pandas as pd
import codecs

train_path = "./data/train.json"
test_path = "./data/test.json"
dev_path = "./data/dev.json"

def get_google_search_nums(query):
    # URLエンコード
    if "&" in query:
        query = query.replace("&", urllib.parse.quote("&"))
    
    res = requests.get("https://google.com/search?q=" + query)
    time.sleep(2)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")
    result_nums = soup.find_all("div", class_="sd", id="resultStats")[0].text

    if result_nums != None:
        result_nums = result_nums.split()
        if "約" in result_nums:
            result_nums = "".join(result_nums[1].split(",")) # ex: ["約", "500,000,000", "件"]
        elif "約" not in result_nums and "," in result_nums:
            result_nums = "".join(result_nums[0].split(",")) # ex: ["500,000,000", "件"]
        elif "約" not in result_nums and "," not in result_nums: # ex: ["2", "件"]
            result_nums = result_nums[0]
        return int(result_nums)
    else:
        # corresponding information was not found
        return 0

def extract_product_info():
    # 商品情報の抽出の前に変数宣言
    product_info = []
    json_paths = [train_path, test_path, dev_path] # scenario nums ... train: 5247, test: 838, dev: 597
    search_nums_dict = {} # シナリオタイトルの検索結果を保存し、検索済みのシナリオタイトルが現れたらここから参照する

    train_furniture_nums, test_furniture_nums, dev_furniture_nums = 0, 0, 0 # 各JSONファイルで家具カテゴリの商品に関するシナリオがいくつあるか
    with open(train_path, encoding="utf-8") as f:
        dataset = json.load(f)
        train_furniture_nums = len([scenario for scenario in dataset if scenario["scenario"]["category"] == "furniture"])
    with open(test_path, encoding="utf-8") as f:
        dataset = json.load(f)
        test_furniture_nums = len([scenario for scenario in dataset if scenario["scenario"]["category"] == "furniture"])
    with open(dev_path, encoding="utf-8") as f:
        dataset = json.load(f)
        dev_furniture_nums = len([scenario for scenario in dataset if scenario["scenario"]["category"] == "furniture"])
    
    print("all of furniture scenarios in 'train.json': {}".format(train_furniture_nums))
    print("all of furniture scenarios in 'test.json': {}".format(test_furniture_nums))
    print("all of furniture scenarios in 'dev.json': {}".format(dev_furniture_nums))
    print()

    # 抽出の処理
    pd_idx = 0 # データフレームの行名に相当するインデックス
    for json_path in json_paths:
        with open(json_path, encoding="utf-8") as f:
            dataset = json.load(f)
            furniture_idx = 0 # 各JSONファイルにおいて、家具カテゴリの何番目を見ているか

            for scenario in dataset:
                scenario_dict = scenario["scenario"]
                scenario_category = scenario_dict["category"]
                json_name = json_path.split("/")[-1]

                if scenario_category == "furniture":
                    furniture_idx += 1
                    if "train.json" in json_path:
                        print("extracting {}th / {} furniture_product_info in '{}'".format(furniture_idx, train_furniture_nums, json_name))
                    elif "test.json" in json_path:
                        print("extracting {}th / {} furniture_product_info in '{}'".format(furniture_idx, test_furniture_nums, json_name))
                    elif "dev.json" in json_path:
                        print("extracting {}th / {} furniture_product_info in '{}'".format(furniture_idx, dev_furniture_nums, json_name))
                                        
                    # title -> 商品名を抽出できそう？ (0: buyer, 1: seller)
                    scenario_title = scenario_dict["kbs"][1]["item"]["Title"] # 参照するのはbuyerでもsellerでもOK

                    search_nums = None
                    if scenario_title not in search_nums_dict.keys():
                        # まだ追加していないシナリオのタイトルなら、Google検索にかけて辞書に記録
                        search_nums = get_google_search_nums(scenario_title)
                        search_nums_dict[scenario_title] = search_nums
                    else:
                        # 検索済みのタイトルなら検索件数を辞書から参照
                        search_nums = search_nums_dict[scenario_title]
                    
                    image_path = scenario_dict["kbs"][1]["item"]["Images"] # 参照するのはbuyerでもsellerでもOK
                    if image_path != []:
                        image_path = image_path[0]
                    else:
                        image_path = None
                    
                    # 買い手、売り手それぞれの目標価格
                    # 買い手 ... bottomline: listing price, target: 以下で取得
                    # 売り手 ... bottomline: listing price * 0.7, target: listing price
                    target_price_buyer = scenario_dict["kbs"][0]["personal"]["Target"]
                    target_price_seller = scenario_dict["kbs"][1]["personal"]["Target"]
                    
                    # Descriptionのリストには、複数の説明文が含まれている
                    # -> 半角スペースで結合
                    description_buyer = scenario_dict["kbs"][0]["item"]["Description"]
                    description_buyer = " ".join(description_buyer)
                    description_seller = scenario_dict["kbs"][1]["item"]["Description"] # buyerよりも説明文長い
                    description_seller = " ".join(description_seller)
                    
                    product_info.append({pd_idx: [scenario_title, search_nums, image_path, target_price_buyer, target_price_seller, description_buyer, description_seller]})
                    pd_idx += 1
        
        print("finished extracting product_info from '{}'".format(json_path.split("/")[-1]))
    
    # setに変換することで重複を排除し、再度listに変換する
    print("finished extracting all product_info.")
    return product_info

def store_furniture_title(product_info):
    print("product_info nums: {}".format(len(product_info)))
    cols = ["scenario_title", "search_nums", "image_path", "target_price_buyer", "target_price_seller", "description_buyer", "description_seller"]
    df_info = pd.DataFrame(columns=cols)

    # シナリオのタイトルとその情報をそれぞれデータフレームに追加
    for info in product_info:
        row_idx, info_value = list(info.keys())[0], list(info.values())[0]

        # 名前がシナリオのタイトル、内容が商品情報のSeries
        # データフレームの各行において、この名前が行ラベルになる
        row_data = pd.Series(info_value, index=cols, name=row_idx)

        df_info = df_info.append(row_data)
    
    # データフレームを検索件数で降順ソート
    df_info = df_info.sort_values("search_nums", ascending=False)

    # タブ文字で区切ったtsvファイルとして出力(Descriptionの内容にカンマが含まれているため)
    df_info.to_csv("./furniture_product_info.tsv", sep="\t")
    print("finished storing product_info as tsv file.")

if __name__ == "__main__":
    # tsvファイル出力済みなら以下2行をコメントアウト
    # product_info = extract_product_info()
    # store_furniture_title(product_info)

    # utf-8でデコードできない文字の0x81（恐らく全角スペース）でUnicodeEncodeError
    # → codecs.openを使い、エラーが出ても無視して開く
    with codecs.open(filename="./furniture_product_info.tsv", mode="r", encoding="utf-8", errors="ignore") as file:
        product_info_df = pd.read_csv(file, sep="\t", index_col=0)

        # IKEAの商品情報のみを抽出する
        # シナリオのタイトルに"IKEA"の文字列が入っているやつを抽出する
        product_info_lower = product_info_df["scenario_title"].str.lower()
        condition = product_info_lower.str.contains("ikea")
        product_info_ikea = product_info_df[condition]
        
        # 抽出したらファイルに保存しておく
        # product_info_ikea.to_csv("./ikea_product_info.tsv", sep="\t")
        # print("finishsed storing ikea_product_info as tsv file.") 

        # 重複したシナリオタイトルの行を削除したデータフレームを取得
        product_info_ikea = product_info_ikea.drop_duplicates(subset=["scenario_title"])

        # これもファイルに保存しておく
        # product_info_ikea.to_csv("./ikea_product_info(no_duplicated).tsv", sep="\t")
        # print("finishsed storing ikea_product_info of no duplicated scenario_title as tsv file.") 

        ### 実験データに使用する商品データのシナリオタイトルたち
        scenario_titles = [
            "Short wide Ikea Billy bookcase black-brown",
            "Storage drawer unit on wheels (ERIK Ikea brand)",
            "Ikea MALM 3-drawer chest, Birch Veneer",
            "IKEA Night stand",
            "IKEA MILLBERGET Desk Chair White"
        ]

        new_df = product_info_ikea[product_info_ikea["scenario_title"].isin(scenario_titles)]
        new_df.to_csv("./experiment_product_info.tsv", sep="\t")

        """ came to be unnecessary
        best1_df = product_info_ikea[0:1]
        best2_df = product_info_ikea[1:2]

        ikea_info_nums = product_info_ikea.shape[0]
        if ikea_info_nums % 2 == 0:
            # 中央の2つのうち、上位寄りの行を抽出
            # 例：[0, 1, 2, 3] -> 1
            idx = ikea_info_nums / 2
            midium_df = product_info_ikea[idx-1:idx]
        elif ikea_info_nums % 2 == 1:
            # 中央を抽出
            # 例：[0, 1, 2, 3, 4] -> 2
            idx = int(ikea_info_nums / 2)
            midium_df = product_info_ikea[idx:idx+1]
        
        worst2_df = product_info_ikea[-2:-1]
        worst1_df = product_info_ikea[-1:]

        # 実験で使用する5個の商品を結合したデータフレームの作成と保存
        # -> 上位2個、中間1個、下位2個
        cols = ["scenario_title", "search_nums", "image_path", "target_price_buyer", "target_price_seller", "description_buyer", "description_seller"]
        experiment_df = pd.DataFrame(columns=cols)
        experiment_df = experiment_df.append(best1_df)
        experiment_df = experiment_df.append(best2_df)
        experiment_df = experiment_df.append(midium_df)
        experiment_df = experiment_df.append(worst2_df)
        experiment_df = experiment_df.append(worst1_df)
        # experiment_df.to_csv("./experiment_product_info.tsv", sep="\t")
        
        # 上位2個、中間1個、下位2個の商品を出力
        # print(best1_df)
        # print(best2_df)
        # print(midium_df)
        # print(worst2_df)
        # print(worst1_df)
        """