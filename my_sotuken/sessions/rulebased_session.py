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
from cocoa.analysis.utils import get_total_turns # 対話の経過ターン数によってポリシーの挙動を変えるのに用いる
from web.main.backend import Backend # my_sotukenのbackend ... get_total_turnsで引数をとる準備に用いる
from cocoa.web.views.utils import userid # ユーザIDの取得に用いる
from web.main.db_reader import DatabaseReader # my_sotukenのdb_reader
import sqlite3 # chat_state.dbへのアクセスに使用
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
        self.prev_total_turns = 0 # 前回価格の提案をした時の経過ターン数を記録する
        self.backend = Backend.get_backend() # get_total_turnsで引数をとる準備に用いる
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

    def fill_template(self, template, price=None):
        return template.format(title=self.title, price=(price or ''), listing_price=self.listing_price, partner_price=(self.state.partner_price or ''), my_price=(self.state.my_price or ''))
    
    def quality_policy(self, mode):
        """
        品質重視のユーザに対して新たな発話文生成を行う
        1: 価格の提案（通常モード。追加する情報は無し）
        2: 売り手が出そうとした価格より少し高い価格の提案＋その価格に近い類似商品の、商品名と品質に関してポジティブなレビュー
        3: 売り手が出そうとした価格と同じぐらいの価格の提案＋その価格に近い類似商品の、商品名と品質に関してポジティブなレビュー
        """
        if mode == 1:
            return u"あ"
        elif mode == 2:
            a
        elif mode == 3:
            a
        return a

    def price_policy(self, mode):
        """
        価格重視のユーザに対して新たな発話文生成を行う
        1: 価格の提案（通常モード。追加する情報は無し）
        2: 売り手が出そうとした価格より少し低い価格の提案＋その価格に近い類似商品の商品名
        3: 更に低い価格の提案＋その価格に近い類似商品の商品名
        """
        if mode == 1:
            return ""
        elif mode == 2:
            a
        elif mode == 3:
            a
        return a

    def brand_policy(self, mode):
        """
        銘柄重視のユーザに対して新たな発話文生成を行う
        1: 価格の提案（通常モード。追加する情報は無し）
        2: 売り手が出そうとした価格と同じぐらいの価格の提案＋その価格に近く、交渉中の商品より良い銘柄の類似商品
        3: 売り手が出そうとした価格より少し低い価格の提案＋その価格に近く、交渉中の商品より良い銘柄の類似商品
        """
        if mode == 1:
            return ""
        elif mode == 2:
            a
        elif mode == 3:
            a
        return a

    '''
    def add_quality_info(self, product_name, similar_product_info):
        """
        品質重視のユーザに対して新たな発話文生成を行う
        """
        # 追加する類似商品の情報をどの銘柄から選ぶかランダムで決める
        key_candidates = ["_ikea1", "_ikea2", "_ikea3", "_nitori1", "_nitori2", "_nitori3", "_muji1", "_muji2", "_muji3"]
        if product_name in ["kullen", "millberget"]: # 交渉中の商品がKULLENかMILLBERGETの場合、類似商品の数が少し合わないためリストの内容を変更
             key_candidates = ["_ikea1", "_ikea2", "_ikea3", "_nitori1", "_nitori2", "_nitori3", "_muji1", "_muji2"]
        key = product_name + random.choice(key_candidates) # どの類似商品の情報を持ってくるかをランダムで決定
        selected_product_of_random_review = random.choice(similar_product_info[key]["reviews"]) # レビュー文をランダムで取得
        selected_product_url = similar_product_info[key]["url"] # 選ばれた商品のページのURL
        if selected_product_of_random_review == []: # ポジティブなレビューが無い場合
            add_info = " / Not found appropriate review of similar product, URL: {}".format(selected_product_url)
            return add_info
        else:
            add_info = " / Review of similar product: {} URL: {}".format(selected_product_of_random_review, selected_product_url) # 英文間の半角スペース付き
            return add_info
    
    def add_price_info(self, product_name, similar_product_info):
        """
        価格重視のユーザに対して新たな発話文生成を行う
        """
        # 追加する類似商品の情報をどの銘柄から選ぶかランダムで決める
        key_candidates = ["_ikea1", "_ikea2", "_ikea3", "_nitori1", "_nitori2", "_nitori3", "_muji1", "_muji2", "_muji3"]
        if product_name in ["kullen", "millberget"]: # 交渉中の商品がKULLENかMILLBERGETの場合、類似商品の数が少し合わないためリストの内容を変更
             key_candidates = ["_ikea1", "_ikea2", "_ikea3", "_nitori1", "_nitori2", "_nitori3", "_muji1", "_muji2"]
        key = product_name + random.choice(key_candidates) # どの類似商品の情報を持ってくるかをランダムで決定
        selected_product_price_dollar = similar_product_info[key]["price_dollar"] # 選ばれた商品のドル価格（オンラインストア表示価格）
        selected_product_url = similar_product_info[key]["url"] # 選ばれた商品のページのURL

        add_info = " / Price of similar product: {} dollars(from online store). URL: {}".format(selected_product_price_dollar, selected_product_url) # 英文間の半角スペース付き
        return add_info
    
    def add_brand_info(self, product_name, similar_product_info):
        """
        銘柄重視のユーザに対して新たな発話文生成を行う
        """
        # 追加する類似商品の情報をどの銘柄から選ぶかランダムで決める
        key_candidates = ["_nitori1", "_nitori2", "_nitori3", "_muji1", "_muji2", "_muji3"] # 実験で使う商品はIKEAの商品のみなので、IKEA以外の類似商品を候補とする
        if product_name in ["kullen", "millberget"]: # 交渉中の商品がKULLENかMILLBERGETの場合、類似商品の数が少し合わないためリストの内容を変更
             key_candidates = ["_ikea1", "_ikea2", "_ikea3", "_nitori1", "_nitori2", "_nitori3", "_muji1", "_muji2"]
        key = product_name + random.choice(key_candidates) # どの類似商品の情報を持ってくるかをランダムで決定
        selected_product_price_dollar = similar_product_info[key]["price_dollar"] # 選ばれた商品のドル価格（オンラインストア表示価格）
        selected_product_brand = similar_product_info[key]["brand"] # 選ばれた商品の銘柄
        selected_product_url = similar_product_info[key]["url"] # 選ばれた商品のページのURL

        add_info = " / Price of similar product, brand {}: {} dollars(from online store). URL: {}".format(selected_product_brand, selected_product_price_dollar, selected_product_url) # 英文間の半角スペース付き
        return add_info
    '''

    def template_message(self, intent, price=None):
        print 'template:', intent, price
        template = self.retrieve_response_template(intent, category=self.kb.category, role=self.kb.role)
        print "templates:" # {'category': ..., 'template': ..., 'logp': ..., 'source': 'rule', 'tag': ..., 'role': ..., 'context': ..., 'id': ..., 'context_tag': ...}
        print template

        ### changed part: テンプレートに追加情報を付与
        if intent == 'counter-price':
            # get_total_turns()の引数にとるデータの準備
            controller = self.backend.controller_map[userid()]
            conn = sqlite3.connect(self.backend.config["db"]["location"])
            cursor = conn.cursor()
            chat_id = controller.get_chat_id()
            scenario_db = self.backend.scenario_db
            print("controller: {}".format(controller))
            print("conn: {}".format(conn))
            print("cursor: {}".format(cursor))
            print("chat_id: {}".format(chat_id))
            print("scenario_db: {}".format(scenario_db))
            ex = DatabaseReader.get_chat_example(cursor, chat_id, scenario_db).to_dict()
            conn.close()

            total_turns = get_total_turns(ex)
            self.prev_total_turns = total_turns # システム側が価格を提案し終わったら、その時点でのターン数を記録(前回の価格の提案から何ターン経過したかを計算するのに用いる)
            print("counter-price...")
            print("total_turns: {}".format(total_turns))
            print("self.prev_total_turns: {}".format(self.prev_total_turns))

            # en_positive_reviews_info = read_json("./data/my_additional_info/en_positive_reviews_info.json") # ポジティブなレビューのみを抽出した類似商品の情報

            # シナリオのタイトルから大雑把な商品名を記録
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
            
            # ポリシーを動かすモードを変更する
            if total_turns - self.prev_total_turns == 2: # 前回の価格の提案から2ターン経過したら
                if self.policy_mode == 1:
                    self.policy_mode = 2
                elif self.policy_mode == 2:
                    self.policy_mode = 3

            # ユーザの買い物属性ごとに、追加する情報を変化させる
            if uam.answer == 1: # 品質重視
                # template["template"] += self.add_quality_info(estimated_product_name, en_positive_reviews_info)
                template["template"] += self.quality_policy(self.policy_mode)
            elif uam.answer == 2: # 価格重視
                # template["template"] += self.add_price_info(estimated_product_name, en_positive_reviews_info)
                template["template"] += self.price_policy(self.policy_mode)
            elif uam.answer == 3: # 銘柄重視
                # template["template"] += self.add_brand_info(estimated_product_name, en_positive_reviews_info)
                template["template"] += self.brand_policy(self.policy_mode)
            
            print "templates(added more info):"
            print template
        ###

        if '{price}' in template['template']:
            price = price or self.state.my_price
        else:
            price = None
        lf = LF(intent, price=price)
        text = self.fill_template(template['template'], price=price)
        utterance = Utterance(raw_text=text, logical_form=lf, template=template)
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
