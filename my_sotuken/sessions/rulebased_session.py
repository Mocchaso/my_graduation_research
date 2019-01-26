# coding: utf-8
# changed part: 文字コードの指定

import random
import re
import logging
import numpy as np
from collections import namedtuple
from itertools import izip

from cocoa.core.entity import is_entity
from cocoa.core.event import Event
from cocoa.model.parser import LogicalForm as LF
from cocoa.sessions.rulebased_session import RulebasedSession as BaseRulebasedSession

from core.tokenizer import tokenize, detokenize
from model.parser import Parser, Utterance
from model.dialogue_state import DialogueState

### changed part
from cocoa.core.util import read_json # 類似商品の情報を読み込むために追加
from user_attributes_manager import UserAttributesManager as uam # ユーザの買い物属性を考慮して発話文生成を行うために追加
from decimal import Decimal, ROUND_HALF_UP # 円ドル変換後の四捨五入に使用
# ネガポジ判定に使用
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
###

class RulebasedSession(object):
    @classmethod
    def get_session(cls, agent, kb, lexicon, config, generator, manager):
        if kb.role == 'buyer':
            return BuyerRulebasedSession(agent, kb, lexicon, config, generator, manager)
        elif kb.role == 'seller':
            return SellerRulebasedSession(agent, kb, lexicon, config, generator, manager)
        else:
            raise ValueError('Unknown role: %s', kb.role)

Config = namedtuple('Config', ['overshoot', 'bottomline_fraction', 'compromise_fraction', 'good_deal_threshold'])

default_config = Config(.2, .5, .5, .7)

