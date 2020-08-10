import re
import ahocorasick

# 加载正则表达式
from data.regexp import *
# 加载映射字典
from data.mapping import *


class QuestionClassifier:

    def __init__(self):
        # 词根目录
        self.region_wds_root = './data/dicts/{}.txt'
        self.question_wds_root = './data/question/{}.txt'
        self.reference_wds_root = './data/reference/{}.txt'
        self.tail_wds_root = './data/tail/{}.txt'

        self.word_type_dict = {}
        # 特征词
        self.area_wds = self.read_region_words('area')
        self.catalog_wds = self.read_region_words('catalog')
        self.index_wds = self.read_region_words('index')
        self.year_wds = self.read_region_words('year')

        # 问句疑问词
        self.exist_qwds = self.read_question_words('Exist')
        self.value_qwds = self.read_question_words('Value')

        # 指代词
        self.status_rwds = self.read_reference_words('Status')
        self.catalog_rwds = self.read_reference_words('Catalog')
        self.parent_index_rwds = self.read_reference_words('ParentIndex')
        self.child_index_rwds = self.read_reference_words('ChildIndex')
        self.location_rwds = self.read_reference_words('Location')

        # 尾词
        self.is_twds = self.read_tail_words('Is')

        self.region_wds = set(self.area_wds + self.catalog_wds + self.index_wds + self.year_wds)
        self.region_tree = self.build_actree()

    def read_region_words(self, word_type: str) -> list:
        """ 加载特征词并构建特征词类型字典 """
        with open(self.region_wds_root.format(word_type.capitalize()), encoding='utf-8') as f:
            collect = []
            for word in f:
                word = word.strip('\n')
                self.word_type_dict[word] = word_type
                collect.append(word)
            return collect

    def read_question_words(self, word_type: str) -> list:
        """ 加载问句疑问词 """
        with open(self.question_wds_root.format(word_type), encoding='utf-8') as f:
            return [w.strip('\n') for w in f]

    def read_reference_words(self, word_type: str) -> list:
        """ 加载指代词 """
        with open(self.reference_wds_root.format(word_type), encoding='utf-8') as f:
            return [w.strip('\n') for w in f]

    def read_tail_words(self, word_type: str) -> list:
        """ 加载尾词 """
        with open(self.tail_wds_root.format(word_type), encoding='utf-8') as f:
            return [w.strip('\n') for w in f]

    def build_actree(self):
        actree = ahocorasick.Automaton()
        for i, word in enumerate(self.region_wds):
            actree.add_word(word, (i, word))
        actree.make_automaton()
        return actree

    def question_filter(self, question: str) -> dict:
        # 先过滤年份
        years = re.compile(Year).findall(question)
        filtered_question = question

        def year_filter(y: str) -> str:
            # 替换
            for k, v in Char2Digit.items():
                y = y.replace(k, v)
            # 补全
            if len(y) == 2:
                y = '20' + y
            return y

        for (year, gap) in years:
            year = year.rstrip('年')
            if not gap:
                new_year = year_filter(year)
            else:
                start, end = year.split(gap)
                start_year, end_year = int(year_filter(start)), int(year_filter(end))
                new_year = ','.join([str(start_year + i) for i in range(end_year - start_year + 1)])
            filtered_question = filtered_question.replace(year, new_year)

        # 再过滤特征词
        region_wds = []
        for w in self.region_tree.iter(filtered_question):
            region_wds.append(w[1][1])
        region_dict = {w: self.word_type_dict.get(w) for w in region_wds}
        return region_dict

    @classmethod
    def do_contain_check(cls, words: list, question: str) -> bool:
        # 检查包含关系
        for word in words:
            if word in question:
                return True
        return False

    @classmethod
    def do_endswith_check(cls, words: list, question: str) -> bool:
        # 检查尾部关系
        return question.endswith(tuple(words))

    @classmethod
    def do_regexp_check(cls, pattern: str, question: str, function) -> bool:
        # 检查正则关系
        result = re.compile(pattern).findall(question)
        if result:
            return function(result)
        return False

    def classify(self, question: str) -> dict:
        result = {}
        args = self.question_filter(question)
        if not args:
            return {}
        result['args'] = args
        # 收集实体类型
        types = [t for t in args.values()]
        question_types = []
        year_count = types.count('year')

        # 问题与单个年份相关
        if year_count == 1:
            # 全年总体情况
            if self.do_contain_check(self.status_rwds, question) and 'catalog' not in types and 'index' not in types:
                question_types.append('year_status')
            # 全年含有目录
            if self.do_contain_check(self.exist_qwds, question) and self.do_contain_check(self.catalog_rwds, question):
                question_types.append('exist_catalog')

            # 目录
            if 'catalog' in types:
                # 总体情况
                if self.do_contain_check(self.status_rwds, question):
                    question_types.append('catalog_status')

            # 指标
            if 'index' in types:
                # 值
                if self.do_contain_check(self.value_qwds, question) or self.do_endswith_check(self.is_twds, question):
                    if not self.do_contain_check(self.child_index_rwds, question):
                        # 涉及地区
                        if 'area' in types:
                            question_types.append('area_index_value')
                        else:
                            question_types.append('index_value')
                # 值比较(上级)
                if self.do_regexp_check(Compare, question,
                                        lambda x: self.do_contain_check(self.parent_index_rwds, x[0][-1])):
                    # 涉及地区
                    if 'area' in types:
                        question_types.append('area_index_compare')
                    else:
                        question_types.append('index_up_compare')
                # 值比较(同类同单位)
                if types.count('index') == 2 and 'area' not in types:
                    if self.do_regexp_check(Compare, question,
                                            lambda x: self.do_contain_check([k for k, v in args.items()
                                                                             if v == 'index'], x[0][-1])):
                        question_types.append('index_index_compare')
                # 地区值比较(相同指标不同地区)
                if types.count('index') == 1 and types.count('area') == 2:
                    if self.do_regexp_check(Compare, question, lambda x: any(x)):
                        question_types.append('area_area_compare')
                # 指标下不同地区组成情况
                if self.do_contain_check(self.location_rwds, question):
                    if self.do_contain_check(self.status_rwds, question):
                        question_types.append('index_area_compose')
                # 指标的子组成
                else:
                    if self.do_contain_check(self.child_index_rwds, question):
                        question_types.append('index_compose')

        # 问题与两个年份相关
        elif year_count == 2:
            pass

        # 问题与多个年份相关
        elif year_count > 2:
            pass

        # 问题与年份无关
        else:
            pass

        result['question'] = question
        result['question_types'] = question_types
        # print(result)

        return result
