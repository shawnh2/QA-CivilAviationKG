from lib.chain import TranslationChain


class Result(object):
    """ 保存查询使用的信息 """
    def __init__(self, region_wds: dict, raw_q: str, filtered_q: str):
        # 特征词
        self.region_wds = region_wds  # word: type_
        self.region_wds_types = [t for t in self.region_wds.values()]
        self.region_wds_reverse = self.reverse_region_dict()  # type_: word
        # 问题
        self.raw_question = raw_q
        self.filtered_question = filtered_q
        # 一些结果
        self.question_types = []
        self.sqls = {}

    def __getitem__(self, type_name: str):
        return self.region_wds_reverse.get(type_name)

    def __len__(self):
        return len(self.region_wds)

    def __contains__(self, type_name: str):
        return type_name in self.region_wds_types

    def is_wds_null(self):
        return self.region_wds == {}

    def is_qt_null(self):
        return self.question_types == []

    def count(self, type_name: str = None):
        """返回某个特征词类型的个数"""
        return self.region_wds_types.count(type_name)

    def add_word(self, word: str, type_: str):
        if word not in self.region_wds.keys():
            self.region_wds[word] = type_
            self.region_wds_types.append(type_)
            self.region_wds_reverse.setdefault(type_, []).append(word)

    def add_qtype(self, question_type):
        self.question_types.append(question_type)

    def add_sql(self, qt: str, sqls: TranslationChain):
        self.sqls[qt] = sqls

    def reverse_region_dict(self):
        # 转换值为键
        new_dict = {}
        for k, v in self.region_wds.items():
            new_dict.setdefault(v, []).append(k)
        return new_dict

    def replace_words(self, old_word: str, new_word: str):
        """ 更改句子中的词语 """
        self.filtered_question = self.filtered_question.replace(old_word, new_word)