class CraigslistRulebasedSession(BaseRulebasedSession):
    def __init__(self, agent, kb, lexicon, config, generator, manager):
        parser = Parser(agent, kb, lexicon)
        state = DialogueState(agent, kb)
        super(CraigslistRulebasedSession, self).__init__(agent, kb, parser, generator, manager, state, sample_temperature=10.)

        self.kb = kb
        self.title = self.shorten_title(self.kb.facts['item']['Title'])
        self.config = default_config if config is None else config

        self.target = self.kb.target
        self.bottomline = None
        self.listing_price = self.kb.listing_price
        self.category = self.kb.category

        # Direction of desired price
        self.inc = None

        ### changed part:
        self.policy_mode = 1 # 各ポリシーの対話モード(1: 通常の価格の提案, 2, 3は各ポリシーに後述)
        self.similar_products_json = read_json("./data/my_additional_info/similar_products_info.json")
        nltk.download("vader_lexicon") # ネガポジ判定に必要なモデルをダウンロード
        ###

    def shorten_title(self, title):
        """If the title is too long, shorten it using a generic name for filling in the templates.
        """
        if len(title.split()) > 3:
            if self.kb.category == 'car':
                return 'car'
            elif self.kb.category == 'housing':
                return 'apartment'
            elif self.kb.category == 'phone':
                return 'phone'
            elif self.kb.category == 'bike':
                return 'bike'
            else:
                return 'item'
        else:
            return title

    @classmethod
    def get_fraction(cls, zero, one, fraction):
        """Return the point at a specific fraction on a line segment.

        Given two points "zero" and "one", return the point in the middle that
        divides the segment by the ratio fraction : (1 - fraction).

        Args:
            zero (float): value at point "zero"
            one (float): value at point "one"
            fraction (float)

        Returns:
            float

        """
        return one * fraction + zero * (1. - fraction)

    def round_price(self, price):
        """Round the price so that it's not too specific.
        """
        if price == self.target:
            return price
        if price > 100:
            return int(round(price, -1))
        if price > 1000:
            return int(round(price, -2))
        return int(round(price))

    def estimate_bottomline(self):
        raise NotImplementedError

    def init_price(self):
        """Initial offer.
        """
        raise NotImplementedError

    def receive(self, event):
        super(CraigslistRulebasedSession, self).receive(event)
        if self.bottomline is None:
            self.bottomline = self.estimate_bottomline()
    
    def yen_to_dollar(self, yen):
        """
        円をドルに変換する
        """
        rate = 109.64
        converted = Decimal(yen / rate)
        result = converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(result)

    def dollar_to_yen(self, dollar):
        """
        ドルを円に変換する
        """
        rate = 109.64
        converted = Decimal(dollar * rate)
        result = converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(result)

    def adjust_ratio_sys_price(self, price, online_price):
        """
        交渉で扱う商品のオンラインストアでの価格から、交渉中に出てくる価格の比率を合わせる
        price: 比率調整の対象となる価格の数値
        """
        adjusted = Decimal(online_price * (price / self.listing_price))
        result = adjusted.quantize(Decimal("1.0"), rounding=ROUND_HALF_UP) # 1の位に四捨五入
        return float(result)

    def is_positive(self, text):
        """
        ネガポジ判定でcompoundが0.5以上ならポジティブとする
        return: True or False
        """
        print("analyzed text: {}".format(text))

        positive_threshold = 0.5 # ポジティブであると見なす閾値
        analyzer = SentimentIntensityAnalyzer()
        all_score = analyzer.polarity_scores(text)
        print("all_score '{}': {}".format(text, all_score))
        compound_score = all_score["compound"]
        return compound_score >= positive_threshold

    def quality_policy(self, mode, sys_thinking_price, estimated_product_name):
        """
        品質重視のユーザに対して新たな発話文生成を行う
        1: 価格の提案（通常モード。追加する情報は無し）
        2: 価格の提案＋提案する価格より少し高い価格の類似商品の商品名と、その品質に関してポジティブなレビュー
        3: 価格の提案＋提案する価格と同じぐらいの価格の類似商品の商品名と、その品質に関してポジティブなレビュー
        """
        # 交渉で扱う商品のオンライン価格を保存
        online_price_yen = 0
        if estimated_product_name == "billy":
            online_price_yen = 6999
        elif estimated_product_name == "erik":
            online_price_yen = 9990
        elif estimated_product_name == "malm":
            online_price_yen = 12990
        elif estimated_product_name == "kullen":
            online_price_yen = 3999
        elif estimated_product_name == "millberget":
            online_price_yen = 9990
        
        if mode == 1:
            return "" # 追加する情報は無し
        elif mode == 2:
            target_price = self.adjust_ratio_sys_price(sys_thinking_price, online_price_yen) * (1 + 0.05) # 類似商品の検索にかける価格を、システムが提案する価格より5%高い価格に設定
        elif mode == 3:
            target_price = self.adjust_ratio_sys_price(sys_thinking_price, online_price_yen) # 類似商品の検索にかける価格を、システムが提案する価格と同じ価格に設定
        
        ### なるべくtarget_priceに近い価格の類似商品の情報を取得する
        price_order = [] # 検索する価格に近い類似商品の価格を、順番を記録する
        similar_products_info = self.similar_products_json[estimated_product_name]
        for i, similar_product in enumerate(similar_products_info):
            # 類似商品の価格と、検索にかけた価格の差を求めて、リストに保存する
            target_diff = abs(similar_product["price_yen"] - target_price)
            price_order.append((i, target_diff))
        price_order.sort(key=lambda x: x[1]) # 検索にかけた価格に近い順に、類似商品の価格情報をソートする

        # 検索にかけた価格に最も近い類似商品を選択する＆一度選ばれた類似商品をデータから削除する
        selected_similar_product = self.similar_products_json[estimated_product_name][price_order[0][0]]
        self.similar_products_json[estimated_product_name].pop(price_order[0][0])

        # quality policyで必要な情報を取得する
        selected_product_name = selected_similar_product["product_name"]
        positive_reviews = [review["en"] for review in selected_similar_product["reviews"] if self.is_positive(review["en"])] # 選ばれた類似商品のレビューのうち、ポジティブなもののみを抽出
        selected_positive_review_en = random.choice(positive_reviews) # ポジティブなレビューをランダムで選択する
        selected_shorten_url = selected_similar_product["shorten_url"]

        # 追加する文章をreturn
        return " / A similar product: '{}', A positive review: '{}', URL: {}".format(selected_product_name, selected_positive_review_en, selected_shorten_url)

    def price_policy(self, mode, sys_thinking_price, estimated_product_name):
        """
        価格重視のユーザに対して新たな発話文生成を行う
        1: 価格の提案（通常モード。追加する情報は無し）
        2: 価格の提案＋提案する価格より少し低い価格の類似商品の商品名とその価格
        3: 価格の提案＋提案する価格より低い価格の類似商品の商品名とその価格（2より低めの価格とする）
        """
        # 交渉で扱う商品のオンライン価格を保存
        online_price_yen = 0
        if estimated_product_name == "billy":
            online_price_yen = 6999
        elif estimated_product_name == "erik":
            online_price_yen = 9990
        elif estimated_product_name == "malm":
            online_price_yen = 12990
        elif estimated_product_name == "kullen":
            online_price_yen = 3999
        elif estimated_product_name == "millberget":
            online_price_yen = 9990
        
        # 提案する価格に、ポリシー内のモードごとの補正＋オンライン価格の補正をかける
        target_price = 0
        if mode == 1:
            return "" # 追加する情報は無し
        elif mode == 2:
            target_price = self.adjust_ratio_sys_price(sys_thinking_price, online_price_yen * (1 - 0.05)) # 類似商品の検索にかける価格を、システムが提案する価格より5%低い価格に設定
        elif mode == 3:
            target_price = self.adjust_ratio_sys_price(sys_thinking_price, online_price_yen * (1 - 0.07)) # 類似商品の検索にかける価格を、システムが提案する価格より7%低い価格に設定
        
        ### なるべくtarget_priceに近い価格の類似商品の情報を取得する
        price_order = [] # 検索する価格に近い類似商品の価格を、順番を記録する
        similar_products_info = self.similar_products_json[estimated_product_name]
        for i, similar_product in enumerate(similar_products_info):
            # 類似商品の価格と、検索にかけた価格の差を求めて、リストに保存する
            target_diff = abs(similar_product["price_yen"] - target_price)
            price_order.append((i, target_diff))
        price_order.sort(key=lambda x: x[1]) # 検索にかけた価格に近い順に、類似商品の価格情報をソートする

        # 検索にかけた価格に最も近い類似商品を選択する＆一度選ばれた類似商品をデータから削除する
        selected_similar_product = self.similar_products_json[estimated_product_name][price_order[0][0]]
        self.similar_products_json[estimated_product_name].pop(price_order[0][0])

        # price policyで必要な情報を取得する
        selected_product_name = selected_similar_product["product_name"]
        selected_product_price = self.yen_to_dollar(selected_similar_product["price_yen"]) # 取得した類似商品の価格をドルに変換しておく
        selected_shorten_url = selected_similar_product["shorten_url"]

        # 追加する文章をreturn
        return " / A similar product: '{}', the price(dollar): '{}', URL: {}".format(selected_product_name, selected_product_price, selected_shorten_url)

    def brand_policy(self, mode, sys_thinking_price, estimated_product_name):
        """
        銘柄重視のユーザに対して新たな発話文生成を行う
        1: 価格の提案（通常モード。追加する情報は無し）
        2: 価格の提案＋提案する価格と同じぐらいの価格で、交渉中の商品より良い銘柄の類似商品の商品名とその価格
        3: 価格の提案＋提案する価格より少し低い価格で、交渉中の商品より良い銘柄の類似商品の商品名とその価格
        """
        # 交渉で扱う商品のオンライン価格を保存
        online_price_yen = 0
        if estimated_product_name == "billy":
            online_price_yen = 6999
        elif estimated_product_name == "erik":
            online_price_yen = 9990
        elif estimated_product_name == "malm":
            online_price_yen = 12990
        elif estimated_product_name == "kullen":
            online_price_yen = 3999
        elif estimated_product_name == "millberget":
            online_price_yen = 9990

        if mode == 1:
            return "" # 追加する情報は無し
        elif mode == 2:
            target_price = self.adjust_ratio_sys_price(sys_thinking_price, online_price_yen) # 類似商品の検索にかける価格を、システムが提案する価格と同じぐらいの価格に設定
        elif mode == 3:
            target_price = self.adjust_ratio_sys_price(sys_thinking_price, online_price_yen * (1 - 0.05)) # 類似商品の検索にかける価格を、システムが提案する価格より5%低い価格に設定
        
        ### なるべくtarget_priceに近い価格の類似商品の情報を取得する
        price_order = [] # 検索する価格に近い類似商品の価格を、順番を記録する
        similar_products_info = self.similar_products_json[estimated_product_name]
        for i, similar_product in enumerate(similar_products_info):
            # 類似商品の価格と、検索にかけた価格の差を求めて、リストに保存する
            target_diff = abs(similar_product["price_yen"] - target_price)
            price_order.append((i, target_diff))
        price_order.sort(key=lambda x: x[1]) # 検索にかけた価格に近い順に、類似商品の価格情報をソートする

        # 検索にかけた価格に最も近い類似商品を選択する＆一度選ばれた類似商品をデータから削除する
        selected_similar_product = self.similar_products_json[estimated_product_name][price_order[0][0]]
        self.similar_products_json[estimated_product_name].pop(price_order[0][0])

        # brand policyで必要な情報を取得する
        selected_product_name = selected_similar_product["product_name"]
        selected_product_price = self.yen_to_dollar(selected_similar_product["price_yen"]) # 取得した類似商品の価格をドルに変換しておく
        selected_product_brand = selected_similar_product["brand"]
        selected_shorten_url = selected_similar_product["shorten_url"]

        # 追加する文章をreturn
        return " / A similar product: '{}', the price(dollar): '{}', the brand: '{}', URL: {}".format(selected_product_name, selected_product_price, selected_product_brand, selected_shorten_url)

    def fill_template(self, template, price=None):
        return template.format(title=self.title, price=(price or ''), listing_price=self.listing_price, partner_price=(self.state.partner_price or ''), my_price=(self.state.my_price or ''))

    def template_message(self, intent, price=None):
        print 'template:', intent, price
        template = self.retrieve_response_template(intent, category=self.kb.category, role=self.kb.role)
        print "template:" # {'category': ..., 'template': ..., 'logp': ..., 'source': 'rule', 'tag': ..., 'role': ..., 'context': ..., 'id': ..., 'context_tag': ...}
        print template

        if '{price}' in template['template']:
            price = price or self.state.my_price
        else:
            price = None

        lf = LF(intent, price=price)
        text = self.fill_template(template['template'], price=price)

        ### changed part: テンプレートに追加情報を付与
        added_text = text # 類似商品の情報を追加するための変数
        if intent == 'counter-price':
            price = (price or '')
            listing_price = self.listing_price
            partner_price = (self.state.partner_price or '')
            my_price = (self.state.my_price or '') # template_messageで考慮されている(244行目)みたいだけど、一応my_priceも用意する

            # システムが考えている価格の提案を記録する（partner_priceは恐らく使わないので除外）
            sys_thinking_price = price
            if sys_thinking_price == '':
                if '{listing_price}' in template['template']:
                    sys_thinking_price = listing_price
                elif '{my_price}' in template['template']:
                    sys_thinking_price = my_price
            print("sys_thinking_price: {}".format(sys_thinking_price))
            print("type(sys_thinking_price): {}".format(type(sys_thinking_price)))

            # シナリオのタイトルから、交渉中の商品の大雑把な商品名を取得
            scenario_title = self.kb.title.lower() # シナリオのタイトルを小文字化
            estimated_product_name = "" 
            if "billy" in scenario_title:
                estimated_product_name = "billy"
            elif "erik" in scenario_title:
                estimated_product_name = "erik"
            elif "malm" in scenario_title:
                estimated_product_name = "malm"
            elif "night stand" in scenario_title:
                estimated_product_name = "kullen"
            elif "millberget" in scenario_title:
                estimated_product_name = "millberget"

            # ユーザの買い物属性ごとに、追加する情報を変化させる
            if uam.answer == 1: # 品質重視のpolicy
                added_text += self.quality_policy(self.policy_mode, sys_thinking_price, estimated_product_name)
            elif uam.answer == 2: # 価格重視のpolicy
                added_text += self.price_policy(self.policy_mode, sys_thinking_price, estimated_product_name)
            elif uam.answer == 3: # 銘柄重視のpolicy
                added_text += self.brand_policy(self.policy_mode, sys_thinking_price, estimated_product_name)
            print("added_text: {}".format(added_text))

            # 提案を終えたら、ポリシーを動かすモードを変更する
            if self.policy_mode == 1:
                self.policy_mode = 2
            elif self.policy_mode == 2:
                self.policy_mode = 3
        ###

        utterance = Utterance(raw_text=added_text, logical_form=lf, template=template)
        return self.message(utterance)

    def _compromise_price(self, price):
        partner_price = self.state.partner_price if self.state.partner_price is not None else self.bottomline
        if partner_price is None:
            # TODO: make it a parameter
            my_price = price * (1 - self.inc * 0.1)
        else:
            my_price = self.get_fraction(partner_price, price, self.config.compromise_fraction)
        my_price = self.round_price(my_price)
        # Don't go below bottomline
        if self.bottomline is not None and self.compare(my_price, self.bottomline) <= 0:
            return self.bottomline
        else:
            return my_price

    def compromise(self):
        if self.bottomline is not None and self.compare(self.state.my_price, self.bottomline) <= 0:
            return self.final_call()

        self.state.my_price = self._compromise_price(self.state.my_price)
        if self.state.partner_price and self.compare(self.state.my_price, self.state.partner_price) < 0:
            return self.agree(self.state.partner_price)

        return self.template_message('counter-price')

    def offer(self, price):
        utterance = Utterance(logical_form=LF('offer', price=price))
        self.state.update(self.agent, utterance)
        metadata = self.metadata(utterance)
        return super(BaseRulebasedSession, self).offer({'price': price}, metadata=metadata)

    def accept(self):
        utterance = Utterance(logical_form=LF('accept'))
        self.state.update(self.agent, utterance)
        metadata = self.metadata(utterance)
        return super(BaseRulebasedSession, self).accept(metadata=metadata)

    def reject(self):
        utterance = Utterance(logical_form=LF('reject'))
        self.state.update(self.agent, utterance)
        metadata = self.metadata(utterance)
        return super(BaseRulebasedSession, self).reject(metadata=metadata)

    def agree(self, price):
        self.state.my_price = price
        return self.template_message('agree', price=price)

    def deal(self, price):
        if self.bottomline is None:
            return False
        good_price = self.get_fraction(self.bottomline, self.target, self.config.good_deal_threshold)
        # Seller
        if self.inc == 1 and (
                price >= min(self.listing_price, good_price) or \
                price >= self.state.my_price
                ):
            return True
        # Buyer
        if self.inc == -1 and (
                price <= good_price or\
                price <= self.state.my_price
                ):
            return True
        return False

    def no_deal(self, price):
        if self.compare(price, self.state.my_price) >= 0:
            return False
        if self.bottomline is not None:
            if self.compare(price, self.bottomline) < 0 and abs(price - self.bottomline) > 1:
                return True
        else:
            return True
        return False

    def final_call(self):
        lf = LF('final_call', price=self.bottomline)
        template = self._final_call_template()
        text = template.format(price=self.bottomline)
        utterance = Utterance(raw_text=text, logical_form=lf, template=template)
        return self.message(utterance)

    def compare(self, x, y):
        """Compare prices x and y.

        For the seller, higher is better; for the buyer, lower is better.

        Args:
            x (float)
            y (float)

        Returns:
            -1: y is a better price
            0: x and y is the same
            1: x is a better price

        """
        raise NotImplementedError

    def send(self):
        if self.has_done('offer'):
            return self.wait()

        if self.state.partner_act == 'offer':
            if self.no_deal(self.state.partner_price):
                return self.reject()
            return self.accept()

        # if self.state.partner_act in ['init_price', 'counter-price']
        if self.state.partner_price is not None and self.deal(self.state.partner_price):
            return self.agree(self.state.partner_price)

        if self.has_done('final_call'):
            return self.offer(self.bottomline if self.compare(self.bottomline, self.state.partner_price) > 0 else self.state.partner_price)

        action = self.choose_action()
        if action in ('counter-price', 'vague-price'):
            return self.compromise()
        elif action == 'offer':
            return self.offer(self.state.curr_price)
        elif action == 'agree':
            return self.agree(self.state.curr_price)
        elif action == 'unknown':
            return self.compromise()
        else:
            return self.template_message(action)

        raise Exception('Uncaught case')

