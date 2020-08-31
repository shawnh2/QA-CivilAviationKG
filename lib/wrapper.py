# 结果包装器， 回答组织器
from types import FunctionType


class AnswerWrapper:

    def __init__(self):
        self.no_records = '{name}: 无数据记录！'

    def iter_one_name(self, data: list, names: list, pattern: FunctionType) -> str:
        """ 制造查询值与查询名称一一对应的回答。

        :param data: 查询结果
        :param names: 查询名称
        :param pattern: 句子模板，提供两个参数 item(结果中的项), name(对应的名称)
        :return: 组织好的回答
        """
        answers = []
        for item, name in zip(data, names):
            if item is None:
                answer = self.no_records.format(name=name)
            else:
                answer = pattern(item, name)
            answers.append(answer)
        return '; '.join(answers)
