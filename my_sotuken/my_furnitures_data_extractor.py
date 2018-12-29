# coding: utf-8

from cocoa.core.util import write_json, read_json

all_furnitures_json_path = "./data/all-furnitures-scenarios.json"
new_json_name = "./data/my-experiment-scenarios.json"

# このリストはシナリオのタイトルを含む# this list contains scenario_titles
experiment_target_furnitures = [
    "Short wide Ikea Billy bookcase black-brown",
    "Storage drawer unit on wheels (ERIK Ikea brand)",
    "Ikea MALM 3-drawer chest, Birch Veneer",
    "IKEA Night stand",
    "IKEA MILLBERGET Desk Chair White"
    ] 

all_furnitures_dict = read_json(all_furnitures_json_path)
experiment_target_scenarios0 = []
experiment_target_scenarios1 = []
experiment_target_scenarios2 = []
experiment_target_scenarios3 = []
experiment_target_scenarios4 = []

for scenario in all_furnitures_dict:
    # 0: buyer, 1: seller
    scenario_title = scenario["kbs"][1]["item"]["Title"] # 参照するのはbuyerでもsellerでもOK

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