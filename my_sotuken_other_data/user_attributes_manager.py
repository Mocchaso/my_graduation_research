class AnswerRangeError(Exception):
    """
    対話前のアンケートで1～5以外の値が入力された時の例外をキャッチするクラス
    """
    def __str__(self):
        return "inputted value is out of range as the answer!"

class UserAttributesManager:
    """
    説得対話スタート前のアンケートに回答してもらった結果を管理するクラス
    """

    def __init__(self):
        self.quality = 0 # 品質
        self.price = 0 # 価格（お得感）
        self.intuition = 0 # 感性・直感
        self.efficiency = 0 # 効率
        self.brand = 0 # 銘柄
        self.information = 0 # 情報
        self.trend = 0 # 流行
        self.answer_dict = {} ### 回答結果を記録しておく辞書
        self.attributes_priority = [] ### 最終的な優先順位を記録するリスト
    
    def execute_questionnaire(self):
        """
        アンケートを実施する
        各項目で、文字列 or 小数 or 1～5以外の整数が入力されたら再度入力させる
        """
        print("あなたが商品を購入するとき、重視する項目の度合いを5段階で回答してください。")
        print("5：当てはまる, 4：まあ当てはまる, 3：どちらともいえない, 2：あまり当てはまらない, 1：当てはまらない")
        print("\n")
        while True:
            try:
                # 品質
                self.quality = int(input("品質 -> "))
                if self.quality < 1 or self.quality > 5:
                    raise AnswerRangeError() # 1～5の範囲外が入力された時
                # 価格（お得感）
                self.price = int(input("価格（お得感） -> "))
                if self.price < 1 or self.price > 5:
                    raise AnswerRangeError() # 1～5の範囲外が入力された時
                # 感性・直感
                self.intuition = int(input("感性・直感 -> "))
                if self.intuition < 1 or self.intuition > 5:
                    raise AnswerRangeError() # 1～5の範囲外が入力された時
                # 効率
                self.efficiency = int(input("効率 -> "))
                if self.efficiency < 1 or self.efficiency > 5:
                    raise AnswerRangeError() # 1～5の範囲外が入力された時
                # 銘柄
                self.brand = int(input("銘柄 -> "))
                if self.brand < 1 or self.brand > 5:
                    raise AnswerRangeError() # 1～5の範囲外が入力された時
                # 情報
                self.information = int(input("情報 -> "))
                if self.information < 1 or self.information > 5:
                    raise AnswerRangeError() # 1～5の範囲外が入力された時
                # 流行
                self.trend = int(input("流行 -> "))
                if self.trend < 1 or self.trend > 5:
                    raise AnswerRangeError() # 1～5の範囲外が入力された時
            except (ValueError, AnswerRangeError) as e:
                print(e)
            else: # 例外をキャッチしなければ入力終了
                self.answer_dict = {
                    "quality": self.quality, "price": self.price, "intuition": self.intuition,
                    "efficiency": self.efficiency, "brand": self.brand,
                    "information": self.information, "trend": self.trend
                }
                print("全ての項目が正常に入力されました")
                break
    
    def update_priorityList(self):
        """
        回答結果を基に、対話で考慮するパラメータの優先順位を記録する
        """
        for k, v in sorted(self.answer_dict.items(), key=lambda x:x[1], reverse=True):
            self.attributes_priority.append((k, v))
