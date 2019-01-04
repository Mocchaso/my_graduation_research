from user_attributes_manager import UserAttributesManager
from parser_dialogue_act import Parser
import sys

if __name__ == "__main__":
    parser = Parser()
    uam = UserAttributesManager()
    # 買い物属性に関するアンケートに回答してもらう
    uam.execute_questionnaire()
    uam.update_priorityList()
    result = uam.attributes_priority
    print(result)

    """
    while True:
        print("test of parsing dialogue act")
        user = input("input utterance >> ")
        print(parser.classify_dialogue_act(user))
    """