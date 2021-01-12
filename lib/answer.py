# 回答构建器
from itertools import product
from types import FunctionType

from pyecharts.charts import Page

from lib.formatter import Formatter
from const import CHART_RENDER_DIR


class Answer:

    def __init__(self):
        self._answers = []
        self._sub_answers = []
        self._charts = []  # 保存图表

    def add_answer(self, string: str):
        self._answers.append(string)

    def to_string(self) -> str:
        return "；".join(self._answers)

    def save_chart(self, chart):
        self._charts.append(chart)

    def combine_charts(self):
        # 若有大于一个以上的图表，将它们合为一个图表（Page类型）
        # 不直接画到一个图表上，是因为在web app中无法直接嵌入Page类型，而其他模式均可以
        if len(self._charts) > 1:
            page = Page()
            page.add(*self._charts)
            self._charts.clear()
            self.save_chart(page)

    def get_chart(self):
        return None if not self.have_charts() else self._charts[0]

    def get_charts(self):
        return self._charts

    def render_chart(self, name: str):
        chart = self._charts[0]
        chart.render(f'{CHART_RENDER_DIR}/{name}.html')

    def have_charts(self):
        return len(self._charts) != 0

    def begin_sub_answers(self):
        self._sub_answers.clear()

    def add_sub_answers(self, string: str):
        self._sub_answers.append(string)

    def end_sub_answers(self):
        self._answers.append('，'.join(self._sub_answers))


class AnswerBuilder:

    def __init__(self, answer: Answer):
        self._data = None
        self.answer = answer

    def feed_data(self, data):
        self._data = data

    @classmethod
    def product_name(cls, *name: list):
        """ 对传入的名称进行笛卡尔积
        eg: [1,2],[a,b] => (1,a),(1,b),(2,a),(2,b)
            if flatten  =>  1a, 1b, 2a, 2b
        """
        for n in product(*name):
            if len(n) == 1:
                yield Formatter({'prod.name': n[0]})
            else:
                yield Formatter({'prod.name': n[1], 'prod.area': n[0]})

    @classmethod
    def product_repeat(cls, feeds: list, n: int):
        """ 对传入的列表元素每个重复n次迭代 """
        count = 0
        i = 0
        for _ in range(len(feeds) * n):
            yield feeds[i]
            count += 1
            if count == n:
                count = 0
                i += 1

    @classmethod
    def product_binary(cls, data: list):
        """ 对传入的数据进行二元输出
        eg: [1,2,3,4] or [1,2,3,4,5] => (1,3),(2,4)
        """
        mid = len(data) // 2
        start = 0
        end = mid
        while start < mid:
            yield data[start], data[end]
            start += 1
            end += 1

    @classmethod
    def binary_calculation(cls, operand1: str, operand2: str, operator: FunctionType,
                           percentage: bool = False) -> float:
        res = None
        try:
            res = operator(float(operand1), float(operand2))
            res = round(res*100, 2) if percentage else round(res, 3)
        finally:
            return res

    @classmethod
    def growth_calculation(cls, this_year: str, last_year: str) -> float:
        res = None
        try:
            f1, f2 = float(this_year), float(last_year)
            res = round(((f1 - f2) / f2) * 100, 2)
        finally:
            return res

    @classmethod
    def group_mapping_to_float(cls, x: list) -> list:
        """ 把x映射为float值序列 """
        res = []
        for e in x:
            try:
                res.append(float(e.value))
            except ValueError or TypeError:
                res.append(0)
            except IndexError:
                res.append(0)
        return res

    def product_data_with_name(self, *names, if_is_none: FunctionType = None):
        for item, name in zip(self._data, self.product_name(*names)):
            if if_is_none is None:
                yield item, name
            else:
                if not item:
                    self.answer.add_answer(if_is_none(item, name))
                else:
                    yield item, name

    def product_data_with_feed(self, *names,
                               if_x_is_none: FunctionType,
                               if_y_is_none: FunctionType):
        data1, data2, feed = self._data
        n = len(data2) // len(feed)
        for item1, item2, feed, name in zip(data1, data2, self.product_repeat(feed, n),
                                            self.product_name(*names)):
            if self.binary_decision(item1, item2,
                                    not_x=if_x_is_none(item1, item2, feed, name),
                                    not_y=if_y_is_none(item1, item2, feed, name)):
                yield item1, item2, feed, name

    def product_data_with_binary(self, *names,
                                 if_x_is_none: FunctionType,
                                 if_y_is_none: FunctionType):
        for item, name in zip(self.product_binary(self._data),
                              self.product_binary([n for n in self.product_name(*names)])):
            x, y = item
            if self.binary_decision(x, y,
                                    not_x=if_x_is_none(x, y, name),
                                    not_y=if_y_is_none(x, y, name)):
                yield item, name

    # 常用逻辑模板

    def binary_decision(self, x, y, not_x: str, not_y: str) -> bool:
        if isinstance(x, list):
            x = any(x)
        if isinstance(y, list):
            y = any(y)
        dec = False
        if x and y:
            dec = True
        elif not x:
            self.answer.add_answer(not_x)
        else:
            self.answer.add_answer(not_y)
        return dec

    def add_if_is_equal_or_not(self, x, y, no: str,
                               equal: bool = True, to_sub: bool = False) -> bool:
        """ equal=True时，两值相同则返回，若不同则把no加入answer；
            equal=False时，两值不同则返回，若相同则把no加入answer """
        add_no = (x != y) if equal else (x == y)
        if add_no:
            if to_sub:
                self.answer.add_sub_answers(no)
            else:
                self.answer.add_answer(no)
            return False
        return True

    def add_if_is_not_none(self, x, no: str, to_sub: bool = True) -> bool:
        """ 如果x为None，就把no加入answers中 """
        if x is None:
            if to_sub:
                self.answer.add_sub_answers(no)
            else:
                self.answer.add_answer(no)
            return False
        return True
