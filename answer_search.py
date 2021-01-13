# 语句查询及组织回答
from operator import truediv, sub

from py2neo import Graph

from lib.utils import sign, debug
from lib.result import Result
from lib.answer import Answer, AnswerBuilder
from lib.painter import Painter
from lib.formatter import Formatter
from lib.chain import TranslationChain

from const import URI, USERNAME, PASSWORD, CHART_RENDER_DIR


class AnswerSearcher:

    def __init__(self):
        self.graph = Graph(URI, auth=(USERNAME, PASSWORD))
        self.painter = Painter()

    def search(self, result: Result) -> [Answer]:
        debug('||QUESTION ORIGINAL||', result.raw_question)
        debug('||QUESTION FILTERED||', result.filtered_question)
        answers = []
        for qt, chain in result.sqls.items():
            answer = self.organize(qt, chain, result)
            answers.append(answer)
        return answers

    def _search_direct(self, sql_gen, offset: int = 0, unpack: bool = False) -> list:
        """ 进行直接查询 """
        # 只支持双层列表的嵌套，有第三层列表嵌套时令unpack=True

        def perform_sql(query_sql: str):
            rs = self.graph.run(query_sql).data()
            if len(rs) > 1:
                return [Formatter(r) for r in rs]
            elif len(rs) == 1:
                return Formatter(rs[0])
            else:
                return Formatter(rs)

        results = []
        if isinstance(sql_gen, TranslationChain):
            generator = sql_gen.iter(offset, unpack)
        else:
            generator = sql_gen
        for sqls in generator:
            debug('||GENERATED SQL||', sqls)
            if isinstance(sqls, list):
                sub_results = []
                for sql in sqls:
                    if sql is None:
                        sub_results.append(Formatter(None))
                        continue
                    sub_results.append(perform_sql(sql))
                results.append(sub_results)
            else:
                sql = sqls
                if sql is None:
                    results.append(Formatter(None))
                    continue
                results.append(perform_sql(sql))
        return results

    def _search_direct_then_feed(self, chain: TranslationChain, unpack_key_name: str) -> tuple:
        """ 将第一次直接查询的结果作为第二次查询的输入 """
        results_1 = self._search_direct(chain)
        pattern_sql = next(chain.iter(1))
        sqls = []
        for items in results_1:
            if not items:
                sqls.append(None)
                continue
            for item in items:
                sqls.append(pattern_sql.format(item[unpack_key_name]))
        results_2 = self._search_direct(sqls)
        return results_1, results_2

    def _search_double_direct_then_feed(self, chain: TranslationChain, unpack: bool = False) -> tuple:
        """ 第一次直接查询，第二次先执行直接查询后将查询结果投递至最后的查询 """
        results_1 = self._search_direct(chain, unpack=unpack)
        temp_res = self._search_direct(chain, 1)
        final_sqls = []
        for feed in temp_res:
            sqls = []
            for pattern_sql in chain.iter(2, unpack=unpack):
                if not feed:
                    sqls.append(None)
                    continue
                sqls.append(pattern_sql.format(feed.name))
            final_sqls.append(sqls)
        results_2 = self._search_direct(final_sqls)
        return results_1, results_2, temp_res

    def organize(self, qt: str, chain: TranslationChain, result: Result) -> Answer:
        answer = Answer()
        builder = AnswerBuilder(answer)
        # 年度总体状况
        if qt == 'year_status':
            self.make_year_status_ans(answer, chain, result)
        # 年度目录状况
        elif qt == 'catalog_status':
            self.make_catalog_status_ans(answer, builder, chain, result)
        # 年度目录包含哪些
        elif qt == 'exist_catalog':
            self.make_exist_catalog_ans(answer, chain, result)
        # 指标值
        elif qt == 'index_value':
            self.make_index_value_ans(answer, builder, chain, result)
        # 指标占总比 & 地区指标占总比
        elif qt in ('index_overall', 'area_overall'):
            self.make_index_or_area_overall_ans(qt, answer, builder, chain, result)
        # 指标组成
        elif qt == 'index_compose':
            self.make_index_compose_ans(answer, builder, chain, result)
        # 指标倍数比较（只有两个指标） & 指标数量比较（只有两个指标）
        elif qt in ('indexes_m_compare', 'indexes_n_compare'):
            self.make_indexes_m_or_n_compare_ans(qt, answer, builder, chain, result)
        elif qt in ('indexes_2m_compare', 'indexes_2n_compare', 'areas_2m_compare', 'areas_2n_compare'):
            self.make_indexes_or_areas_2m_or_2n_compare_ans(qt, answer, builder, chain, result)
        # 指标值同比比较
        elif qt == 'indexes_g_compare':
            self.make_indexes_g_compare_ans(answer, builder, chain, result)
        # 地区指标值
        elif qt == 'area_value':
            self.make_area_value_ans(answer, builder, chain, result)
        # 地区指标占总比的变化 & 指标占总比的变化
        elif qt in ('area_2_overall', 'index_2_overall'):
            self.make_index_or_area_2_overall_ans(qt, answer, builder, chain, result)
        # 地区指标倍数比较（只有两个地区） & 地区指标数量比较（只有两个地区）
        elif qt in ('areas_m_compare', 'areas_n_compare'):
            self.make_areas_m_or_n_compare_ans(qt, answer, builder, chain, result)
        # 地区指标值同比比较
        elif qt == 'areas_g_compare':
            self.make_areas_g_compare_ans(answer, builder, chain, result)
        # 两年目录的变化 & 两年指标的变化
        elif qt in ('catalog_change', 'index_change'):
            self.make_catalog_or_index_change_ans(qt, answer, builder, chain, result)
        # 多年目录的变化 & 多年指标的变化
        elif qt in ('catalogs_change', 'indexes_change'):
            self.make_catalogs_or_indexes_change_ans(qt, answer, chain, result)
        # 指标值变化(多年份)
        elif qt in ('indexes_trend', 'areas_trend'):
            self.make_indexes_or_areas_trend_ans(qt, answer, builder, chain, result)
        # 占总指标比的变化
        elif qt in ('indexes_overall_trend', 'areas_overall_trend'):
            self.make_indexes_or_areas_overall_trend_ans(qt, answer, builder, chain, result)
        # 几个年份中的最值
        elif qt in ('indexes_max', 'areas_max'):
            self.make_indexes_or_areas_max_ans(qt, answer, builder, chain, result)
        # 何时开始统计此指标
        elif qt == 'begin_stats':
            self.make_begin_stats_ans(answer, builder, chain, result)

        return answer

    def make_year_status_ans(self, answer: Answer, chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        answer.add_answer(f'{result["year"][0]}年，{data[0].info}')

    def make_catalog_status_ans(self, answer: Answer, builder: AnswerBuilder,
                                chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(
                result['catalog'],
                if_is_none=lambda _, na: f'并没有关于{result["year"][0]}年{na.subject()}的描述'
        ):
            answer.add_answer(item.info)

    def make_exist_catalog_ans(self, answer: Answer, chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        if not all(data):
            answer.add_answer(f'无{result["year"][0]}年的记录。')
        else:
            answer.add_answer(f'{result["year"][0]}年目录包括: ' + '，'.join([item.name for item in data[0]]))

    def make_index_value_ans(self, answer: Answer, builder: AnswerBuilder,
                             chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(
                result['index'], if_is_none=lambda _, na: f'无{na.subject()}数据记录'
        ):
            answer.add_answer(f'{name.subject()}为{item.val()}')

    def make_index_compose_ans(self, answer: Answer, builder: AnswerBuilder,
                               chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        collect = []
        units = []
        sub_titles = []
        # for overall
        sqls_overall = [sql for sql in chain.iter(3)]
        data_overall = self._search_direct(sqls_overall)
        # collect
        for total, (item, name) in zip(
                data_overall,
                builder.product_data_with_name(result['index'])
        ):  # 为使两可迭代对象同步迭代和collect不用做判空，此处不使用if_is_none参数
            if not item:
                answer.add_answer(f'指标“{name.name}”没有任何组成')
                continue
            indexes, areas = [], []
            for n in item:
                n.life_check(result['year'][0])
                if n:
                    if n.label == 'Index':
                        indexes.append(n.name)
                    else:
                        areas.append(n.name)
            if len(indexes) == 0 and len(areas) == 0:
                answer.add_answer(f'指标“{name.name}”没有任何组成')
                continue
            # for indexes
            sqls1 = [sql.format(i) for sql in chain.iter(1) for i in indexes]
            data1 = self._search_direct(sqls1)
            # for areas
            sqls2 = [sql.format(name.name, a) for sql in chain.iter(2) for a in areas]
            data2 = self._search_direct(sqls2)
            # make data pairs
            final_data = {}
            for k, v in zip(indexes + areas, data1 + data2):
                if not v:
                    continue
                if v.child_id is None:
                    continue
                try:
                    final_data.setdefault(v.child_id, []).append((k, float(v.value)))
                except ValueError or TypeError:
                    answer.add_answer(f'{name.name}中{k}的记录非数值类型，无法比较')
                    return
            # make other
            for k, v in final_data.items():
                op1 = sum([x[1] for x in v])
                op2 = float(total.value)
                if op1 < int(op2):  # 舍弃一些误差，避免图中出现极小的部分
                    final_data[k].append(('其他', round(op2 - op1, 2)))
            collect.append(final_data)
            units.append(total.unit)
            sub_titles.append(f'{name.subject()}为{total.val()}，其构成分为：')
        # paint
        for pie in self.painter.paint_pie(collect, units,
                                          title=result.raw_question, sub_titles=sub_titles):
            answer.save_chart(pie)
        answer.add_answer(f'该问题的回答已渲染为图像，详见：{CHART_RENDER_DIR}/{result.raw_question}.html')

    def make_indexes_m_or_n_compare_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                        chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        operator = truediv if qt == 'indexes_m_compare' else sub
        for (x, y), (n1, n2) in builder.product_data_with_binary(
                result['index'],
                if_x_is_none=lambda _1, _2, na: f'无{na[0].subject()}数据记录，无法比较',
                if_y_is_none=lambda _1, _2, na: f'无{na[1].subject()}数据记录，无法比较'
        ):
            # 单位检查
            ux, uy = x.unit or '无', y.unit or '无'
            if builder.add_if_is_equal_or_not(ux, uy,
                                              no=f'{n1.subject()}的单位（{ux}）与{n2.subject()}的单位（{uy}）不同，无法比较'):
                answer.begin_sub_answers()
                answer.add_sub_answers(f'{n1.subject()}为{x.val()}，{n2.subject()}为{y.val()}')
                res1 = builder.binary_calculation(x.value, y.value, operator)
                if builder.add_if_is_not_none(res1,
                                              no=f'{n1.subject()}或{n2.subject()}非数值类型，无法比较'):
                    if qt == 'indexes_m_compare':
                        answer.add_sub_answers(f'前者是后者的{res1}倍')
                    else:
                        answer.add_sub_answers(f'前者比后者{sign(res1)}{abs(res1)}{ux}')
                if qt == 'indexes_m_compare':
                    res2 = builder.binary_calculation(y.value, x.value, truediv)
                    if builder.add_if_is_not_none(res2,
                                                  no=f'{n1.subject()}或{n2.subject()}非数值类型，无法比较'):
                        answer.add_sub_answers(f'后者是前者的{res2}倍')
                answer.end_sub_answers()

    def make_indexes_g_compare_ans(self, answer: Answer, builder: AnswerBuilder,
                                   chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(result['index']):
            x, y = item
            if builder.binary_decision(
                    x, y,
                    not_x=f'无{result["year"][0]}年关于{name.subject()}的数据',
                    not_y=f'无{result["year"][0]}前一年关于{name.subject()}的数据'
            ):
                res = builder.growth_calculation(y.value, x.value)
                if builder.add_if_is_not_none(
                        res, to_sub=False,
                        no=f'{result["year"][0]}年{name.subject()}的记录非数值类型，无法计算'
                ):
                    answer.add_answer(f'{result["year"][0]}年的{name.subject()}为{y.val()}，'
                                      f'其去年的为{x.val()}，同比{sign(res, ("降低", "增长"))}{abs(res)}%')

    def make_area_value_ans(self, answer: Answer, builder: AnswerBuilder,
                            chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(
                result['area'], result['index'],
                if_is_none=lambda _, na: f'{na.subject()}无数据记录'
        ):
            name.repr = item.repr
            answer.add_answer(f'{name.subject()}为{item.value}{item.unit}')

    def make_index_or_area_overall_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                       chain: TranslationChain, result: Result):
        if qt == 'index_overall':
            gen = [result['index']]
            tag = '指标'
        else:
            gen = [result['area'], result['index']]
            tag = ''
        data = self._search_double_direct_then_feed(chain)
        builder.feed_data(data)
        for x, y, f, n in builder.product_data_with_feed(
                *gen,
                if_x_is_none=lambda _1, _2, _3, na: f'无{na.subject()}的数据记录，无法比较',
                if_y_is_none=lambda _1, _2, _3, na: f'无{na.subject()}的父级{tag}数据记录，无法比较'
        ):
            f.life_check(result['year'][0])
            if not f:
                answer.add_answer(f'无{n.subject()}父级{tag}数据记录，无法比较')
                return
            answer.begin_sub_answers()
            unit_x, unit_y = x.unit, y[0].unit
            if qt == 'area_overall':  # 交换值域
                f.area, f.name = f.name, n.name
            n.repr = f.repr = x.repr
            answer.add_sub_answers(f'{n.subject()}为{x.val()}')
            answer.add_sub_answers(f'其父级{tag}{f.subject()}为{y[0].val()}')
            if unit_x != unit_y:
                answer.add_sub_answers('两者单位不同，无法比较')
                answer.end_sub_answers()
                return
            res1 = builder.binary_calculation(x.value, y[0].value, truediv, percentage=True)
            if builder.add_if_is_not_none(res1, no=f'无效的{n.subject()}值类型，无法比较'):
                answer.add_sub_answers(f'前者占后者的{res1}%')
            res2 = builder.binary_calculation(y[0].value, x.value, truediv)
            if builder.add_if_is_not_none(res2, no=f'无效的{n.subject()}值类型，无法比较'):
                answer.add_sub_answers(f'后者是前者的{res2}倍')
            answer.end_sub_answers()

    def make_index_or_area_2_overall_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                         chain: TranslationChain, result: Result):
        years = '、'.join(result['year'])
        # init
        if qt == 'area_2_overall':
            unpack = True
            gen = [result["area"], result["index"]]
        else:
            unpack = False
            gen = [result["index"]]
        # collect data
        data = self._search_double_direct_then_feed(chain, unpack=unpack)
        builder.feed_data(data)
        # product data
        for x, y, f, n in builder.product_data_with_feed(
                *gen,
                if_x_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na.subject()}的数据记录，无法比较',
                if_y_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na.subject()}的父级数据记录，无法比较'
        ):
            temp = []  # 记录两次计算的结果值
            for i, year in enumerate(result["year"]):
                f.life_check(year)
                if not f:
                    answer.add_answer(f'无{year}年{n.subject()}的父级数据记录，无法比较')
                    continue
                unit_x, unit_y = x[i].unit, y[i].unit
                answer.begin_sub_answers()
                n.repr = x[i].repr
                answer.add_sub_answers(f'{year}年{n.subject()}为{x[i].value}{unit_x}')
                answer.add_sub_answers(f'其总体{f.name}{y[i].repr}为{y[i].value}{unit_y}')
                if unit_x != unit_y:
                    answer.add_sub_answers('两者单位不同，无法比较')
                    answer.end_sub_answers()
                    continue
                res = builder.binary_calculation(x[i].value, y[i].value, truediv, percentage=True)
                if builder.add_if_is_not_none(res, no=f'无效的{n}值类型，无法比较'):
                    answer.add_sub_answers(f'约占总体的{res}%')
                    temp.append(res)
                answer.end_sub_answers()
            if len(temp) == 2:
                num = round(temp[0] - temp[1], 2)
                answer.add_answer(f'前者相比后者{sign(num, ("降低", "提高"))}{abs(num)}%')

    def make_areas_m_or_n_compare_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                      chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        operator = truediv if qt == 'areas_m_compare' else sub
        builder.feed_data(data)
        for (x, y), (n1, n2) in builder.product_data_with_binary(
                result['area'], result['index'],
                if_x_is_none=lambda _1, _2, na: f'无{na[0].subject()}数据记录，无法比较',
                if_y_is_none=lambda _1, _2, na: f'无{na[1].subject()}数据记录，无法比较'
        ):
            # 单位检查
            ux, uy = x.unit or '无', y.unit or '无'
            if builder.add_if_is_equal_or_not(ux, uy,
                                              no=f'{n1.subject()}的单位（{ux}）与{n2.subject()}的单位（{uy}）不同，无法比较'):
                answer.begin_sub_answers()
                n1.repr, n2.repr = x.repr, y.repr
                answer.add_sub_answers(f'{n1.subject()}为{x.val()}，{n2.subject()}为{y.val()}')
                res1 = builder.binary_calculation(x.value, y.value, operator)
                if builder.add_if_is_not_none(res1,
                                              no=f'{n1.subject()}或{n2.subject()}非数值类型，无法比较'):
                    if qt == 'areas_m_compare':
                        answer.add_sub_answers(f'前者是后者的{res1}倍')
                    else:
                        answer.add_sub_answers(f'前者比后者{sign(res1)}{abs(res1)}{ux}')
                if qt == 'areas_m_compare':
                    res2 = builder.binary_calculation(y.value, x.value, truediv)
                    if builder.add_if_is_not_none(res2,
                                                  no=f'{n1.subject()}或{n2.subject()}非数值类型，无法比较'):
                        answer.add_sub_answers(f'后者是前者的{res2}倍')
                answer.end_sub_answers()

    def make_indexes_or_areas_2m_or_2n_compare_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                                   chain: TranslationChain, result: Result):
        # set operator
        if qt in ('areas_2m_compare', 'indexes_2m_compare'):
            operator = truediv
        else:
            operator = sub
        # set gen and flatten
        if qt in ('areas_2m_compare', 'areas_2n_compare'):
            gen = [result['area'], result['index']]
            unpack = True
        else:
            gen = [result['index']]
            unpack = False
        # code begin
        data = self._search_direct(chain, unpack=unpack)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(*gen):
            x, y = item
            if builder.binary_decision(
                    x, y,
                    not_x=f'无关于{result["year"][0]}年的{name.subject()}的记录',
                    not_y=f'无关于{result["year"][1]}年的{name.subject()}的记录'
            ):
                answer.begin_sub_answers()
                res = builder.binary_calculation(x.value, y.value, operator)
                if builder.add_if_is_not_none(res, no=f'{name.subject()}的记录为无效的值类型，无法比较'):
                    answer.add_sub_answers(f'{result["year"][0]}年的{name.subject()}为{x.val()}')
                    answer.add_sub_answers(f'{result["year"][1]}年的{name.subject()}为{y.val()}')
                    if qt in ('areas_2m_compare', 'indexes_2m_compare'):
                        ux, uy = x.unit, y.unit
                        # 单位为%的数值不支持此类型比较
                        if ux == uy == '%':
                            answer.add_sub_answers(f'它们单位为‘%’，不支持此类型的比较')
                        else:
                            answer.add_sub_answers(f'前者是后者的{res}倍')
                    else:
                        answer.add_sub_answers(f'前者比后者{sign(res, ("减少", "增加"))}{abs(res)}{x.unit}')
                answer.end_sub_answers()

    def make_areas_g_compare_ans(self, answer: Answer, builder: AnswerBuilder,
                                 chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(result['area'], result['index']):
            x, y = item
            if builder.binary_decision(
                    x, y,
                    not_x=f'无{result["year"][0]}年关于{name.subject()}的数据',
                    not_y=f'无{result["year"][0]}前一年关于{name.subject()}的数据'
            ):
                res = builder.growth_calculation(y.value, x.value)
                if builder.add_if_is_not_none(
                        res, to_sub=False,
                        no=f'{result["year"][0]}年{name.subject()}的记录非数值类型，无法计算'
                ):
                    answer.add_answer(f'{result["year"][0]}年的{name.subject()}为{y.val()}，'
                                      f'其去年的为{x.val()}，同比{sign(res, ("减少", "增长"))}{abs(res)}%')

    def make_catalog_or_index_change_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                         chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        tag_name = '指标' if qt == 'index_change' else '目录'
        set1, set2 = set([n.name for n in data[0]]), set([n.name for n in data[1]])
        diff1, diff2 = set1.difference(set2), set2.difference(set1)
        n1, n2 = len(diff1), len(diff2)
        if builder.add_if_is_equal_or_not(
                n1, 0, equal=False,
                no=f'{result["year"][1]}年与{result["year"][0]}年的{tag_name}相同'
        ):
            answer.add_answer(f'{result["year"][1]}年与{result["year"][0]}年相比，未统计{n1}个{tag_name}：' + '、'.join(diff1))
        if builder.add_if_is_equal_or_not(
                n2, 0, equal=False,
                no=f'{result["year"][0]}年与{result["year"][1]}年的{tag_name}相同'
        ):
            answer.add_answer(f'{result["year"][0]}年与{result["year"][1]}年相比，未统计{n2}个{tag_name}：' + '、'.join(diff2))

    def make_catalogs_or_indexes_change_ans(self, qt: str, answer: Answer, chain: TranslationChain, result: Result):
        tag = '目录' if qt == 'catalogs_change' else '指标'
        data = self._search_direct(chain)
        y = [len(item) for item in data]
        line = self.painter.paint_line(result['year'], f'{tag}个数', y, result.raw_question)
        answer.save_chart(line)
        answer.add_answer(f'该问题的回答已渲染为图像，详见：{CHART_RENDER_DIR}/{result.raw_question}.html')

    def make_indexes_or_areas_trend_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                        chain: TranslationChain, result: Result, mark_point: bool = False):
        if qt == 'areas_trend':
            unpack = True
            gen = [result['area'], result['index']]
        else:
            unpack = False
            gen = [result['index']]
        # collect
        data = self._search_direct(chain, unpack=unpack)
        builder.feed_data(data)
        collects = []  # 根据不同单位划分数据
        for item, name in builder.product_data_with_name(*gen):
            collect = []
            units = set([n.unit for n in item if n.unit != ''])
            ys = builder.group_mapping_to_float(item)
            if builder.add_if_is_equal_or_not(sum(ys), 0, equal=False,
                                              no=f'指标“{name.subject()}”无任何值记录，无法比较'):
                for unit in units:
                    tmp = []
                    for y, n in zip(ys, item):
                        tmp.append(y if n.unit == unit else 0)
                    collect.append((name.subject(), unit, tmp))
                collects.append(collect)
        # paint
        if len(collects) != 0:
            bar = self.painter.paint_bar(result['year'], collects,
                                         title=result.raw_question, mark_point=mark_point)
            answer.save_chart(bar)
            answer.add_answer(f'该问题的回答已渲染为图像，详见：{CHART_RENDER_DIR}/{result.raw_question}.html')

    def make_indexes_or_areas_overall_trend_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                                chain: TranslationChain, result: Result):
        if qt == 'areas_overall_trend':
            unpack = True
            gen = [result["area"], result["index"]]
        else:
            unpack = False
            gen = [result["index"]]
        data = self._search_double_direct_then_feed(chain, unpack)
        builder.feed_data(data)
        parents = {}
        children = {}
        for x, y, f, n in builder.product_data_with_feed(
                *gen,
                if_x_is_none=lambda _1, _2, _3, na: f'无关于”{na.subject()}“的记录',
                if_y_is_none=lambda _1, _2, _3, na: f'无关于”{na.subject()}“的父级记录'
        ):
            xs = builder.group_mapping_to_float(x)
            if not builder.add_if_is_not_none(xs, to_sub=False,
                                              no=f'{n.subject()}的记录非数值类型，无法比较'):
                return
            parent = f.name + n.name if qt == 'areas_overall_trend' else f.name
            ys = builder.group_mapping_to_float(y)
            if not builder.add_if_is_not_none(ys, to_sub=False,
                                              no=f'{n.subject()}的父级记录（{parent}）非数值类型，无法比较'):
                return
            overall = [round(i / j, 3) if j != 0 else 0 for i, j in zip(xs, ys)]
            # 同一个父级指标将其子孙合并
            parents[parent] = ys
            children.setdefault((parent, x[-1].unit), []).append((n.subject(), xs, overall))
        # paint
        if len(parents) != 0:
            for bar in self.painter.paint_bar_stack_with_line(result['year'], children, parents,
                                                              result.raw_question):
                answer.save_chart(bar)
            answer.add_answer(f'该问题的回答已渲染为图像，详见：{CHART_RENDER_DIR}/{result.raw_question}.html')

    def make_indexes_or_areas_max_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                      chain: TranslationChain, result: Result):
        # 可以直接复用
        if qt == 'areas_max':
            self.make_indexes_or_areas_trend_ans('areas_trend', answer, builder, chain, result, mark_point=True)
        else:
            self.make_indexes_or_areas_trend_ans('indexes_trend', answer, builder, chain, result, mark_point=True)

    def make_begin_stats_ans(self, answer: Answer, builder: AnswerBuilder,
                             chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(result['index']):
            years = [int(year.name) for year in item]
            answer.add_answer(f'指标“{name.name}”最早于{min(years)}年开始统计')
