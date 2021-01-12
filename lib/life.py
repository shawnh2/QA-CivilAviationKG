# 为知识图谱结构关系编码/解码生命周期


class Life:

    def __init__(self):
        self._mask = 0x01
        self._code = {}  # 保存关键字的编码值

    def encode(self, obj: str):
        """ 编码，若已存在则不再进行编码 """
        if self._code.get(obj) is None:
            self._code[obj] = self._mask
            self._mask *= 2

    def get_life(self, obj: str):
        """ 返回编码，若不存在则返回0 """
        code = self._code.get(obj)
        return code if code is not None else 0

    @staticmethod
    def live(year, life) -> bool:
        """ 返回输入year编码是否还存在生命 """
        return (year & life) != 0

    @staticmethod
    def extend_life(life, code):
        """ 延续生命周期，code为延续时长编码 """
        return life + code
