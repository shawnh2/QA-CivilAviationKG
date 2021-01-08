# 问题分类器
import ahocorasick

from lib.check import *
from lib.regexp import *
from lib.result import Result
from lib.utils import read_words, debug
from lib.complement import year_complement, index_complement
from lib.errors import QuestionOrderError


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
        self.when_qwds = read_words(self.qwds_root.format('When'))

        # 指代词
        self.status_rwds = read_words(self.rwds_root.format('Status'))
        self.catalog_rwds = read_words(self.rwds_root.format('Catalog'))
        self.parent_index_rwds = read_words(self.rwds_root.format('ParentIndex'))
        self.child_index_rwds = read_words(self.rwds_root.format('ChildIndex'))
        self.location_rwds = read_words(self.rwds_root.format('Location'))
        self.index_rwds = read_words(self.rwds_root.format('Index'))
        self.max_rwds = read_words(self.rwds_root.format('Max'))

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
        # 过滤年份
        filtered_question = year_complement(question)
        # 过滤特征词
        region_wds = []
        for w in self.region_tree.iter(filtered_question):
            region_wds.append(w[1][1])
        region_dict = {w: self.word_type_dict.get(w) for w in region_wds}

        return Result(region_dict, question, filtered_question)

    def extract_index(self, result: Result, len_threshold: int = 4, ratio_threshold: float = 0.5):
        """ 提取因错别字或说法而未识别到的指标 """
        new_word, old_word = index_complement(result.filtered_question, self.index_wds, len_threshold, ratio_threshold)
        if new_word:
            debug('||REPLACE FOUND||', new_word, '<=', old_word)
            result.add_word(new_word, self.word_type_dict.get(new_word))
            result.replace_words(old_word, new_word)

    def classify(self, question: str):
        result = self.question_filter(question)
        if result.count('index') == 0 and 'catalog' not in result:
            self.extract_index(result)
        # 没有任何提取结果
        if result.is_wds_null():
            return None
        self._classify_tree(result)
        debug('||QUESTION WORDS||', result.region_wds)
        debug('||QUESTION TYPES||', result.question_types)
        return result

    def _classify_tree(self, result: Result):
        # 收集实体类型
        question = result.filtered_question
        year_count = result.count('year')

        # 问题与单个年份相关
        if year_count == 1:
            # 全年总体情况
            if check_contain(self.status_rwds, question) and 'year' in result and len(result) == 1:
                result.add_qtype('year_status')
            # 全年含有目录
            if check_contain(self.exist_qwds, question) and check_contain(self.catalog_rwds, question):
                result.add_qtype('exist_catalog')

            # 目录
            if 'catalog' in result:
                # 总体情况
                if check_contain(self.status_rwds, question):
                    result.add_qtype('catalog_status')

            # 指标
            if 'index' in result:
                # 值
                if check_contain(self.value_qwds, question) or check_endswith(self.is_twds, question):
                    if not check_contain(self.child_index_rwds, question):
                        # 涉及地区
                        if 'area' in result:
                            result.add_qtype('area_value')
                        else:
                            result.add_qtype('index_value')
                # 值比较(上级)
                if check_regexp(question, MultipleCmp1,
                                functions=[lambda x: check_contain(self.parent_index_rwds, x[0][-1])],
                                callback=lambda x: QuestionOrderError.check(x, self.parent_index_rwds)
                                ):
                    # 涉及地区
                    if 'area' in result:
                        result.add_qtype('area_overall')
                    else:
                        result.add_qtype('index_overall')
                # 值比较(同类同单位)
                if result.count('index') < 2:
                    self.extract_index(result, ratio_threshold=0.7)
                    question = result.filtered_question  # 重新查询后更新
                if result.count('index') == 2 and 'area' not in result:
                    if check_regexp(question, MultipleCmp1, functions=[
                        lambda x: check_list_contain(result['index'], x[0], 0, -1)
                    ]):
                        result.add_qtype('indexes_m_compare')  # 比较倍数关系
                    if check_regexp(question, NumberCmp1, functions=[
                        lambda x: (check_list_contain(result['index'], x[0], 0, -1) or
                                   check_all_contain(result['index'], x[0][0]))
                    ]):
                        result.add_qtype('indexes_n_compare')  # 比较数量关系
                # 地区值比较(相同指标不同地区)
                if result.count('area') == 2:
                    if check_regexp(question, MultipleCmp1, functions=[
                        lambda x: (check_list_contain(result['area'], x[0], 0, -1) and
                                   check_list_contain(result['index'], x[0], 0, not_=-1))
                    ]):
                        result.add_qtype('areas_m_compare')  # 比较倍数关系
                    if check_regexp(question, NumberCmp1, functions=[
                        lambda x: ((check_list_contain(result['area'], x[0], 0, -1) and
                                    check_contain(result['index'], x[0][0]))
                                   or
                                   (check_all_contain(result['area'], x[0][0]) and
                                    check_list_any_contain(result['index'], x[0], 0, -1)))
                    ]):
                        result.add_qtype('areas_n_compare')  # 比较数量关系
                # 同比值比较
                if check_regexp(question, GrowthCmp, functions=[
                    lambda x: check_all_contain(result['index'], x[0])
                ]):
                    if 'area' in result:
                        # 单地区多指标
                        if result.count('area') == 1:
                            result.add_qtype('areas_g_compare')
                    else:
                        result.add_qtype('indexes_g_compare')
                # 指标的组成
                if check_contain(self.child_index_rwds, question):
                    result.add_qtype('index_compose')

        # 问题与两个年份相关
        elif year_count == 2:
            # 目录与指标的变化情况
            if result.count('year') == len(result):
                if check_contain(self.catalog_rwds, question):
                    result.add_qtype('catalog_change')
                elif check_contain(self.index_rwds, question):
                    result.add_qtype('index_change')

            # 指标
            if 'index' in result:
                if check_contain(self.parent_index_rwds, question):
                    # 上级占比变化
                    if check_regexp(question, NumberCmp2[0], NumberCmp2[1], functions=[
                        lambda x: check_contain(self.parent_index_rwds, x[0])
                    ]*2):
                        if 'area' not in result:
                            result.add_qtype('index_2_overall')
                        elif check_regexp(question, NumberCmp2[0], NumberCmp2[1], functions=[
                            lambda x: check_contain(result['area'], x[0])
                        ]*2):
                            result.add_qtype('area_2_overall')
                else:
                    # 比较数值
                    if check_regexp(question, *NumberCmp2, functions=[
                        lambda x: check_contain(result['index'], x[0]),
                        lambda x: check_contain(result['index'], x[0]),
                        lambda x: check_contain(result['index'], x[0]),
                        lambda x: check_contain(result['index'], x[0][-1])
                    ]):
                        if 'area' not in result:  # 不涉及地区
                            result.add_qtype('indexes_2n_compare')
                        else:  # 涉及地区
                            if result.count('index') == 1:  # 单指标下不同地区比较
                                if check_regexp(question, *NumberCmp2, functions=[
                                    lambda x: check_contain(result['area'], x[0]),
                                    lambda x: check_contain(result['area'], x[0]),
                                    lambda x: check_contain(result['area'], x[0]),
                                    lambda x: check_contain(result['area'], x[0][0]),
                                ]):
                                    result.add_qtype('areas_2n_compare')
                    # 比较倍数
                    if check_regexp(question, MultipleCmp2, functions=[
                        lambda x: check_list_any_contain(result['index'], x[0], 0, -1)
                    ]):
                        if 'area' not in result:  # 不涉及地区
                            result.add_qtype('indexes_2m_compare')
                        else:  # 涉及地区
                            if check_regexp(question, MultipleCmp2, functions=[
                                lambda x: check_list_any_contain(result['area'], x[0], 0, -1)
                            ]):
                                result.add_qtype('areas_2m_compare')

        # 问题与多个年份相关
        elif year_count > 2:
            # 指标/目录变化趋势
            if result.count('year') == len(result) and check_contain(self.status_rwds, question):
                if check_contain(self.catalog_rwds, question):
                    result.add_qtype('catalogs_change')
                elif check_contain(self.index_rwds, question):
                    result.add_qtype('indexes_change')

            # 关于指标的变化趋势
            if 'index' in result:
                # 占上级的
                if check_regexp(question, MultipleCmp1, functions=[
                    lambda x: (check_contain(result['index'], x[0][0]) and
                               check_contain(self.status_rwds, x[0][-1]) and
                               check_contain(self.parent_index_rwds, x[0][-1]))
                ]):
                    if 'area' in result:
                        result.add_qtype('areas_overall_trend')
                    else:
                        result.add_qtype('indexes_overall_trend')
                # 值的
                if check_contain(self.status_rwds, question) and not check_contain(self.parent_index_rwds, question):
                    if 'area' in result:
                        result.add_qtype('areas_trend')
                    else:
                        result.add_qtype('indexes_trend')
                # 最值
                if check_contain(self.max_rwds, question):
                    if 'area' in result:
                        result.add_qtype('areas_max')
                    else:
                        result.add_qtype('indexes_max')

        # 问题与年份无关
        else:
            if 'index' in result and check_contain(self.when_qwds, question):
                result.add_qtype('begin_stats')
