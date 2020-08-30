# 解析器翻译链


class TranslationChain:
    """ 按照sql语句的执行顺序串成链, 后链需前一链的结果作为输入(@为其占位符)。"""

    def __init__(self):
        self._chain = {}
        self._offset = 0

    def make(self, sqls: list):
        self._chain[self._offset] = sqls
        return self

    def then(self, sqls: list):
        self._offset += 1
        return self.make(sqls)

    def reset(self):
        """ 重置目前的链 """
        self._chain.clear()
        self._offset = 0

    def __repr__(self):
        return str(self._chain)

    def __iter__(self):
        for n in range(len(self._chain)):
            yield self._chain[n]
