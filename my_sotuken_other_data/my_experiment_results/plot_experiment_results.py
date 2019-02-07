# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties # 日本語表示
import pandas as pd
from itertools import combinations

def test1():
    """
    参考サイト：
    http://bicycle1885.hatenablog.com/entry/2014/02/14/023734
    """
    x = np.arange(-3, 3, 0.1)
    y = np.sin(x)
    plt.plot(x, y)
    plt.show()

def test2():
    """
    参考サイト：
    http://bicycle1885.hatenablog.com/entry/2014/02/14/023734
    """
    x = np.random.randn(30)
    y = np.sin(x) + np.random.randn(30)
    # plt.plot(x, y, "o")  # "o"は小さい円(circle marker)
    plt.plot(x, y, "ro")  # "r"はredの省略
    plt.show()

def plot_prev_system_results():
    # 先行研究
    # プロットする回答データの設問の組み合わせ：2+3と4, 2+3と7, 2+3と8, 4と7, 4と8, 7と8

    df_prev = pd.read_excel("./craigslistbargain_ans.xlsx")
    questions_prev = df_prev.columns.values
    timestamps_prev = df_prev[questions_prev[0]]
    prev1 = df_prev[questions_prev[1]]
    prev3 = df_prev[questions_prev[3]]
    prev2_3 = df_prev[[questions_prev[2], questions_prev[3]]]
    prev4 = df_prev[questions_prev[4]]
    prev6 = df_prev[questions_prev[6]]
    prev5_6 = df_prev[[questions_prev[5], questions_prev[6]]]
    prev7 = df_prev[questions_prev[7]]
    prev8 = df_prev[questions_prev[8]]
    prev9 = df_prev[questions_prev[9]]

    ax = plt.subplot()
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    fp = FontProperties(fname="C:\Windows\Fonts\YuGothic.ttf", size=18)
    
    # 設問2+3, 4
    for i, attr_ans in enumerate(["1: 品質", "2: 価格", "3: 銘柄"]):
        attr_dict = {0: "quality", 1: "price", 2: "brand"}
        
        ax.set_title("アンケート結果 - {}".format(attr_dict[i]), fontproperties=fp)
        ax.set_xlabel("設問2+3", fontproperties=fp)
        ax.set_ylabel("設問4", fontproperties=fp)
        ax.grid(linestyle="dashed") # 破線のグリッド

        # prev2_3から、属性ごとの回答データを抽出
        prev_attr = df_prev[df_prev[questions_prev[2]].isin([attr_ans])]
        print(prev_attr)
        if i == 0:
            ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[4]], s=300, c="red", marker='o', alpha=0.3)
        elif i == 1:
            ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[4]], s=300, c="green", marker='o', alpha=0.3)
        elif i == 2:
            ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[4]], s=300, c="blue", marker='o', alpha=0.3)
        plt.savefig("./craigslistbargain_figs/q2+3_4-{}.png".format(attr_dict[i])) # プロットした図を画像として保存する
        ax.cla()
        
    # 設問2+3, 7
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    for i, attr_ans in enumerate(["1: 品質", "2: 価格", "3: 銘柄"]):
        attr_dict = {0: "quality", 1: "price", 2: "brand"}

        ax.set_title("アンケート結果 - {}".format(attr_dict[i]), fontproperties=fp)
        ax.set_xlabel("設問2+3", fontproperties=fp)
        ax.set_ylabel("設問7", fontproperties=fp)
        ax.grid(linestyle="dashed") # 破線のグリッド

        # prev2_3から、属性ごとの回答データを抽出
        prev_attr = df_prev[df_prev[questions_prev[2]].isin([attr_ans])]
        print(prev_attr)
        if i == 0:
            ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[7]], s=300, c="red", marker='o', alpha=0.3)
        elif i == 1:
            ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[7]], s=300, c="green", marker='o', alpha=0.3)
        elif i == 2:
            ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[7]], s=300, c="blue", marker='o', alpha=0.3)
        plt.savefig("./craigslistbargain_figs/q2+3_7-{}.png".format(attr_dict[i])) # プロットした図を画像として保存する
        ax.cla()

    # # 設問2+3, 8
    # for i, attr_ans in enumerate(["1: 品質", "2: 価格", "3: 銘柄"]):
    #     attr_dict = {0: "quality", 1: "price", 2: "brand"}

    #     fp = FontProperties(fname="C:\Windows\Fonts\YuGothic.ttf", size=18)
    #     ax.set_title("アンケート結果 - {}".format(attr_dict[i]), fontproperties=fp)
    #     ax.set_xlabel("設問2+3", fontproperties=fp)
    #     ax.set_ylabel("設問8", fontproperties=fp)
    #     ax.grid(linestyle="dashed") # 破線のグリッド

    #     # prev2_3から、属性ごとの回答データを抽出
    #     prev_attr = df_prev[df_prev[questions_prev[2]].isin([attr_ans])]
    #     print(prev_attr)
    #     if i == 0:
    #         ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[8]], s=300, c="red", marker='o', alpha=0.3)
    #     elif i == 1:
    #         ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[8]], s=300, c="green", marker='o', alpha=0.3)
    #     elif i == 2:
    #         ax.scatter(x=prev_attr[questions_prev[3]], y=prev_attr[questions_prev[8]], s=300, c="blue", marker='o', alpha=0.3)
    #     plt.savefig("./craigslistbargain_figs/q2+3_8-{}.png".format(attr_dict[i])) # プロットした図を画像として保存する
    #     ax.cla()

    # 設問4, 7
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    ax.set_title("アンケート結果", fontproperties=fp)
    ax.set_xlabel("設問4", fontproperties=fp)
    ax.set_ylabel("設問7", fontproperties=fp)
    ax.grid(linestyle="dashed") # 破線のグリッド
    ax.scatter(x=prev4, y=prev7, s=300, marker='o', alpha=0.3)
    plt.savefig("./craigslistbargain_figs/q4_7.png") # プロットした図を画像として保存する
    ax.cla()

    # 設問4, 8
    # fp = FontProperties(fname="C:\Windows\Fonts\YuGothic.ttf", size=18)
    # ax.set_title("アンケート結果", fontproperties=fp)
    # ax.set_xlabel("設問4", fontproperties=fp)
    # ax.set_ylabel("設問8", fontproperties=fp)
    # ax.grid(linestyle="dashed") # 破線のグリッド
    # ax.scatter(x=prev4, y=prev8, s=300, marker='o', alpha=0.3)
    # plt.savefig("./craigslistbargain_figs/q4_8.png") # プロットした図を画像として保存する
    # ax.cla()

    # # 設問7, 8
    # fp = FontProperties(fname="C:\Windows\Fonts\YuGothic.ttf", size=18)
    # ax.set_title("アンケート結果", fontproperties=fp)
    # ax.set_xlabel("設問7", fontproperties=fp)
    # ax.set_ylabel("設問8", fontproperties=fp)
    # ax.grid(linestyle="dashed") # 破線のグリッド
    # ax.scatter(x=prev7, y=prev8, s=300, marker='o', alpha=0.3)
    # plt.savefig("./craigslistbargain_figs/q7_8.png") # プロットした図を画像として保存する
    # ax.cla()



