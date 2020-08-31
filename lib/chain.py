# 解析器翻译链
from enum import Enum


class QueryType(Enum):
    Direct = 0                    # 直接查询
    DirectThenFeed = 1            # 直接查询后投递
    DoubleDirectThenFeed = 2      # 直接查询两次后投递


class TranslationChain:
    """ 按照sql语句的执行顺序串成链, 后链需前一链的结果作为输入(@为其占位符)。"""

    def __init__(self):
        self._chain = {}
        self._offset = 0
        self.query_type = QueryType.Direct

    def make(self, sqls: list):
        self._chain[self._offset] = sqls
        return self

    def then(self, sqls: list):
        self._offset += 1
        return self.make(sqls)

    def set_query_type(self, qtype: QueryType = QueryType.Direct):
        self.query_type = qtype

    def reset(self):
        """ 重置目前的链 """
        self._chain.clear()
        self._offset = 0
        self.query_type = QueryType.Direct

    def iter(self, offset: int = 0):
        for sql in self._chain[offset]:
            yield sql

    def __repr__(self):
        return str(self._chain)
