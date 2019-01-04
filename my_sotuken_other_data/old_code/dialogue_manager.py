class DialogueManager:
    """
    クラス変数
    """
    t = 0 # ターン数
    steps = 0 # ステップ数（ユーザとシステムの発話1往復 = 1ステップ）
    dialogue_history = [] # 対話履歴を記録
    now_suggested_price = None # 現時点での提示価格。システムのpropose(price), ユーザorシステムのcounter(price)によって更新される

    def __init__(self):
        self.inner_states = {
            "user_intent": {
                "interested_in": None, # ユーザが、商品に対して興味を持っているかどうか
                "quality_sat": None, # qualityに満足しているかどうか
                "price_sat": None, # priceに満足しているかどうか
                "intuition_sat": None, # intuitionに満足しているかどうか
                "efficiency_sat": None, # efficiencyに満足しているかどうか
                "brand_sat": None, # brandに満足しているかどうか
                "information_sat": None, # informationに満足しているかどうか
                "trend_sat": None # trendに満足しているかどうか
            }
        }
        self.isAccepted = False # 価格交渉が成立したかがどうか
        self.isFinished = False # 価格交渉が終了したかどうか（成立の可否問わず）

    def select_dialogue_act(self):
        """
        行動選択（seq2seqでやる）
        """
        # 別のスクリプトで学習させたモデルを読み込む
        # 読み込んだモデルを使って、次の発話での対話行為を生成する
        # 生成された対話行為を次の行動として選択する
    
    def update_innner_states(self):
        """
        内部状態の更新
        """