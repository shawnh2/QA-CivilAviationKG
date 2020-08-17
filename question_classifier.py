# 问题分类器
import ahocorasick

from lib.check import *
from lib.result import Result
from lib.utils import read_words
from lib.regexp import MultipleCmp, NumberCmp
from lib.complement import year_complement, index_complement
from lib.errors import QuestionError, QuestionOrderError


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
        self.index_rwds = read_words(self.rwds_root.format('Index'))

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

    def question_filter(self, question: str) -> Result:
        question = question.replace(' ', '')
        # 先过滤年份
        filtered_question = year_complement(question)
        # 再过滤特征词
        region_wds = []
        for w in self.region_tree.iter(filtered_question):
            region_wds.append(w[1][1])
        region_dict = {w: self.word_type_dict.get(w) for w in region_wds}
        return Result(region_dict)

    def classify(self, question: str):
        result = self.question_filter(question)
        if result.is_null():
            return None
        try:
            self._classify_tree(question, result)
        except QuestionError as err:
            # 收集错误问题的提示
            result.add_msg(err.args[0])
        finally:
            return result

    def _classify_tree(self, question: str, result: Result):
        # 收集实体类型
        types = result.get_words_types()
        year_count = types.count('year')

        # 问题与单个年份相关
        if year_count == 1:
            # 全年总体情况
            if check_contain(self.status_rwds, question) and 'year' in types and len(types) == 1:
                result.add_qtype('year_status')
            # 全年含有目录
            if check_contain(self.exist_qwds, question) and check_contain(self.catalog_rwds, question):
                result.add_qtype('exist_catalog')

            # 目录
            if 'catalog' in types:
                # 总体情况
                if check_contain(self.status_rwds, question):
                    result.add_qtype('catalog_status')

            # 指标
            if 'index' in types:
                # 值
                if check_contain(self.value_qwds, question) or check_endswith(self.is_twds, question):
                    if not check_contain(self.child_index_rwds, question):
                        # 涉及地区
                        if 'area' in types:
                            result.add_qtype('area_value')
                        else:
                            result.add_qtype('index_value')
                # 值比较(上级)
                if check_regexp(question, MultipleCmp,
                                lambda x: check_contain(self.parent_index_rwds, x[0][-1]),
                                callback=lambda x: QuestionOrderError.check(x, self.parent_index_rwds)
                                ):
                    # 涉及地区
                    if 'area' in types:
                        result.add_qtype('area_overall')
                    else:
                        result.add_qtype('index_overall')
                # 值比较(同类同单位)
                if types.count('index') == 2 and 'area' not in types:
                    if check_regexp(question, MultipleCmp,
                                    lambda x: check_list_contain(result['index'], x[0], 0, -1)
                                    ):
                        result.add_qtype('indexes_m_compare')  # 比较倍数关系
                    if check_regexp(question, NumberCmp,
                                    lambda x: (check_list_contain(result['index'], x[0], 0, -1) or
                                               check_all_contain(result['index'], x[0][0]))
                                    ):
                        result.add_qtype('indexes_n_compare')  # 比较数量关系
                # 地区值比较(相同指标不同地区)
                if types.count('index') == 1 and types.count('area') == 2:
                    if check_regexp(question, MultipleCmp,
                                    lambda x: (check_list_contain(result['area'], x[0], 0, -1) and
                                               check_list_contain(result['index'], x[0], 0))
                                    ):
                        result.add_qtype('areas_m_compare')  # 比较倍数关系
                    if check_regexp(question, NumberCmp,
                                    lambda x: ((check_list_contain(result['area'], x[0], 0, -1) and
                                               check_contain(result['index'], x[0][0]))
                                               or
                                               (check_all_contain(result['area'], x[0][0]) and
                                               check_list_any_contain(result['index'], x[0], 0, -1)))
                                    ):
                        result.add_qtype('areas_n_compare')  # 比较数量关系
                # 指标下不同地区组成情况
                if check_contain(self.location_rwds, question):
                    if check_contain(self.status_rwds, question):
                        result.add_qtype('area_compose')
                # 指标的子组成
                else:
                    if check_contain(self.child_index_rwds, question):
                        result.add_qtype('index_compose')

        # 问题与两个年份相关
        elif year_count == 2:
            # 目录与指标的变化情况
            if len(result) == 2:
                if check_contain(self.catalog_rwds, question):
                    result.add_qtype('catalog_change')
                elif check_contain(self.index_rwds, question):
                    result.add_qtype('index_change')

        # 问题与多个年份相关
        elif year_count > 2:
            pass

        # 问题与年份无关
        else:
            pass
