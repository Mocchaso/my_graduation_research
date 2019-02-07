# coding: utf-8

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from collections import OrderedDict

review_txt_paths = [
    "./billy_reviews.txt",
    "./erik_reviews.txt",
    "./malm_3drawer_reviews.txt",
    "./kullen_2drawer_reviews.txt",
    "./millberget_reviews.txt"
]
review_tsv_paths = [
    "./billy_reviews.tsv",
    "./erik_reviews.tsv",
    "./malm_3drawer_reviews.tsv",
    "./kullen_2drawer_reviews.tsv",
    "./millberget_reviews.tsv"
]

def output_review_tsvs():
    for review_txt_path, review_tsv_path in zip(review_txt_paths, review_tsv_paths):
        df = pd.read_table(review_txt_path) # ファイル内の1行目が強制的にヘッダーになるがそれでOK
        df.to_csv(review_tsv_path, encoding="utf-8", sep="\t")
        print("finished storing '{}'".format(review_tsv_path))

def extract_freqword():
    freq_nums_in_review = dict()

    for review_tsv_path in review_tsv_paths:
        df = pd.read_csv(review_tsv_path, encoding="utf-8", sep="\t")
        reviews = df["review"].values

        # 単語の出現回数を数える
        cv = CountVectorizer(stop_words="english")
        matrix = cv.fit_transform(reviews)
        words = cv.get_feature_names()
        # print(matrix)
        # print(matrix.toarray())

        # 行方向の和を求めて各単語の出現回数を表す行列を求める
        word_nums_matrix = np.sum(matrix.toarray(), axis=0)
        # print(word_nums_matrix)

        # 単語とその出現回数を記録した辞書を作る
        freq_nums = {words[i]: word_nums_matrix[i] for i in range(len(words))}
        # print(freq_nums)

        # 出現回数で降順ソート
        freq_nums_descend = OrderedDict(sorted(freq_nums.items(), key=lambda x: x[1], reverse=True))
        # print(freq_nums_descend)

        # 各家具データごとの単語出現回数を記録する
        freq_nums_in_review[review_tsv_path] = freq_nums_descend
    
    return freq_nums_in_review


if __name__ == "__main__":
    # output_review_tsvs()

    # 単語の出現回数を算出する
    freq_nums_in_review = extract_freqword()

    # 元のデータフレームを読み込む
    df = pd.read_csv(review_tsv_path, encoding="utf-8", sep="\t")

    # 出現回数が最も多い単語を含む行以外を削除したデータフレームを作成する

    # 作成したデータフレームを保存する

    # そのデータフレームの中からランダムでレビューを選ぶ。それをブラウザ上に表示させる
    