
class Result(object):
    """ 保存查询的结果 """
    def __init__(self, region_wds: dict):
        self.region_wds = region_wds
        self.question_types = []
        self.messages = []

    def is_null(self):
        return self.region_wds == {}

    def add_msg(self, message: str):
        self.messages.append(message)

    def add_qtype(self, question_type):
        self.question_types.append(question_type)

    def get_words_types(self):
        return [t for t in self.region_wds.values()]

    def __getitem__(self, type_name: str):
        return [k for k, v in self.region_wds.items() if v == type_name]

    def __len__(self):
        return len(self.region_wds)
