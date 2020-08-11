# 问题的检查
import re
from types import FunctionType


def check_contain(words: list, question: str) -> bool:
    # 检查包含关系
    for word in words:
        if word in question:
            return True
    return False


def check_endswith(words: list, question: str) -> bool:
    # 检查尾部关系
    return question.endswith(tuple(words))


def check_regexp(pattern: str, question: str, function: FunctionType, callback: FunctionType = None) -> bool:
    # 检查正则关系
    results = re.compile(pattern).findall(question)
    if results:
        value = function(results)
        # 值为假时调用callback
        if callback and not value:
            callback(results)
        else:
            return value
    return False
