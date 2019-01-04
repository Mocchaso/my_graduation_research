ORIG_BASE_PATH = "./dataset_orig"
SAVING_BASE_PATH = "./dataset"

# 元の対話データの最後の発話者がユーザ側（buyer）であるもののみ抽出する

import json
from collections import OrderedDict
import pprint

def extract_dataset(json_path):
    """
    システム（1, seller）から対話スタート、ユーザ（0, buyer）で対話終了している、
    商品のカテゴリがelectronicsである対話データのみ抽出して、別のディレクトリに保存
    抽出結果 -> train: 151, test: 33, dev（何者？）: 8
    """
    saving_scenarios = [] # 保存対象となるシナリオ
    scenario_count = 0
    with open(ORIG_BASE_PATH + "/" + json_path, "r") as f:
        scenarios = json.load(f)
        for i, scenario in enumerate(scenarios):
            if scenario["events"][0]["agent"] == 1 and scenario["events"][-1]["agent"] == 0 and scenario["scenario"]["category"] == "electronics":
                # 条件に合致するシナリオなら保存対象とする
                saving_scenarios.append(scenario)
                scenario_count += 1
                print("Selected {}th scenario as saving data.".format(i))
    with open(SAVING_BASE_PATH + "/" + json_path, "w", encoding="utf-8") as f:
        # 実際に、リストをJSON形式の文字列としてJSONファイルへ保存
        f.write(json.dumps(saving_scenarios))
    print("finished extracting {} scenarios from {}".format(scenario_count, json_path))

extract_dataset("train.json")
extract_dataset("test.json")
extract_dataset("dev.json")

# ちゃんと抽出できたかのテスト -> できた
with open(SAVING_BASE_PATH + "/train.json", "r", encoding="utf-8") as f:
    d = json.load(f)
    pprint.pprint(d[120], width=100)
