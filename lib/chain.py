# 解析器翻译链


class TranslationChain:
    """ 按照sql语句的执行顺序串成链, 后链需前一链的结果作为输入({}为其占位符)。"""

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

    def iter(self, offset: int = 0, unpack: bool = False):
        gen = self._chain[offset][0] if unpack else self._chain[offset]
        for sql in gen:
            yield sql

    def __repr__(self):
        return str(self._chain)
