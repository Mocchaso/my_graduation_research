import re
import nltk
from nltk import ngrams
from nltk.corpus import stopwords

class Parser:
    def __init__(self):
        self.question_words = set(['what', 'when', 'where', 'why', 'which', 'who', 'whose', 'how', 'do', 'did', 'does', 'are', 'is', 'would', 'will', 'can', 'could', 'any'])
        self.neg_words = set(['no', 'not', "n't", "nothing", "dont"]) # 関連研究のコードでは"n't"までしか入っていなかったが、論文内のマッチングパターンに準拠した
        nltk.download('stopwords')
        self.stopwords = set(stopwords.words('english'))
        self.stopwords.update(['may', 'might', 'rent', 'new', 'brand', 'low', 'high', 'now', 'available'])
        self.vague_price_patterns = [
                r'come down',
                r'(highest|lowest)',
                r'go (lower|higher)',
                r'too (high|low)',
                ]
        self.greeting_patterns = [ # 関連研究のコードのgreeting_wordsを、本研究では1つの正規表現パターンにまとめた
                r'hi',
                r'hello',
                r'hey',
                r'hiya',
                r'howdy'
                r'how are you',
                r'interested in',
                ]
        self.agreement_patterns = [
            r'^that works[.!]*$',
            r'^great[.!]*$',
            r'^(ok|okay)[.!]*$',
            r'^great, thanks[.!]*$',
            r'^deal[.!]*$',
            r'^[\w ]*have a deal[\w ]*$',
            r'^i can do that[.]*$',
        ]
        self.qa_attr = None # inquire or informされている属性を記録する変数
        self.proposed_price = None # 現時点で提示されている価格を記録する変数

    def is_greeting(self, utterance):
        for pattern in self.greeting_patterns:
            if re.search(pattern, utterance, re.IGNORECASE):
                return True
        return False

    def is_negative(self, utterance):
        for pattern in self.neg_words:
            if re.search(pattern, utterance, re.IGNORECASE):
                return True
        return False
    
    def is_agreement(self, utterance):
        for pattern in self.agreement_patterns:
            if re.search(pattern, utterance, re.IGNORECASE):
                return True
        return False

    def is_insistence(self, utterance):
        """
        本研究で独自に定義
        """
        # 以前現れたofferと同じofferが検出された時
        # OFFER {"price":800.0,"sides": ""}
        return True

    def is_question(self, utterance):
        tokens = utterance.split()
        if "how are you" in utterance or len(tokens) < 1:
            return False
        last_word = tokens[-1]
        first_word = tokens[0]
        return last_word == '?' or first_word in self.question_words

    def is_proposal(self, utterance):
        """
        本研究で独自に定義
        """
        # 初めて価格に言及された時
        return True

    def is_vague_price(self, utterance):
        for pattern in self.vague_price_patterns:
            if re.search(pattern, utterance, re.IGNORECASE):
                return True
        return False
    
    def is_counter(self, utterance):
        """
        本研究で独自に定義
        """
        # 新しい価格提示が検出された時
        return True
    
    def is_information(self, utterance):
        """
        本研究で独自に定義
        """
        # 以前の対話行為がinquireだった時
        return True

    def compare(self, system_price, user_price, inc=1):
        """Compare two prices.
        Args:
            system_price (float)
            user_price (float)
            inc (float={1,-1}): 1 means higher is better and -1 mean lower is better.
            ※本研究では、システム（seller）がユーザ（buyer）に価格交渉を持ちかける場合に限定しているため、inc=1で固定となる
        """
        inc = 1
        if system_price == user_price:
            r = 0
        elif system_price < user_price:
            r = -1
        else:
            r = 1
        r *= inc
        return r
    
    def classify_dialogue_act(self, utterance):
        """
        本研究では、関連研究のtag_utteranceを無くして直に分類させている
        """
        intent = None
        if self.is_greeting(utterance):
            intent = 'intro'
        if self.is_negative(utterance):
            intent = 'disagree'
        if self.is_agreement(utterance):
            intent = 'agree'
        # if self.is_insistence(utterance):
        #    intent = 'insist'
        if self.is_question(utterance):
            intent = 'inquire(attr)'
        #if self.is_proposal(utterance):
        #    intent = 'propose(price)'
        if self.is_vague_price(utterance):
            intent = 'vague-price'
        #if self.is_counter(utterance):
        #    intent = 'counter(price)'
        #if self.is_information(utterance):
        #    intent = 'inform(attr)'
        if intent == None:
            intent = 'unknown'
        return intent
