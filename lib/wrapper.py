# 结果包装器， 回答组织器
from types import FunctionType
from itertools import product


class Wrapper:

    @classmethod
    def product_name(cls, *name: list):
        """ 对传入的名称进行笛卡尔积 """
        for n in product(*name):
            yield n

    @classmethod
    def product_binary(cls, data: list):
        """ 对传入的数据进行二元输出 """
        mid = len(data) // 2
        start = 0
        end = mid
        while start < mid:
            yield data[start], data[end]
            start += 1
            end += 1

    @classmethod
    def product_repeat(cls, feeds: list, n: int):
        """ 对传入的列表元素每个重复n次迭代 """
        count = 0
        i = 0
        for _ in range(len(feeds)*n):
            yield feeds[i]
            count += 1
            if count == n:
                count = 0
                i += 1

    @classmethod
    def calc_binary(cls, x, y, func: FunctionType) -> float:
        """ 二元计算 """
        return round(func(x, y), 3) if func else None

    def with_name(self, data: list, *names: list,
                  ok_pattern: FunctionType,
                  none_pattern: FunctionType,
                  default_unpack_index: bool = True) -> str:
        """ 制造查询值与查询名称相互对应的回答。

        :param data: 查询结果
        :param names: 查询名称，按主次顺序依次传入
        :param ok_pattern: 句子模板，有值时使用。提供两个参数：item（值）, name（对应名称）
        :param none_pattern: 句子模板，无值时使用。提供一个参数：name（对应名称）
        :param default_unpack_index: 使item的默认拆包位置为0
        :return: 回答
        """
        answers = []
        for item, name in zip(data, self.product_name(*names)):
            if item is None:
                answer = none_pattern(*name)
            else:
                answer = ok_pattern(item[0] if default_unpack_index else item, *name)
            answers.append(answer)
        return '；'.join(answers)

    def with_binary(self, data: list, *names: list, func_and_pattern: list) -> str:
        """ 制造只涉及二元运算的回答，包括单位检查，内置错误语句模板。

        :param data: 查询结果
        :param names: 查询名称
        :param func_and_pattern: 元组列表，包括一个二元计算函数和一个句子模板，后者提供五个参数：res（二元计算结果），x，y（值），n1，n2（名称）
        :return: 回答
        """
        answers = []
        for (x, y), (n1, n2) in zip(self.product_binary(data),
                                    self.product_binary([n for n in self.product_name(*names)])):
            if x and y:
                # 单位检查
                ux, uy = x[0]['r.unit'], y[0]['r.unit']
                if ux != uy:
                    return f'{n1}的单位（{ux}）与{n2}的单位（{uy}）不同-无法比较'
                sub_answers = []
                for func, ok_pattern in func_and_pattern:
                    sent = ''
                    try:
                        res = self.calc_binary(x, y, func)
                        sent = ok_pattern(res, x, y, n1, n2)
                    except ValueError:
                        sent = f'{n1}或{n2}非数值类型-无法比较'
                    finally:
                        sub_answers.append(sent)
                answer = '，'.join(sub_answers)
            elif not x:
                answer = f'{n1}无数据记录-无法比较'
            elif not y:
                answer = f'{n2}无数据记录-无法比较'
            else:
                answer = f'{n1}与{n2}无数据记录-无法比较'
            answers.append(answer)
        return '；'.join(answers)

    def with_feed(self, data: tuple, *names: list,
                  binary_cmp_and_patterns: list,
                  err_pattern: FunctionType,
                  x_none_pattern: FunctionType,
                  y_none_pattern: FunctionType,
                  all_none_pattern: FunctionType) -> str:
        """ 制造涉值的投递及二元运算的回答。

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
        for x, y, f, n in zip(item1, item2,
                              self.product_repeat(feed, len(item2)//len(feed)),
                              self.product_name(*names)):
            if x and y:
                sub_answers = []
                for cmp_func, ok_pattern in binary_cmp_and_patterns:
                    sent = ''
                    try:
                        result = self.calc_binary(x, y, cmp_func)
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
