# 结果包装器， 回答组织器
from types import FunctionType


def iter_one_name(data: list, names: list,
                  ok_pattern: FunctionType,
                  none_pattern: FunctionType) -> str:
    """ 制造查询值与查询名称一一对应的回答。

    :param data: 查询结果
    :param names: 查询名称
    :param ok_pattern: 句子模板，有值时使用。提供两个参数：item（值）, name（对应名称）
    :param none_pattern: 句子模板，无值时使用。提供一个参数：name（对应名称）
    :return: 回答
    """
    answers = []
    for item, name in zip(data, names):
        if item is None:
            answer = none_pattern(name)
        else:
            answer = ok_pattern(item, name)
        answers.append(answer)
    return '；'.join(answers)


def iter_cross_name(data: list, main_names: list, sub_names: list,
                    ok_pattern: FunctionType,
                    none_pattern: FunctionType) -> str:
    """ 制造查询值与主副名称交叉对应的回答。

    :param data: 查询结果
    :param main_names: 查询主循环名称
    :param sub_names: 查询次循环名称
    :param ok_pattern: 句子模板，有值时使用。提供两个参数：item（值）, main_name（主名称），sub_name（副名称）
    :param none_pattern: 句子模板，无值时使用。提供一个参数：main_name（主名称），sub_name（副名称）
    :return:
    """
    assert len(main_names) * len(sub_names) == len(data)

    answers = []
    i = 0
    for main in main_names:
        for sub in sub_names:
            item = data[i]
            if item:
                answer = ok_pattern(item, main, sub)
            else:
                answer = none_pattern(main, sub)
            i += 1
            answers.append(answer)
    return '；'.join(answers)
