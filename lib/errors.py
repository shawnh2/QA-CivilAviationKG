# 问题的有关错误
from lib.check import check_contain


class QuestionError(Exception):
    """ 问题中的错误 """


class ParentIndexSequenceError(QuestionError):
    """ 问题中指标与其总体出现的顺序错误
        例：11年总量是港澳台运输总周转量的多少倍？ 【错误】
        》：11年港澳台运输总周转量是总量的多少倍？ 【正确】
    """
    @staticmethod
    def check(results: list, words: list):
        if check_contain(words, results[0][0]):
            raise ParentIndexSequenceError()
