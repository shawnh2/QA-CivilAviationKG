# 问题的检查
import re
from types import FunctionType

__all__ = ['check_contain', 'check_all_contain', 'check_list_contain', 'check_list_any_contain',
           'check_regexp', 'check_endswith']


def check_contain(words: list, question: str) -> bool:
    # 检查包含关系
    for word in words:
        if word in question:
            return True
    return False


def check_all_contain(words: list, question: str) -> bool:
    # 检查是否全部包含
    count = 0
    for word in words:
        if word in question:
            count += 1
    return count == len(words)


def check_list_contain(words: list, dst: list, *pos: int) -> bool:
    # 检查列表中指定位置的包含关系
    for i in pos:
        # 有一个不存在就为假
        if not check_contain(words, dst[i]):
            return False
    return True


def check_list_any_contain(words: list, dst: list, *pos: int) -> bool:
    # 检查列表中指定位置的包含关系
    for i in pos:
        # 有一个存在即为真
        if check_contain(words, dst[i]):
            return True
    return False


def check_endswith(words: list, question: str) -> bool:
    # 检查尾部关系
    return question.endswith(tuple(words))


def check_regexp(question: str, *patterns: str, functions: list, callback: FunctionType = None) -> bool:
    # 检查正则关系
    for pattern, function in zip(patterns, functions):
        results = re.compile(pattern).findall(question)
        if results:
            value = function(results)
            # 值为假时调用callback
            if callback and not value:
                callback(results)
            else:
                return value
    return False
