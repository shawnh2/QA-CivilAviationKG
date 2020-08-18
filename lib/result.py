
class Result(object):
    """ 保存查询的结果 """
    def __init__(self, region_wds: dict, raw_q: str, filtered_q: str):
        # 特征词
        self.region_wds = region_wds
        self.region_wds_types = [t for t in self.region_wds.values()]
        # 问题
        self.raw_question = raw_q
        self.filtered_question = filtered_q
        # 一些结果
        self.question_types = []
        self.messages = []

    def __getitem__(self, type_name: str):
        return [k for k, v in self.region_wds.items() if v == type_name]

    def __len__(self):
        return len(self.region_wds)

    def __contains__(self, type_name: str):
        return type_name in self.region_wds_types

    def is_null(self):
        return self.region_wds == {}

    def count(self, type_name: str = None):
        # 返回某个特征词类型的个数
        return self.region_wds_types.count(type_name)

    def add_msg(self, message: str):
        self.messages.append(message)

    def add_qtype(self, question_type):
        self.question_types.append(question_type)