def plot_proposal_system_results():
    # 本研究
    # プロットする回答データの設問の組み合わせ：2+3と4, 2+3と7, 2+3と8, 4と7, 4と8, 7と8

    df_proposal = pd.read_excel("./my_sotuken_ans.xlsx")
    questions_proposal = df_proposal.columns
    timestamps_proposal = df_proposal[questions_proposal[0]]
    proposal1 = df_proposal[questions_proposal[1]]
    proposal3 = df_proposal[questions_proposal[3]]
    proposal2_3 = df_proposal[[questions_proposal[2], questions_proposal[3]]]
    proposal4 = df_proposal[questions_proposal[4]]
    proposal6 = df_proposal[questions_proposal[6]]
    proposal5_6 = df_proposal[[questions_proposal[5], questions_proposal[6]]]
    proposal7 = df_proposal[questions_proposal[7]]
    proposal8 = df_proposal[questions_proposal[8]]
    proposal9 = df_proposal[questions_proposal[9]]

    ax = plt.subplot()
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    fp = FontProperties(fname="C:\Windows\Fonts\YuGothic.ttf", size=18)

    # 設問2+3, 4
    for i, attr_ans in enumerate(["1: 品質", "2: 価格", "3: 銘柄"]):
        attr_dict = {0: "quality", 1: "price", 2: "brand"}

        ax.set_title("アンケート結果 - {}".format(attr_dict[i]), fontproperties=fp)
        ax.set_xlabel("設問2+3", fontproperties=fp)
        ax.set_ylabel("設問4", fontproperties=fp)
        ax.grid(linestyle="dashed") # 破線のグリッド

        # proposal2_3から、属性ごとの回答データを抽出
        proposal_attr = df_proposal[df_proposal[questions_proposal[2]].isin([attr_ans])]
        print(proposal_attr)
        if i == 0:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[4]], s=300, c="red", marker='o', alpha=0.3)
        elif i == 1:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[4]], s=300, c="green", marker='o', alpha=0.3)
        elif i == 2:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[4]], s=300, c="blue", marker='o', alpha=0.3)
        plt.savefig("./my_sotuken_figs/q2+3_4-{}.png".format(attr_dict[i])) # プロットした図を画像として保存する
        ax.cla()
    
    # 設問2+3, 5+6
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    for i, attr_ans in enumerate(["1: 品質", "2: 価格", "3: 銘柄"]):
        attr_dict = {0: "quality", 1: "price", 2: "brand"}

        ax.set_title("アンケート結果 - {}".format(attr_dict[i]), fontproperties=fp)
        ax.set_xlabel("設問2+3", fontproperties=fp)
        ax.set_ylabel("設問5+6", fontproperties=fp)
        ax.grid(linestyle="dashed") # 破線のグリッド

        # proposal2_3から、属性ごとの回答データを抽出
        proposal_attr = df_proposal[df_proposal[questions_proposal[2]].isin([attr_ans])]
        # 更に、類似商品が提示されたユーザの回答データのみを抽出
        proposal_sim_product = proposal_attr[proposal_attr[questions_proposal[5]] == "はい"]
        print(proposal_sim_product)
        if i == 0:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[6]], s=300, c="red", marker='o', alpha=0.3)
        elif i == 1:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[6]], s=300, c="green", marker='o', alpha=0.3)
        elif i == 2:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[6]], s=300, c="blue", marker='o', alpha=0.3)
        plt.savefig("./my_sotuken_figs/q2+3_5+6-{}.png".format(attr_dict[i])) # プロットした図を画像として保存する
        ax.cla()
    
    # 設問2+3, 7
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    for i, attr_ans in enumerate(["1: 品質", "2: 価格", "3: 銘柄"]):
        attr_dict = {0: "quality", 1: "price", 2: "brand"}

        ax.set_title("アンケート結果 - {}".format(attr_dict[i]), fontproperties=fp)
        ax.set_xlabel("設問2+3", fontproperties=fp)
        ax.set_ylabel("設問7", fontproperties=fp)
        ax.grid(linestyle="dashed") # 破線のグリッド

        # proposal2_3から、属性ごとの回答データを抽出
        proposal_attr = df_proposal[df_proposal[questions_proposal[2]].isin([attr_ans])]
        print(proposal_attr)
        if i == 0:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[7]], s=300, c="red", marker='o', alpha=0.3)
        elif i == 1:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[7]], s=300, c="green", marker='o', alpha=0.3)
        elif i == 2:
            ax.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[7]], s=300, c="blue", marker='o', alpha=0.3)
        plt.savefig("./my_sotuken_figs/q2+3_7-{}.png".format(attr_dict[i])) # プロットした図を画像として保存する
        ax.cla()

    # 設問2+3, 8
    # for i, attr_ans in enumerate(["1: 品質", "2: 価格", "3: 銘柄"]):
    #     attr_dict = {0: "quality", 1: "price", 2: "brand"}

    #     plt.title("アンケート結果 - {}".format(attr_dict[i]), fontproperties=fp)
    #     plt.xlabel("設問2+3", fontproperties=fp)
    #     plt.ylabel("設問8", fontproperties=fp)
    #     plt.axis("equal")
    #     plt.yticks([1,2,3,4])
    #     plt.grid(linestyle="dashed") # 破線のグリッド

    #     # proposal2_3から、属性ごとの回答データを抽出
    #     proposal_attr = df_proposal[df_proposal[questions_proposal[2]].isin([attr_ans])]
    #     print(proposal_attr)
    #     if i == 0:
    #         plt.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[8]], s=300, c="red", marker='o', alpha=0.3)
    #     elif i == 1:
    #         plt.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[8]], s=300, c="green", marker='o', alpha=0.3)
    #     elif i == 2:
    #         plt.scatter(x=proposal_attr[questions_proposal[3]], y=proposal_attr[questions_proposal[8]], s=300, c="blue", marker='o', alpha=0.3)
    #     plt.savefig("./my_sotuken_figs/q2+3_8-{}.png".format(attr_dict[i])) # プロットした図を画像として保存する
    #     ax.cla()

    # 設問4, 5+6
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    ax.set_title("アンケート結果", fontproperties=fp)
    ax.set_xlabel("設問4", fontproperties=fp)
    ax.set_ylabel("設問5+6", fontproperties=fp)
    ax.grid(linestyle="dashed") # 破線のグリッド
    
    # 更に、類似商品が提示されたユーザの回答データのみを抽出
    proposal_sim_product = df_proposal[df_proposal[questions_proposal[5]] == "はい"]
    print(proposal_sim_product)

    ax.scatter(x=proposal_sim_product[questions_proposal[4]], y=proposal_sim_product[questions_proposal[6]], s=300, marker='o', alpha=0.3)
    plt.savefig("./my_sotuken_figs/q4_5+6.png") # プロットした図を画像として保存する
    ax.cla()

    # 設問4, 7
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    ax.set_title("アンケート結果", fontproperties=fp)
    ax.set_xlabel("設問4", fontproperties=fp)
    ax.set_ylabel("設問7", fontproperties=fp)
    ax.grid(linestyle="dashed") # 破線のグリッド
    ax.scatter(x=proposal4, y=proposal7, s=300, marker='o', alpha=0.3)
    plt.savefig("./my_sotuken_figs/q4_7.png") # プロットした図を画像として保存する
    ax.cla()

    # 設問4, 8
    # ax.set_title("アンケート結果", fontproperties=fp)
    # ax.set_xlabel("設問4", fontproperties=fp)
    # ax.set_ylabel("設問8", fontproperties=fp)
    # ax.grid(linestyle="dashed") # 破線のグリッド
    # ax.scatter(x=proposal4, y=proposal8, s=300, marker='o', alpha=0.3)
    # plt.savefig("./my_sotuken_figs/q4_8.png") # プロットした図を画像として保存する
    # ax.cla()

    # 設問5+6, 7
    ax.set_xlim([0,5]) # 1~4
    ax.set_xticks([0,1,2,3,4,5]) # 1~4
    ax.set_ylim([0,5]) # 1~4
    ax.set_yticks([0,1,2,3,4,5]) # 1~4
    ax.set_title("アンケート結果", fontproperties=fp)
    ax.set_xlabel("設問5+6", fontproperties=fp)
    ax.set_ylabel("設問7", fontproperties=fp)
    ax.grid(linestyle="dashed") # 破線のグリッド
    
    # 更に、類似商品が提示されたユーザの回答データのみを抽出
    proposal_sim_product = df_proposal[df_proposal[questions_proposal[5]] == "はい"]
    print(proposal_sim_product)

    ax.scatter(x=proposal_sim_product[questions_proposal[6]], y=proposal_sim_product[questions_proposal[7]], s=300, marker='o', alpha=0.3)
    plt.savefig("./my_sotuken_figs/q5+6_7.png") # プロットした図を画像として保存する
    ax.cla()

    # 設問5+6, 8
    # plt.title("アンケート結果", fontproperties=fp)
    # plt.xlabel("設問5+6", fontproperties=fp)
    # plt.ylabel("設問8", fontproperties=fp)
    # plt.axis("equal")
    # plt.yticks([1,2,3,4])
    # plt.grid(linestyle="dashed") # 破線のグリッド
    
    # # 更に、類似商品が提示されたユーザの回答データのみを抽出
    # proposal_sim_product = df_proposal[df_proposal[questions_proposal[5]] == "はい"]
    # print(proposal_sim_product)

    # plt.scatter(x=proposal_sim_product[questions_proposal[6]], y=proposal_sim_product[questions_proposal[8]], s=300, marker='o', alpha=0.3)
    # plt.savefig("./my_sotuken_figs/q5+6_8.png") # プロットした図を画像として保存する
    # ax.cla()

    # 設問7, 8
    # plt.title("アンケート結果", fontproperties=fp)
    # plt.xlabel("設問7", fontproperties=fp)
    # plt.ylabel("設問8", fontproperties=fp)
    # plt.xticks([1,2,3,4])
    # plt.yticks([0,1])
    # plt.grid(linestyle="dashed") # 破線のグリッド
    # plt.scatter(x=proposal7, y=proposal8, s=300, marker='o', alpha=0.3)
    # plt.savefig("./my_sotuken_figs/q7_8.png") # プロットした図を画像として保存する
    # ax.cla()

    # print(df_proposal.isnull()[proposal1.name])

def plot_experiment_results():
    plot_prev_system_results()
    print("先行研究のグラフ全部保存完了")
    plot_proposal_system_results()
    print("本研究のグラフ全部保存完了")
    print("全部保存できた")

if __name__ == "__main__":
    plot_experiment_results()
