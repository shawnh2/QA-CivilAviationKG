# 语句查询及组织回答
from operator import truediv, sub

from py2neo import Graph

from lib.utils import sign, debug
from lib.result import Result
from lib.answer import Answer, AnswerBuilder
from lib.painter import Painter
from lib.formatter import Formatter
from lib.chain import TranslationChain
from const import URI, USERNAME, PASSWORD


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
            result = self.graph.run(query_sql).data()
            return Formatter(result) if result else None

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
                        sub_results.append(None)
                        continue
                    sub_results.append(perform_sql(sql))
                results.append(sub_results)
            else:
                sql = sqls
                if sql is None:
                    results.append(None)
                    continue
                results.append(perform_sql(sql))
        return results

    def _search_direct_then_feed(self, chain: TranslationChain, unpack_key_name: str) -> tuple:
        """ 将第一次直接查询的结果作为第二次查询的输入 """
        results_1 = self._search_direct(chain)
        pattern_sql = next(chain.iter(1))
        sqls = []
        for items in results_1:
            if items is None:
                sqls.append(None)
                continue
            for item in items:
                sqls.append(pattern_sql.format(item[unpack_key_name]))
        results_2 = self._search_direct(sqls)
        return results_1, results_2

    def _search_double_direct_then_feed(self, chain: TranslationChain,
                                        unpack_key_name: str, unpack: bool = False) -> tuple:
        """ 第一次直接查询，第二次先执行直接查询后将查询结果投递至最后的查询 """
        results_1 = self._search_direct(chain, unpack=unpack)
        temp_res = self._search_direct(chain, 1)
        final_sqls = []
        for feed in temp_res:
            sqls = []
            for pattern_sql in chain.iter(2, unpack=unpack):
                if feed is None:
                    sqls.append(None)
                    continue
                sqls.append(pattern_sql.format(feed[unpack_key_name]))
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
        # 指标占总比
        elif qt == 'index_overall':
            self.make_index_overall_ans(answer, builder, chain, result)
        # 指标组成
        elif qt == 'index_compose':
            self.make_index_compose_ans(answer, builder, chain, result)
        # 指标倍数比较（只有两个指标） & 指标数量比较（只有两个指标）
        elif qt in ('indexes_m_compare', 'indexes_n_compare'):
            self.make_indexes_m_or_n_compare_ans(qt, answer, builder, chain, result)
        elif qt in ('indexes_2m_compare', 'indexes_2n_compare'):
            self.make_indexes_2m_or_2n_compare_ans(qt, answer, builder, chain, result)
        # 指标值同比比较
        elif qt == 'indexes_g_compare':
            self.make_indexes_g_compare_ans(answer, builder, chain, result)
        # 地区指标值
        elif qt == 'area_value':
            self.make_area_value_ans(answer, builder, chain, result)
        # 地区指标占总比
        elif qt == 'area_overall':
            self.make_area_overall_ans(answer, builder, chain, result)
        # 地区指标占总比的变化 & 指标占总比的变化
        elif qt in ('area_2_overall', 'index_2_overall'):
            self.make_index_or_area_2_overall_ans(qt, answer, builder, chain, result)
        # 地区指标倍数比较（只有两个地区） & 地区指标数量比较（只有两个地区）
        elif qt in ('areas_m_compare', 'areas_n_compare'):
            self.make_areas_m_or_n_compare_ans(qt, answer, builder, chain, result)
        elif qt in ('areas_2m_compare', 'areas_2n_compare'):
            self.make_areas_2m_or_2n_compare_ans(qt, answer, builder, chain, result)
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
        answer.add_answer(f'{result["year"][0]}年，{data[0]["y.info"]}')

    def make_catalog_status_ans(self, answer: Answer, builder: AnswerBuilder,
                                chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(
                result['catalog'], if_is_none=lambda _, na: f'并没有关于{result["year"][0]}年{na}的描述'
        ):
            answer.add_answer(f'{name}在{item["r.info"]}')

    def make_exist_catalog_ans(self, answer: Answer, chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        if not all(data):
            answer.add_answer(f'无{result["year"][0]}年的记录。')
        else:
            answer.add_answer(f'{result["year"][0]}年目录包括: ' + '，'.join([item['c.name'] for item in data[0]]))

    def make_index_value_ans(self, answer: Answer, builder: AnswerBuilder,
                             chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(
                result['index'], if_is_none=lambda _, na: f'无{na}数据记录'
        ):
            answer.add_answer(f'{name}为{item["r.value"]}{item["r.unit"]}')

    def make_index_overall_ans(self, answer: Answer, builder: AnswerBuilder,
                               chain: TranslationChain, result: Result):
        data = self._search_double_direct_then_feed(chain, 'n.name')
        builder.feed_data(data)
        for x, y, f, n in builder.product_data_with_feed(
                result['index'],
                if_x_is_none=lambda _1, _2, _3, na: f'无{na}的数据记录，无法比较',
                if_y_is_none=lambda _1, _2, _3, na: f'无{na}的父级数据记录，无法比较'
        ):
            answer.begin_sub_answers()
            answer.add_sub_answers(f'{n}为{x["r.value"]}{x["r.unit"]}')
            res1 = builder.binary_calculation(x['r.value'], y[0]['r.value'], truediv, percentage=True)
            if builder.add_if_is_not_none(res1, no=f'无效的{n}值类型，无法比较'):
                answer.add_sub_answers(f'其占总体（{f["n.name"]}）的{res1}%')
            res2 = builder.binary_calculation(y[0]['r.value'], x['r.value'], truediv)
            if builder.add_if_is_not_none(res2, no=f'无效的{n}值类型，无法比较'):
                answer.add_sub_answers(f'总体（{f["n.name"]}）是其的{res2}倍')
            answer.end_sub_answers()

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
            if item is None:
                answer.add_answer(f'指标“{name}”没有任何组成')
                return
            indexes, areas = [], []
            for n in item:
                feed = n.get('m.name')
                if n.get('labels(m)[0]') == 'Index':
                    indexes.append(feed)
                else:
                    areas.append(feed)
            # for indexes
            sqls1 = [sql.format(i) for sql in chain.iter(1) for i in indexes]
            data1 = self._search_direct(sqls1)
            # for areas
            sqls2 = [sql.format(name, a) for sql in chain.iter(2) for a in areas]
            data2 = self._search_direct(sqls2)
            # make data pairs
            final_data = {}
            for k, v in zip(indexes + areas, data1 + data2):
                if v is None:
                    continue
                child_id = v['r.child_id']
                if child_id is None:
                    continue
                value = v['r.value']
                try:
                    final_data.setdefault(child_id, []).append((k, float(value)))
                except ValueError or TypeError:
                    answer.add_answer(f'{name}中{k}的记录非数值类型，无法比较')
                    return
            # make other
            for k, v in final_data.items():
                op1 = sum([x[1] for x in v])
                op2 = float(total['r.value'])
                if op1 < int(op2):  # 舍弃一些误差，避免图中出现极小的部分
                    final_data[k].append(('其他', round(op2 - op1, 2)))
            collect.append(final_data)
            units.append(total['r.unit'])
            sub_titles.append(f'{name}为{total["r.value"]}{total["r.unit"]}，其构成分为：')
        # paint
        pie = self.painter.paint_pie(collect, units, title=result.raw_question, sub_titles=sub_titles)
        path = self.painter.render_html(pie, result.raw_question)
        answer.save_chart(pie)
        answer.add_answer(f'该问题的回答已渲染为图像，详见：{path}')

    def make_indexes_m_or_n_compare_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                        chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        operator = truediv if qt == 'indexes_m_compare' else sub
        for (x, y), (n1, n2) in builder.product_data_with_binary(
                result['index'],
                if_x_is_none=lambda _1, _2, na: f'无{na[0]}数据记录，无法比较',
                if_y_is_none=lambda _1, _2, na: f'无{na[1]}数据记录，无法比较'
        ):
            # 单位检查
            ux, uy = x['r.unit'] or '无', y['r.unit'] or '无'
            if builder.add_if_is_equal_or_not(ux, uy, no=f'{n1}的单位（{ux}）与{n2}的单位（{uy}）不同，无法比较'):
                answer.begin_sub_answers()
                answer.add_sub_answers(f'{n1}为{x["r.value"]}{x["r.unit"]}，'
                                       f'{n2}为{y["r.value"]}{y["r.unit"]}')
                res1 = builder.binary_calculation(x['r.value'], y['r.value'], operator)
                if builder.add_if_is_not_none(res1, no=f'{n1}或{n2}非数值类型，无法比较'):
                    if qt == 'indexes_m_compare':
                        answer.add_sub_answers(f'前者是后者的{res1}倍')
                    else:
                        answer.add_sub_answers(f'前者比后者{sign(res1)}{abs(res1)}{x["r.unit"]}')
                if qt == 'indexes_m_compare':
                    res2 = builder.binary_calculation(y['r.value'], x['r.value'], truediv)
                    if builder.add_if_is_not_none(res2, no=f'{n1}或{n2}非数值类型，无法比较'):
                        answer.add_sub_answers(f'后者是前者的{res2}倍')
                answer.end_sub_answers()

    def make_indexes_2m_or_2n_compare_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                          chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        operator = truediv if qt == 'indexes_2m_compare' else sub
        for item, name in builder.product_data_with_name(result["index"]):
            x, y = item
            if builder.binary_decision(
                    x, y,
                    not_x=f'无关于{result["year"][0]}年{name}的记录',
                    not_y=f'无关于{result["year"][1]}年{name}的记录'
            ):
                res = builder.binary_calculation(x["r.value"], y["r.value"], operator)
                if builder.add_if_is_not_none(res, no=f'{name}的记录为无效的值类型，无法比较', to_sub=False):
                    if qt == 'indexes_2m_compare':
                        line = f'{result["year"][0]}年的{name}（{x["r.value"]}{x["r.unit"]}）' \
                               f'是{result["year"][1]}年的（{y["r.value"]}{y["r.unit"]}）{res}倍'
                    else:
                        line = f'{result["year"][0]}年的{name}（{x["r.value"]}{x["r.unit"]}）' \
                               f'比{result["year"][1]}年的（{y["r.value"]}{y["r.unit"]}）' \
                               f'{sign(res, ("减少", "增加"))}{abs(res)}{x["r.unit"]}'
                    answer.add_answer(line)

    def make_indexes_g_compare_ans(self, answer: Answer, builder: AnswerBuilder,
                                   chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(result['index']):
            x, y = item
            if builder.binary_decision(
                    x, y,
                    not_x=f'无{result["year"][0]}年关于{name}的数据',
                    not_y=f'无{result["year"][0]}前一年关于{name}的数据'
            ):
                res = builder.growth_calculation(y["r.value"], x["r.value"])
                if builder.add_if_is_not_none(
                        res, to_sub=False,
                        no=f'{result["year"][0]}年{name}的记录非数值类型，无法计算'
                ):
                    answer.add_answer(f'{result["year"][0]}年的{name}为{y["r.value"]}{y["r.unit"]}，'
                                      f'其去年的为{x["r.value"]}{y["r.unit"]}，同比{sign(res, ("降低", "增长"))}{abs(res)}%')

    def make_area_value_ans(self, answer: Answer, builder: AnswerBuilder,
                            chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(
                result['area'], result['index'],
                if_is_none=lambda _, na: f'{na[0]}{na[1]}，无数据记录'
        ):
            answer.add_answer(f'{name[0]}{item["r.repr"]}{name[1]}为{item["r.value"]}{item["r.unit"]}')

    def make_area_overall_ans(self, answer: Answer, builder: AnswerBuilder,
                              chain: TranslationChain, result: Result):
        data = self._search_double_direct_then_feed(chain, 'n.name')
        builder.feed_data(data)
        for x, y, f, n in builder.product_data_with_feed(
                result['area'], result['index'],
                if_x_is_none=lambda _1, _2, _3, na: f'{na[0]}无{na[1]}的数据记录，无法比较',
                if_y_is_none=lambda _1, _2, _3, na: f'{na[0]}无{na[1]}父级地区的数据记录，无法比较'
        ):
            answer.begin_sub_answers()
            answer.add_sub_answers(f'{n[0]}{x["r.repr"]}的{n[1]}为{x["r.value"]}{x["r.unit"]}')
            res1 = builder.binary_calculation(x['r.value'], y[0]['r.value'], truediv, percentage=True)
            if builder.add_if_is_not_none(res1, no=f'{n[0]}中无效的{n[1]}值类型，无法比较'):
                answer.add_sub_answers(f'其占{f["n.name"]}{n[1]}的{res1}%')
            res2 = builder.binary_calculation(y[0]['r.value'], x['r.value'], truediv)
            if builder.add_if_is_not_none(res2, no=f'{n[0]}中无效的{n[1]}值类型，无法比较'):
                answer.add_sub_answers(f'{f["n.name"]}{n[1]}是其的{res2}倍')
            answer.end_sub_answers()

    def make_index_or_area_2_overall_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                         chain: TranslationChain, result: Result):
        years = '、'.join(result['year'])
        if qt == 'area_2_overall':
            unpack = True
            tag = '地区'
            gen = [result["area"], result["index"]]
        else:
            unpack = False
            tag = '指标'
            gen = [result["index"]]
        data = self._search_double_direct_then_feed(chain, "n.name", unpack=unpack)
        builder.feed_data(data)
        for x, y, f, n in builder.product_data_with_feed(
                *gen, flatten=unpack,  # 只是flatten参数的取值正好和unpack一致
                if_x_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na}的数据记录，无法比较',
                if_y_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na}的父级数据记录，无法比较'
        ):
            temp = []  # 记录两次计算的结果值
            for i, year in enumerate(result["year"]):
                answer.begin_sub_answers()
                answer.add_sub_answers(f'{year}年{n}为{x[i]["r.value"]}{x[i]["r.unit"]}')
                answer.add_sub_answers(f'其总体{tag}（{f["n.name"]}）的为{y[i]["r.value"]}{y[i]["r.unit"]}')
                res = builder.binary_calculation(x[i]["r.value"], y[i]["r.value"], truediv, percentage=True)
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
                if_x_is_none=lambda _1, _2, na: f'无{na[0][0]}{na[0][1]}数据记录，无法比较',
                if_y_is_none=lambda _1, _2, na: f'无{na[1][0]}{na[1][1]}数据记录，无法比较'
        ):
            # 单位检查
            ux, uy = x['r.unit'] or '无', y['r.unit'] or '无'
            if builder.add_if_is_equal_or_not(ux, uy,
                                              no=f'{n1[0]}的单位（{ux}）与{n2[0]}的单位（{uy}）不同，无法比较'):
                answer.begin_sub_answers()
                answer.add_sub_answers(f'{n1[0]}{x["r.repr"]}的{n1[1]}为{x["r.value"]}{x["r.unit"]}，'
                                       f'{n2[0]}{x["r.repr"]}的{n2[1]}为{y["r.value"]}{y["r.unit"]}')
                res1 = builder.binary_calculation(x['r.value'], y['r.value'], operator)
                if builder.add_if_is_not_none(res1,
                                              no=f'{n1[0][0]}{n1[0][1]}或{n2[1][0]}{n2[1][1]}非数值类型，无法比较'):
                    if qt == 'areas_m_compare':
                        answer.add_sub_answers(f'前者是后者的{res1}倍')
                    else:
                        answer.add_sub_answers(f'前者比后者{sign(res1)}{abs(res1)}{x["r.unit"]}')
                if qt == 'areas_m_compare':
                    res2 = builder.binary_calculation(y['r.value'], x['r.value'], truediv)
                    if builder.add_if_is_not_none(res2,
                                                  no=f'{n1[0][0]}{n1[0][1]}或{n2[1][0]}{n2[1][1]}非数值类型，无法比较'):
                        answer.add_sub_answers(f'后者是前者的{res2}倍')
                answer.end_sub_answers()

    def make_areas_2m_or_2n_compare_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                        chain: TranslationChain, result: Result):
        data = self._search_direct(chain, unpack=True)
        builder.feed_data(data)
        operator = truediv if qt == 'areas_2m_compare' else sub
        for item, name in builder.product_data_with_name(result["area"], result["index"], flatten=True):
            x, y = item
            if builder.binary_decision(
                    x, y,
                    not_x=f'无关于{result["year"][0]}年的{name}的记录',
                    not_y=f'无关于{result["year"][0]}年的{name}的记录'
            ):
                res = builder.binary_calculation(x["r.value"], y["r.value"], operator)
                if builder.add_if_is_not_none(res, no=f'{name}的记录为无效的值类型，无法比较', to_sub=False):
                    if qt == 'areas_2m_compare':
                        line = f'{result["year"][0]}年的{name}（{x["r.value"]}{x["r.unit"]}）' \
                               f'是{result["year"][1]}年的（{y["r.value"]}{y["r.unit"]}）{res}倍'
                    else:
                        line = f'{result["year"][0]}年的{name}（{x["r.value"]}{x["r.unit"]}）' \
                               f'比{result["year"][1]}年的（{y["r.value"]}{y["r.unit"]}）' \
                               f'{sign(res, ("减少", "增加"))}{abs(res)}{x["r.unit"]}'
                    answer.add_answer(line)

    def make_areas_g_compare_ans(self, answer: Answer, builder: AnswerBuilder,
                                 chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        builder.feed_data(data)
        for item, name in builder.product_data_with_name(result['area'], result['index'], flatten=True):
            x, y = item
            if builder.binary_decision(
                    x, y,
                    not_x=f'无{result["year"][0]}年关于{name}的数据',
                    not_y=f'无{result["year"][0]}前一年关于{name}的数据'
            ):
                res = builder.growth_calculation(y["r.value"], x["r.value"])
                if builder.add_if_is_not_none(
                        res, to_sub=False,
                        no=f'{result["year"][0]}年{name}的记录非数值类型，无法计算'
                ):
                    answer.add_answer(f'{result["year"][0]}年的{name}为{y["r.value"]}{y["r.unit"]}，'
                                      f'其去年的为{x["r.value"]}{y["r.unit"]}，同比{sign(res, ("减少", "增长"))}{abs(res)}%')

    def make_catalog_or_index_change_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                         chain: TranslationChain, result: Result):
        data = self._search_direct(chain)
        unpack_key_name = qt[0] + '.name'
        tag_name = '指标' if qt == 'index_change' else '目录'
        set1, set2 = set([n[unpack_key_name] for n in data[0]]), set([n[unpack_key_name] for n in data[1]])
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
        path = self.painter.render_html(line, result.raw_question)
        answer.save_chart(line)
        answer.add_answer(f'该问题的回答已渲染为图像，详见：{path}')

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
        ys = []
        for item, name in builder.product_data_with_name(*gen, flatten=unpack):
            y = builder.group_mapping_to_float(item, 'r.value')
            if builder.add_if_is_not_none(y, no=f'指标“{name}”非数值类型，无法比较', to_sub=False):
                ys.append((name, y))
        # paint
        if len(ys) != 0:
            unit = data[0][0]['r.unit']
            bar = self.painter.paint_bar(result['year'], *ys, unit=unit,
                                         title=result.raw_question, mark_point=mark_point)
            path = self.painter.render_html(bar, result.raw_question)
            answer.save_chart(bar)
            answer.add_answer(f'该问题的回答已渲染为图像，详见：{path}')

    def make_indexes_or_areas_overall_trend_ans(self, qt: str, answer: Answer, builder: AnswerBuilder,
                                                chain: TranslationChain, result: Result):
        if qt == 'areas_overall_trend':
            unpack = True
            gen = [result["area"], result["index"]]
        else:
            unpack = False
            gen = [result["index"]]
        data = self._search_double_direct_then_feed(chain, 'n.name', unpack)
        builder.feed_data(data)
        parents = {}
        children = {}
        for x, y, f, n in builder.product_data_with_feed(
                *gen, flatten=unpack,
                if_x_is_none=lambda _1, _2, _3, na: f'无关于”{na}“的记录',
                if_y_is_none=lambda _1, _2, _3, na: f'无关于”{na}“的父级记录'
        ):
            xs = builder.group_mapping_to_float(x, 'r.value')
            if not builder.add_if_is_not_none(xs, to_sub=False, no=f'{n}的记录非数值类型，无法比较'):
                return
            parent = f['n.name']
            ys = builder.group_mapping_to_float(y, 'r.value')
            if not builder.add_if_is_not_none(ys, to_sub=False, no=f'{n}的父级记录（{parent}）非数值类型，无法比较'):
                return
            unit = x[0]['r.unit']
            overall = [round(i / j, 3) for i, j in zip(xs, ys)]
            # 同一个父级指标将其子孙合并
            parents[parent] = ys
            children.setdefault((parent, unit), []).append((n, xs, overall))
        # paint
        if len(parents) != 0:
            bar = self.painter.paint_bar_stack_with_line(result['year'], children, parents, result.raw_question)
            path = self.painter.render_html(bar, result.raw_question)
            answer.save_chart(bar)
            answer.add_answer(f'该问题的回答已渲染为图像，详见：{path}')

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
            years = [int(year['y.name']) for year in item]
            answer.add_answer(f'指标“{name}”最早于{min(years)}年开始统计')
