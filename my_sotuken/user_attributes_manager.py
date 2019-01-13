# coding: utf-8

class AnswerRangeError(Exception):
    """
    In previous questoinnaire, catch exception when inputted values except 1 ~ 5
    """
    def __str__(self):
        return "inputted value is out of range as the answer!"

class UserAttributesManager:
    """
    questionnaire result manager
    """
    answer = None
    
    def execute_questionnaire(self):
        """
        do questionnaire
        re-input when inputted str or float or int except 1 ~ 4
        """
        print("\n買い物をする際、あなたが最も重視する点は何ですか？")
        print("1: 品質, 2: 価格, 3: 銘柄\n")
        while True:
            try:
                UserAttributesManager.answer = int(raw_input("回答（1～3） -> ")) # cocoaの環境が2.7なのでraw_input
                if UserAttributesManager.answer < 1 or UserAttributesManager.answer > 3:
                    raise AnswerRangeError()
            except (ValueError, AnswerRangeError) as e:
                print(e)
            else: # finish inputting when did not catch exception
                print("finished all correctly.")
                break