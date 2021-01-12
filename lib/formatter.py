# 格式化sql查询结果
import pickle


class Formatter:

    def __init__(self, data):
        self._life_path = './data/dicts/life.pk'
        # flags
        self._is_none = (data is None or len(data) == 0)
        # fields
        self.name = ''  # index_name
        self.area = ''
        self.info = ''
        self.value = ''
        self.unit = ''
        self.life = ''
        self.repr = ''
        self.label = ''
        self.child_id = ''
        # init
        self._distribute(data)

    def _distribute(self, data):
        """ 将传入的数据字段分散为各个字段 """
        if self._is_none:
            return
        for k, v in data.items():
            if k.endswith('name'):
                self.name = v
            elif k.endswith('area'):
                self.area = v
            elif k.endswith('info'):
                self.info = v
            elif k.endswith('value'):
                self.value = v
            elif k.endswith('unit'):
                self.unit = v
            elif k.endswith('life'):
                self.life = int(v)
            elif k.endswith('repr'):
                self.repr = v
            elif k.startswith('label'):
                self.label = v
            elif k.endswith('child_id'):
                self.child_id = v

    def __repr__(self):
        return f'<name:{self.name} info:{self.info} value:{self.value} unit:{self.unit}' \
               f' life:{self.life} area:{self.area} repr:{self.repr} labels:{self.label} child_id:{self.child_id}>'

    def __bool__(self):
        return not self._is_none

    def life_check(self, year: str):
        """ 检查并剔除不在生命周期中的数据 """
        if self._is_none:
            return
        with open(self._life_path, 'rb') as f:
            life = pickle.load(f)
            year = life.get_life(year)
            if life.live(year, self.life) == 0:
                self._is_none = True

    def subject(self):
        """ 获取主语 """
        return f'{self.area}{self.repr}{self.name}'

    def val(self):
        """ 获取取值 """
        return f'{self.value}{self.unit}'