class SellerRulebasedSession(CraigslistRulebasedSession):
    def __init__(self, agent, kb, lexicon, config, generator, manager):
        super(SellerRulebasedSession, self).__init__(agent, kb, lexicon, config, generator, manager)
        # Direction of desired price
        self.inc = 1.
        self.init_price()

    def estimate_bottomline(self):
        if self.state.partner_price is None:
            return None
        else:
            return self.get_fraction(self.state.partner_price, self.listing_price, self.config.bottomline_fraction)

    def init_price(self):
        # Seller: The target/listing price is shown.
        self.state.my_price = self.target

    def compare(self, x, y):
        if x == y:
            return 0
        elif x < y:
            return -1
        else:
            return 1

    def _final_call_template(self):
        s = (
                "The absolute lowest I can do is {price}",
                "I cannot go any lower than {price}",
                "{price} or you'll have to go to another place",
            )
        return random.choice(s)

class BuyerRulebasedSession(CraigslistRulebasedSession):
    def __init__(self, agent, kb, lexicon, config, generator, manager):
        super(BuyerRulebasedSession, self).__init__(agent, kb, lexicon, config, generator, manager)
        # Direction of desired price
        self.inc = -1.
        self.init_price()

    def estimate_bottomline(self):
        return self.get_fraction(self.listing_price, self.target, self.config.bottomline_fraction)

    def init_price(self):
        self.state.my_price = self.round_price(self.target * (1 + self.inc * self.config.overshoot))

    def compare(self, x, y):
        if x == y:
            return 0
        elif x < y:
            return 1
        else:
            return -1

    def _final_call_template(self):
        s = (
                "The absolute highest I can do is {price}",
                "I cannot go any higher than {price}",
                "{price} is all I have",
            )
        return random.choice(s)
