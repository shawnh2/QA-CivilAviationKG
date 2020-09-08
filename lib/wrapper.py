# 结果包装器， 回答组织器
from types import FunctionType
from itertools import product

__all__ = ['iter_with_name', 'iter_with_bcmp']


def product_name(*name: list):
    """ 对传入的名称进行笛卡尔积 """
    for n in product(*name):
        yield n


def repeat_feed(feeds: list, n: int):
    """ 对传入的列表元素每个重复n次迭代 """
    count = 0
    i = 0
    for _ in range(len(feeds)*n):
        yield feeds[i]
        count += 1
        if count == n:
            count = 0
            i += 1


def iter_with_name(data: list, *names: list,
                   ok_pattern: FunctionType,
                   none_pattern: FunctionType) -> str:
    """ 制造查询值与查询名称相互对应的回答。

    :param data: 查询结果
    :param names: 查询名称，按主次顺序依次传入
    :param ok_pattern: 句子模板，有值时使用。提供两个参数：item（值）, name（对应名称）
    :param none_pattern: 句子模板，无值时使用。提供一个参数：name（对应名称）
    :return: 回答
    """
    answers = []
    for item, name in zip(data, product_name(*names)):
        if item is None:
            answer = none_pattern(*name)
        else:
            answer = ok_pattern(item, *name)
        answers.append(answer)
    return '；'.join(answers)


def iter_with_bcmp(data: tuple, *names: list,
                   binary_cmp_and_patterns: list,
                   err_pattern: FunctionType,
                   x_none_pattern: FunctionType,
                   y_none_pattern: FunctionType,
                   all_none_pattern: FunctionType) -> str:
    """ 制造涉及二元运算的回答。

    :param data: 查询结果
    :param names: 查询名称
    :param binary_cmp_and_patterns: 元组列表，包括一个二元计算函数和一个句子模板，后者提供五个参数：result（二元计算结果），n（对应名称），x（值），y（值），f（中间值）
    :param err_pattern: 句子模板，值错误时使用。提供一个参数：name（对应名称）
    :param x_none_pattern: 句子模板，无x值时使用。提供参数：name（对应名称）
    :param y_none_pattern: 句子模板，无y值时使用。提供参数：name（对应名称）
    :param all_none_pattern: 句子模板，无x,y值时使用。提供参数：name（对应名称）
    :return: 回答
    """
    answers = []
    item1, item2, feed = data
    for x, y, f, n in zip(item1, item2, repeat_feed(feed, len(item2)//len(feed)), product_name(*names)):
        if x and y:
            sub_answers = []
            for cmp_func, ok_pattern in binary_cmp_and_patterns:
                sent = ''
                try:
                    if cmp_func:
                        result = round(cmp_func(x, y), 3)
                    else:
                        result = None
                    sent = ok_pattern(result, *n, x, y, f)
                except ValueError:
                    sent = err_pattern(*n)
                finally:
                    sub_answers.append(sent)
            answer = '，'.join(sub_answers)
        elif not x:
            answer = x_none_pattern(*n)
        elif not y:
            answer = y_none_pattern(*n)
        else:
            answer = all_none_pattern(*n)
        answers.append(answer)

    return '；'.join(answers)
