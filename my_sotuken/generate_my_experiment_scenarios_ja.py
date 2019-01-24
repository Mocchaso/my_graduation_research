# coding: utf-8

from cocoa.core.util import write_json, read_json

all_furnitures_json_path = "./data/all-furnitures-scenarios.json"
new_json_name = "./data/my-experiment-scenarios.json"
new_json_name_javer = "./data/my-experiment-scenarios-ja.json"

# このリストはシナリオのタイトルを含む
# this list contains scenario_titles
experiment_target_furnitures = [
    "Short wide Ikea Billy bookcase black-brown",
    "Storage drawer unit on wheels (ERIK Ikea brand)",
    "Ikea MALM 3-drawer chest, Birch Veneer",
    "IKEA Night stand",
    "IKEA MILLBERGET Desk Chair White"
] 

# 買い手側に見える商品データの説明文、日本語版
# HTML内でsafeフィルターを適用しているので、以下のHTMLタグも反映されるようになっている
description_buyer_ja = [
    u"幅：31と1/2 inch（80 cm）、奥行き：11 inch（28 cm）<br><a href='https://www.ikea.com/jp/ja/catalog/products/10404246/#/40351581' target='_blank'>商品の詳細情報（IKEA公式オンラインストアのページ）</a><br>オンラインストアでの価格：6,999円 -> 63.79ドル（2019年1月24日時点）",
    u"ベッドサイドのテーブル、あるいは保管用として最適です。錠と鍵も付属しています。<br><a href='https://www.ikea.com/jp/ja/catalog/products/30176069/' target='_blank'>商品の詳細情報（IKEA公式オンラインストアのページ）</a><br>オンラインストアでの価格：9,990円 -> 91.04ドル（2019年1月24日時点）",
    u"Ikea Malm ... 3つの引き出し付きのタンスです。<br>色：カンバ材（Birch veneer）<br>状態：非常に良好で引き出しはスムーズに動きます。<br><a href='https://www.ikea.com/jp/ja/catalog/products/30354660/' target='_blank'>商品の詳細情報（IKEA公式オンラインストアのページ）</a><br>オンラインストアでの価格：12,990円 -> 118.38ドル（2019年1月24日時点）",
    u"IKEA製のナイトテーブルです。幅：35 cm、奥行き：40 cm、高さ：49 cm<br><a href='https://www.ikea.com/jp/ja/catalog/products/30355706/' target='_blank'>商品の詳細情報（IKEA公式オンラインストアのページ）</a><br>オンラインストアでの価格：3,999円 -> 36.44ドル（2019年1月24日時点）",# u"型番は不明ですが、IKEAで購入しました。" -> 説明文としては微妙なので少し変更する
    u"6か月間使用されたものですが、新品のように綺麗です。また、セダンの後部座席に置けるほどの大きさです。<br><a href='https://www.ikea.com/jp/ja/catalog/products/50339414/#/00339416' target='_blank'>商品の詳細情報（IKEA公式オンラインストアのページ）</a><br>オンラインストアでの価格：9,990円 -> 91.04ドル（2019年1月24日時点）"
]

"""
買い手側に表示される、実験で使用する商品データの説明文

追加する情報
銘柄：
スウェーデン発祥。ヨーロッパ・北米・アジア・オセアニアなど世界各地に出店している。
日本には9店舗あり、オンラインストアのサービスも展開している。
特徴：自分で家具を組み立てる。スウェーデン語の名前が商品名についている。
↓ 短縮
スウェーデン発祥で、ヨーロッパ・北米・アジア・オセアニアなど世界各地に出店されている。特徴：自分で家具を組み立てる、スウェーデン語の名前が商品名についている。


short wide ... :
英語："Here's the link to my other ads: https://sfbay.craigslist.org/search/sss?userid=55884146 Read about it here: http://www.ikea.com/us/en/catalog/products/70263842/ Width: 31 1/2 "" Depth: 11 "" Width: 80 cm Depth: 28 cm"
和訳："幅：31と1/2 inch（80 cm）、深さ：11 inch（28 cm）"
品質情報：
-> 口コミ：小部屋に小さめの本棚が必要となって購入したら、ピッタリのサイズだった。
情報量の情報：
約8,720,000件（2018年12月27日時点）

storage drawer ... :
英語：Great as a bedside table, or for storage. Lock + Key included See product specs here: http://www.ikea.com/us/en/catalog/products/20341003/#/10151809 Key features - The casters make it easy to move around. - The two lower drawers can be locked. - Drawer stops prevent the drawer from being pulled out too far.
和訳：ベッドサイドのテーブル、あるいは保管用として最適です。錠と鍵も付属しています。
（品質情報に利用）主な機能：キャスター付きで移動が楽です。下2段の引き出しは施錠することができます。引き出しは引っ張りすぎるのを防止します。
品質情報：
-> 口コミ：自分で組み立てることに少々不安があったが、2人で1個を10分程度で完成させることができた。
情報量の情報：
約1,970,000件（2018年12月27日時点）

ikea malm ... :
英語：Ikea Malm 3-drawer chest is for sale Color: Birch veneer Condition: Excellent, smooth running drawers
和訳：3つの引き出し付きのタンスです。色：カンバ材（Birch veneer）、状態：非常に良好で引き出しはスムーズに動きます。
品質情報：
-> 口コミ：つくりはとてもしっかりしていて、長期間気持ち良く使える商品だと思う。しかし、重いため、女性が1人で自宅に持ち帰って組み立てるのは少々厳しい。
情報量の情報：
約410,000件（2018年12月27日時点）

ikea night stand:
英語：Not sure about the model number but I bought it at IKEA.
和訳：（craigslistの投稿からスクレイピングした情報で、今回のシステムには利用できなさそうな情報）型番は不明ですが、IKEAで購入しました。
品質情報：
-> 口コミ：ベッドサイトに置いたところ、高さと幅が丁度良く使い勝手が良い。天板周りの部分が外れてきたが、木工用ボンドで簡単に直せる程度なので許せる範囲。
情報量の情報：
約230,000件（2018年12月27日時点）

ikea millberget ... :
英語：Only used for 6 months and very clean. Looks like new. Can be put on the backseat of Sedan. Pickup only.
和訳：6か月間のみ使用していました。新品のように綺麗です。セダンの後部座席に置けます。
品質情報：
-> 口コミ：イメージより大きかったが、その分ホールド感が抜群。コストパフォーマンスが良い。
情報量の情報：
約89,600件（2018年12月27日時点）
"""

