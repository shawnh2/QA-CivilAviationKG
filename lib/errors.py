# 问题的有关错误
from lib.check import check_contain


class QuestionError(Exception):
    """ 问题错误 """


class QuestionOrderError(QuestionError):
    """ 问句的顺序颠倒错误。
        例.11年总量是港澳台运输总周转量的多少倍？ 【错误】
           11年港澳台运输总周转量是总量的多少倍？ 【正确】
    """
    @staticmethod
    def check(results: list, parent_words: list):
        sent = results[0][0]
        if check_contain(parent_words, sent):
            raise QuestionOrderError(f'不明白你所指的“{sent}”。是问反了吗？')
