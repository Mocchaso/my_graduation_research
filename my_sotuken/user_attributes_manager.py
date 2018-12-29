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
    attributes_priority = []

    def __init__(self):
        self.condition = 0
        self.price = 0
        # self.sense = 0
        # self.effect = 0
        self.brand = 0
        # self.information = 0
        self.popular = 0
        self.answer_dict = {}
    
    def execute_questionnaire(self):
        """
        do questionnaire
        re-input when inputted str or float or int except 1 ~ 5
        """
        print("\nPlease answer 4 questions about you focus on things when you buy something.")
        print("5: Strong Applicable, 4: Applicable, 3: Neutral, 2: Few Applicable, 1: Not at all\n")
        while True:
            try:
                self.condition = int(input("quality (condition) -> "))
                if self.condition < 1 or self.condition > 5:
                    raise AnswerRangeError()
                
                self.price = int(input("price -> "))
                if self.price < 1 or self.price > 5:
                    raise AnswerRangeError()
                
                """
                self.sense = int(input("intuition (sense) -> "))
                if self.sense < 1 or self.sense > 5:
                    raise AnswerRangeError()
                """
                
                """
                self.effect = int(input("efficiency (effect) -> "))
                if self.effect < 1 or self.effect > 5:
                    raise AnswerRangeError()
                """
                
                self.brand = int(input("brand -> "))
                if self.brand < 1 or self.brand > 5:
                    raise AnswerRangeError()
                
                """
                self.information = int(input("information -> "))
                if self.information < 1 or self.information > 5:
                    raise AnswerRangeError()
                """
                
                self.popular = int(input("trend (popular) -> "))
                if self.popular < 1 or self.popular > 5:
                    raise AnswerRangeError()
            except (ValueError, AnswerRangeError) as e:
                print(e)
            else: # finish inputting when did not catch exception
                self.answer_dict = {
                    "condition": self.condition, "price": self.price,
                    "brand": self.brand, "popular": self.popular
                }
                print("finished all correctly.")
                break
    
    def update_priorityList(self):
        """
        according to questionnaire result, record priority considering parameters in a dialogue
        """
        for k, v in sorted(self.answer_dict.items(), key=lambda x:x[1], reverse=True):
            UserAttributesManager.attributes_priority.append((k, v))
