# 问题分类器
import ahocorasick

from lib.regexp import Compare
from lib.utils import read_words
from lib.complement import year_complement
from lib.check import check_contain, check_endswith, check_regexp
from lib.errors import QuestionError, ParentIndexSequenceError


class QuestionClassifier:

    def __init__(self):
        # 词根目录
        self.region_wds_root = './data/dicts/{}.txt'
        self.qwds_root = './data/question/{}.txt'
        self.rwds_root = './data/reference/{}.txt'
        self.twds_root = './data/tail/{}.txt'

        self.word_type_dict = {}
        # 特征词
        self.area_wds = self.read_region_words('area')
        self.catalog_wds = self.read_region_words('catalog')
        self.index_wds = self.read_region_words('index')
        self.year_wds = self.read_region_words('year')

        # 问句疑问词
        self.exist_qwds = read_words(self.qwds_root.format('Exist'))
        self.value_qwds = read_words(self.qwds_root.format('Value'))

        # 指代词
        self.status_rwds = read_words(self.rwds_root.format('Status'))
        self.catalog_rwds = read_words(self.rwds_root.format('Catalog'))
        self.parent_index_rwds = read_words(self.rwds_root.format('ParentIndex'))
        self.child_index_rwds = read_words(self.rwds_root.format('ChildIndex'))
        self.location_rwds = read_words(self.rwds_root.format('Location'))

        # 尾词
        self.is_twds = read_words(self.twds_root.format('Is'))

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

    def build_actree(self):
        actree = ahocorasick.Automaton()
        for i, word in enumerate(self.region_wds):
            actree.add_word(word, (i, word))
        actree.make_automaton()
        return actree

    def question_filter(self, question: str) -> dict:
        # 先过滤年份
        filtered_question = year_complement(question)
        # 再过滤特征词
        region_wds = []
        for w in self.region_tree.iter(filtered_question):
            region_wds.append(w[1][1])
        region_dict = {w: self.word_type_dict.get(w) for w in region_wds}
        return region_dict

    def classify(self, question: str) -> dict:
        result = {}
        args = self.question_filter(question)
        if not args:
            return {}
        question_types = []
        try:
            question_types = self._classify_tree(question, args)
        except QuestionError:
            pass
        finally:
            result['args'] = args
            # result['question'] = question
            result['question_types'] = question_types
            return result

    def _classify_tree(self, question: str, args: dict) -> list:
        # 收集实体类型
        types = [t for t in args.values()]
        question_types = []
        year_count = types.count('year')

        # 问题与单个年份相关
        if year_count == 1:
            # 全年总体情况
            if check_contain(self.status_rwds, question) and 'catalog' not in types and 'index' not in types:
                question_types.append('year_status')
            # 全年含有目录
            if check_contain(self.exist_qwds, question) and check_contain(self.catalog_rwds, question):
                question_types.append('exist_catalog')

            # 目录
            if 'catalog' in types:
                # 总体情况
                if check_contain(self.status_rwds, question):
                    question_types.append('catalog_status')

            # 指标
            if 'index' in types:
                # 值
                if check_contain(self.value_qwds, question) or check_endswith(self.is_twds, question):
                    if not check_contain(self.child_index_rwds, question):
                        # 涉及地区
                        if 'area' in types:
                            question_types.append('area_index_value')
                        else:
                            question_types.append('index_value')
                # 值比较(上级)
                if check_regexp(Compare, question,
                                lambda x: check_contain(self.parent_index_rwds, x[0][-1]),
                                lambda x: ParentIndexSequenceError.check(x, self.parent_index_rwds)):
                    # 涉及地区
                    if 'area' in types:
                        question_types.append('area_index_compare')
                    else:
                        question_types.append('index_up_compare')
                # 值比较(同类同单位)
                if types.count('index') == 2 and 'area' not in types:
                    if check_regexp(Compare, question,
                                    lambda x: check_contain([k for k, v in args.items() if v == 'index'], x[0][-1])):
                        question_types.append('index_index_compare')
                # 地区值比较(相同指标不同地区)
                if types.count('index') == 1 and types.count('area') == 2:
                    if check_regexp(Compare, question, lambda x: any(x)):
                        question_types.append('area_area_compare')
                # 指标下不同地区组成情况
                if check_contain(self.location_rwds, question):
                    if check_contain(self.status_rwds, question):
                        question_types.append('index_area_compose')
                # 指标的子组成
                else:
                    if check_contain(self.child_index_rwds, question):
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

        return question_types
