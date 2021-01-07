# 格式化sql查询结果


class Formatter:

    def __init__(self, data: list):
        self._data = data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, name):
        # 0 为常用默认拆包位置
        item = self._data[0].get(name)
        return item if item is not None else ''

    def __iter__(self):
        for item in self._data:
            yield item

    def __repr__(self):
        return str(self._data)
