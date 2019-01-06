# coding: utf-8
# changed part: 文字コードの指定

from cocoa.web.main.utils import Messages as BaseMessages

class Messages(BaseMessages):
    # changed part: 各状況で表示されるテキストの和訳
    # ChatCompleted, ChatIncompleteは英語のままの方が良さそうなのでそのままにした
    # Redirectedは、表示されるタイミングが違うので和訳した
    ChatCompleted = "Great, you reached a final offer!"
    ChatIncomplete = "Sorry, you weren't able to reach a deal. :("
    Redirect = u"申し訳ありません。只今のチャットは長さの基準を満たしていませんでした。"
    """
    ChatCompleted = u"素晴らしい、あなたは最後のオファーに到達しました！"
    ChatIncomplete = u"申し訳ありません、あなたは取引に到達することができませんでした...。"
    Redirect = "Sorry, that chat did not meet our acceptance criteria."
    """

    #BetterDeal = "Congratulations, you got the better deal! We'll award you a bonus on Mechanical Turk."
    #WorseDeal = "Sorry, your partner got the better deal. :("