# 问题的检查
import re
from types import FunctionType

__all__ = ['check_contain', 'check_all_contain', 'check_list_contain', 'check_list_any_contain',
           'check_regexp', 'check_endswith']


def check_contain(words: list, question: str) -> bool:
    """检查是否有包含关系"""
    for word in words:
        if word in question:
            return True
    return False


def check_all_contain(words: list, question: str) -> bool:
    """检查是否全部包含"""
    for word in words:
        if word not in question:
            return False
    return True


def check_list_contain(words: list, dst: list, *pos: int, not_: int = None) -> bool:
    """检查列表中指定位置的包含关系, 有一个不存在即为假, not_即不能存在的位置"""
    for i in pos:
        if not check_contain(words, dst[i]):
            return False
    if not_ and check_contain(words, dst[not_]):
        return False
    return True


def check_list_any_contain(words: list, dst: list, *pos: int) -> bool:
    """检查列表中指定位置的包含关系, 有一个存在即为真"""
    for i in pos:
        if check_contain(words, dst[i]):
            return True
    return False


def check_endswith(words: list, question: str) -> bool:
    """检查尾部关系"""
    return question.endswith(tuple(words))


def check_regexp(question: str, *patterns: str, functions: list, callback: FunctionType = None) -> bool:
    """ 检查正则关系

    :param question: 问题
    :param patterns: 正则表达式
    :param functions: 为每个正则表达式的匹配结果调用
    :param callback: 在function调用后结果为假时使用
    :return: 假值 或 真值
    """
    for pattern, function in zip(patterns, functions):
        results = re.compile(pattern).findall(question)
        if results:
            value = function(results)
            if not value:
                if callback:
                    callback(results)
                return False
            else:
                return True
    return False
