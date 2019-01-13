# coding: utf-8

import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

similar_products_json = "./en_similar_products_info.json"
en_positive_reviews_json = "./en_positive_reviews_info.json"

def is_positive(text):
    """
    ネガポジ判定でcompoundが0.5以上ならポジティブとする
    return: True or False
    """
    positive_threshold = 0.5 # ポジティブであると見なす閾値
    nltk.download("vader_lexicon") # ネガポジ判定に必要なモデルをダウンロード
    analyzer = SentimentIntensityAnalyzer()
    all_score = analyzer.polarity_scores(text)
    compound_score = all_score["compound"]
    return compound_score >= positive_threshold

def extract_positive_reviews():
    """
    読み込むJSONの構造
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

    # 類似商品に関するデータを記録したJSONを読み込む
    # このJSONを作成できるのは、shape_en_reviews_to_json.py
    similar_products_info = None
    with open(similar_products_json, "r", encoding="utf-8") as f:
        similar_products_info = json.load(f)

    for product, info in similar_products_info.items():
        reviews = info["reviews"] # en_similar_products_info.jsonに記録したレビュー文（この時点でネガポジ判定はまだ）
        positive_reviews = [review for review in reviews if is_positive(review)] # ネガポジ判定してポジティブと見なされたレビューのみを抽出
        info["reviews"] = positive_reviews # infoを、ポジティブなレビューのみが含まれたものに置き換える
        similar_products_info[product] = info # 置き換えたinfoを再登録
    
    # ポジティブなレビューの再登録を終えた辞書を、JSONとして新しく保存
    with open(en_positive_reviews_json, "w", encoding="utf-8") as f:
        json.dump(similar_products_info, f, indent = 4)
    print("finished saving en-positive-reviews to json.")

if __name__ == "__main__":
    extract_positive_reviews()