def extract_furnitures_scenarios():
    print(u"実験で使用するシナリオデータの英語版（JSONファイル）を作成します。")

    all_furnitures_dict = read_json(all_furnitures_json_path)
    experiment_target_scenarios0 = []
    experiment_target_scenarios1 = []
    experiment_target_scenarios2 = []
    experiment_target_scenarios3 = []
    experiment_target_scenarios4 = []

    for scenario in all_furnitures_dict:
        # 0: buyer, 1: seller
        scenario_title = scenario["kbs"][0]["item"]["Title"] # 参照するのはbuyerでもsellerでもOK

        # in演算子を使った方がスマートだが、上記のリストの順番を保ってデータを抽出するため、このような処理とした
        if scenario_title == experiment_target_furnitures[0]:
            # "Short wide Ikea Billy bookcase black-brown"
            experiment_target_scenarios0.append(scenario)
        if scenario_title == experiment_target_furnitures[1]:
            # "Storage drawer unit on wheels (ERIK Ikea brand)"
            experiment_target_scenarios1.append(scenario)
        if scenario_title == experiment_target_furnitures[2]:
            # "Ikea MALM 3-drawer chest, Birch Veneer"
            experiment_target_scenarios2.append(scenario)
        if scenario_title == experiment_target_furnitures[3]:
            # "IKEA Night stand"
            experiment_target_scenarios3.append(scenario)
        if scenario_title == experiment_target_furnitures[4]:
            # "IKEA MILLBERGET Desk Chair White"
            experiment_target_scenarios4.append(scenario)
        
        if scenario_title in experiment_target_furnitures:
            print("finished extracting a scenario: {}".format(scenario_title))

    # リスト結合
    experiment_target_scenarios = experiment_target_scenarios0 + experiment_target_scenarios1 + experiment_target_scenarios2 + experiment_target_scenarios3 + experiment_target_scenarios4
    print("finished extracting all targets(scenarios).")

    write_json(experiment_target_scenarios, new_json_name)
    print("finished storing all targets as a json file.")

def extract_furnitures_scenarios_as_ja():
    print(u"実験で使用するシナリオデータの日本語版（JSONファイル）を作成します。")
    experiment_target_scenarios = read_json(new_json_name)

    # 説明文を、日本語のものに置換
    for i, scenario in enumerate(experiment_target_scenarios):
        scenario_title = scenario["kbs"][0]["item"]["Title"]
        if scenario_title == experiment_target_furnitures[0]:
            experiment_target_scenarios[i]["kbs"][0]["item"]["Description"] = description_buyer_ja[0]
        elif scenario_title == experiment_target_furnitures[1]:
            experiment_target_scenarios[i]["kbs"][0]["item"]["Description"] = description_buyer_ja[1]
        elif scenario_title == experiment_target_furnitures[2]:
            experiment_target_scenarios[i]["kbs"][0]["item"]["Description"] = description_buyer_ja[2]
        elif scenario_title == experiment_target_furnitures[3]:
            experiment_target_scenarios[i]["kbs"][0]["item"]["Description"] = description_buyer_ja[3]
        elif scenario_title == experiment_target_furnitures[4]:
            experiment_target_scenarios[i]["kbs"][0]["item"]["Description"] = description_buyer_ja[4]

    write_json(experiment_target_scenarios, new_json_name_javer)
    print("finished storing all targets as a json file.")

if __name__ == "__main__":
    extract_furnitures_scenarios()
    extract_furnitures_scenarios_as_ja()

    test_json = read_json(new_json_name_javer)

    scenario0 =  test_json[0]
    print(scenario0["kbs"][0]["item"]["Description"])
