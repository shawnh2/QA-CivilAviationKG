# 语句查询及组织回答
from operator import truediv, sub

from py2neo import Graph

from lib.utils import sign, debug
from lib.result import Result
from lib.answer import Answer
from lib.painter import Painter
from lib.chain import TranslationChain
from const import URI, USERNAME, PASSWORD


class AnswerSearcher:

    def __init__(self):
        self.graph = Graph(URI, auth=(USERNAME, PASSWORD))

    def search(self, result: Result):
        debug('||QUESTION ORIGINAL||', result.raw_question)
        debug('||QUESTION FILTERED||', result.filtered_question)
        for qt, chain in result.sqls.items():
            answer = self.organize(qt, chain, result)
            print(answer, '\n')

    def _search_direct(self, sql_gen, offset: int = 0, unpack: bool = False) -> list:
        """ 进行直接查询 """
        # 只支持双层列表的嵌套，有第三层列表嵌套时令unpack=True

        def perform_sql(query_sql: str):
            result = self.graph.run(query_sql).data()
            return result if result else None

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
        sqls = []
        for feed in temp_res:
            for pattern_sql in chain.iter(2, unpack=unpack):
                if feed is None:
                    sqls.append(None)
                    continue
                sqls.append(pattern_sql.format(feed[0][unpack_key_name]))
        results_2 = self._search_direct(sqls)
        return results_1, results_2, temp_res

    def organize(self, qt: str, chain: TranslationChain, result: Result) -> str:
        answer = Answer()
        # 年度总体状况
        if qt == 'year_status':
            data = self._search_direct(chain)
            answer.add_answer(f'{result["year"][0]}年，{data[0][0]["y.info"]}')
        # 年度目录状况
        elif qt == 'catalog_status':
            data = self._search_direct(chain)
            answer.feed_data(data)
            for item, name in answer.product_data_with_name(
                    result['catalog'], if_is_none=lambda _, na: f'并没有关于{result["year"][0]}年{na}的描述'):
                answer.add_answer(f'{name}在{item[0]["r.info"]}')
        # 年度目录包含哪些
        elif qt == 'exist_catalog':
            data = self._search_direct(chain)
            if not all(data):
                answer.add_answer(f'无{result["year"][0]}年的记录。')
            else:
                answer.add_answer(f'{result["year"][0]}年目录包括: ' + '，'.join([item['c.name'] for item in data[0]]))
        # 指标值
        elif qt == 'index_value':
            data = self._search_direct(chain)
            answer.feed_data(data)
            for item, name in answer.product_data_with_name(
                    result['index'], if_is_none=lambda _, na: f'{na}-无数据记录'):
                answer.add_answer(f'{name}为{item[0]["r.value"]}{item[0]["r.unit"]}')
        # 指标占总比
        elif qt == 'index_overall':
            data = self._search_double_direct_then_feed(chain, 'n.name')
            answer.feed_data(data)
            for x, y, f, n in answer.product_data_with_feed(
                    result['index'],
                    if_x_is_none=lambda _1, _2, _3, na: f'无{na}的数据记录-无法比较',
                    if_y_is_none=lambda _1, _2, _3, na: f'无{na}的父级数据记录-无法比较'):
                answer.begin_sub_answers()
                answer.add_sub_answers(f'{n}为{x[0]["r.value"]}{x[0]["r.unit"]}')
                res1 = answer.binary_calculation(x[0]['r.value'], y[0]['r.value'], truediv, percentage=True)
                if answer.add_if_is_not_none(res1, no=f'无效的{n}值类型-无法比较'):
                    answer.add_sub_answers(f'其占总体（{f[0]["n.name"]}）的{res1}%')
                res2 = answer.binary_calculation(y[0]['r.value'], x[0]['r.value'], truediv)
                if answer.add_if_is_not_none(res2, no=f'无效的{n}值类型-无法比较'):
                    answer.add_sub_answers(f'总体（{f[0]["n.name"]}）是其的{res2}倍')
                answer.end_sub_answers()
        # 指标组成
        elif qt == 'index_compose':
            data = self._search_direct(chain)
            answer.feed_data(data)
            for item, name in answer.product_data_with_name(
                    result['index'], if_is_none=lambda _, na: f'指标{na}没有任何子指标'):
                answer.add_answer(f'指标{name}的子集包括：' + '，'.join(n["m.name"] for n in item))
        # 指标倍数比较（只有两个指标） & 指标数量比较（只有两个指标）
        elif qt in ('indexes_m_compare', 'indexes_n_compare'):
            data = self._search_direct(chain)
            answer.feed_data(data)
            operator = truediv if qt == 'indexes_m_compare' else sub
            for (x, y), (n1, n2) in answer.product_data_with_binary(
                    result['index'],
                    if_x_is_none=lambda _1, _2, na: f'无{na[0]}数据记录-无法比较',
                    if_y_is_none=lambda _1, _2, na: f'无{na[1]}数据记录-无法比较'):
                # 单位检查
                ux, uy = x[0]['r.unit'], y[0]['r.unit']
                if answer.add_if_is_equal_or_not(ux, uy, no=f'{n1}的单位（{ux}）与{n2}的单位（{uy}）不同-无法比较'):
                    answer.begin_sub_answers()
                    answer.add_sub_answers(f'{n1}为{x[0]["r.value"]}{x[0]["r.unit"]}，'
                                           f'{n2}为{y[0]["r.value"]}{y[0]["r.unit"]}')
                    res1 = answer.binary_calculation(x[0]['r.value'], y[0]['r.value'], operator)
                    if answer.add_if_is_not_none(res1, no=f'{n1}或{n2}非数值类型-无法比较'):
                        if qt == 'indexes_m_compare':
                            answer.add_sub_answers(f'前者是后者的{res1}倍')
                        else:
                            answer.add_sub_answers(f'前者比后者{sign(res1)}{abs(res1)}{x[0]["r.unit"]}')
                    if qt == 'indexes_m_compare':
                        res2 = answer.binary_calculation(y[0]['r.value'], x[0]['r.value'], truediv)
                        if answer.add_if_is_not_none(res2, no=f'{n1}或{n2}非数值类型-无法比较'):
                            answer.add_sub_answers(f'后者是前者的{res2}倍')
                    answer.end_sub_answers()
        elif qt in ('indexes_2m_compare', 'indexes_2n_compare'):
            data = self._search_direct(chain)
            answer.feed_data(data)
            operator = truediv if qt == 'indexes_2m_compare' else sub
            for item, name in answer.product_data_with_name(result["index"]):
                x, y = item
                if answer.binary_decision(x, y,
                                          not_x=f'无关于{result["year"][0]}年{name}的记录',
                                          not_y=f'无关于{result["year"][1]}年{name}的记录'):
                    res = answer.binary_calculation(x[0]["r.value"], y[0]["r.value"], operator)
                    if answer.add_if_is_not_none(res, no=f'{name}的记录为无效的值类型-无法比较', to_sub=False):
                        if qt == 'indexes_2m_compare':
                            line = f'{result["year"][0]}年的{name}（{x[0]["r.value"]}{x[0]["r.unit"]}）' \
                                   f'是{result["year"][1]}年的（{y[0]["r.value"]}{y[0]["r.unit"]}）{res}倍'
                        else:
                            line = f'{result["year"][0]}年的{name}（{x[0]["r.value"]}{x[0]["r.unit"]}）' \
                                   f'比{result["year"][1]}年的（{y[0]["r.value"]}{y[0]["r.unit"]}）' \
                                   f'{sign(res, ("减少", "增加"))}{abs(res)}{x[0]["r.unit"]}'
                        answer.add_answer(line)
        # 指标值同比比较
        elif qt == 'indexes_g_compare':
            data = self._search_direct(chain)
            answer.feed_data(data)
            for item, name in answer.product_data_with_name(result['index']):
                x, y = item
                if answer.binary_decision(x, y,
                                          not_x=f'无{result["year"][0]}年关于{name}的数据',
                                          not_y=f'无{result["year"][0]}前一年关于{name}的数据'):
                    res = answer.growth_calculation(y[0]["r.value"], x[0]["r.value"])
                    if answer.add_if_is_not_none(res, to_sub=False,
                                                 no=f'{result["year"][0]}年{name}的记录非数值类型，无法计算'):
                        answer.add_answer(f'{result["year"][0]}年的{name}为{y[0]["r.value"]}{y[0]["r.unit"]}，'
                                          f'其去年的为{x[0]["r.value"]}{y[0]["r.unit"]}，'
                                          f'同比{sign(res, ("降低", "增长"))}{abs(res)}%')
        # 地区指标值
        elif qt == 'area_value':
            data = self._search_direct(chain)
            answer.feed_data(data)
            for item, name in answer.product_data_with_name(
                    result['area'], result['index'], if_is_none=lambda _, na: f'{na[0]}{na[1]}-无数据记录'):
                answer.add_answer(f'{name[0]}{item[0]["r.repr"]}{name[1]}为{item[0]["r.value"]}{item[0]["r.unit"]}')
        # 地区指标占总比
        elif qt == 'area_overall':
            data = self._search_double_direct_then_feed(chain, 'n.name')
            answer.feed_data(data)
            for x, y, f, n in answer.product_data_with_feed(
                    result['area'], result['index'],
                    if_x_is_none=lambda _1, _2, _3, na: f'{na[0]}无{na[1]}的数据记录-无法比较',
                    if_y_is_none=lambda _1, _2, _3, na: f'{na[0]}无{na[1]}父级地区的数据记录-无法比较'):
                answer.begin_sub_answers()
                answer.add_sub_answers(f'{n[0]}{x[0]["r.repr"]}的{n[1]}为{x[0]["r.value"]}{x[0]["r.unit"]}')
                res1 = answer.binary_calculation(x[0]['r.value'], y[0]['r.value'], truediv, percentage=True)
                if answer.add_if_is_not_none(res1, no=f'{n[0]}中无效的{n[1]}值类型-无法比较'):
                    answer.add_sub_answers(f'其占{f[0]["n.name"]}{n[1]}的{res1}%')
                res2 = answer.binary_calculation(y[0]['r.value'], x[0]['r.value'], truediv)
                if answer.add_if_is_not_none(res2, no=f'{n[0]}中无效的{n[1]}值类型-无法比较'):
                    answer.add_sub_answers(f'{f[0]["n.name"]}{n[1]}是其的{res2}倍')
                answer.end_sub_answers()
        # 地区指标占总比的变化 & 指标占总比的变化
        elif qt in ('area_2_overall', 'index_2_overall'):
            years = '、'.join(result['year'])
            if qt == 'area_2_overall':
                unpack = True
                tag = '地区'
                gen = answer.product_data_with_feed(
                    result["area"], result["index"], flatten=True,
                    if_x_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na}的数据记录-无法比较',
                    if_y_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na}的父级数据记录-无法比较')
            else:
                unpack = False
                tag = '指标'
                gen = answer.product_data_with_feed(
                    result["index"],
                    if_x_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na}的数据记录-无法比较',
                    if_y_is_none=lambda _1, _2, _3, na: f'无{years}这几年{na}的父级数据记录-无法比较')

            data = self._search_double_direct_then_feed(chain, "n.name", unpack=unpack)
            feed_data = data[0], [data[1]], [data[2]]
            answer.feed_data(feed_data)
            for x, y, f, n in gen:
                temp = []  # 记录两次计算的结果值
                for i, year in enumerate(result["year"]):
                    answer.begin_sub_answers()
                    answer.add_sub_answers(f'{year}年{n}为{x[i][0]["r.value"]}{x[i][0]["r.unit"]}')
                    answer.add_sub_answers(f'其总体{tag}（{f[0][0]["n.name"]}）的为{y[i][0]["r.value"]}{y[i][0]["r.unit"]}')
                    res = answer.binary_calculation(x[i][0]["r.value"], y[i][0]["r.value"], truediv, percentage=True)
                    if answer.add_if_is_not_none(res, no=f'无效的{n}值类型-无法比较'):
                        answer.add_sub_answers(f'约占总体的{res}%')
                        temp.append(res)
                    answer.end_sub_answers()
                if len(temp) == 2:
                    num = round(temp[0] - temp[1], 2)
                    answer.add_answer(f'前者相比后者{sign(num, ("降低", "提高"))}{abs(num)}%')
        # 地区指标组成
        elif qt == 'area_compose':
            data = self._search_direct(chain)  # 若要使用各指标具体值，则使用self._search_direct_then_feed()
            answer.feed_data(data)
            for item, name in answer.product_data_with_name(
                    result['index'], if_is_none=lambda _, na: f'地区指标{name}没有任何子地区指标'):
                answer.add_answer(f'地区指标{name}的子地区集包括：' + '，'.join(n["a.name"] for n in item))
        # 地区指标倍数比较（只有两个地区） & 地区指标数量比较（只有两个地区）
        elif qt in ('areas_m_compare', 'areas_n_compare'):
            data = self._search_direct(chain)
            operator = truediv if qt == 'areas_m_compare' else sub
            answer.feed_data(data)
            for (x, y), (n1, n2) in answer.product_data_with_binary(
                    result['area'], result['index'],
                    if_x_is_none=lambda _1, _2, na: f'无{na[0][0]}{na[0][1]}数据记录-无法比较',
                    if_y_is_none=lambda _1, _2, na: f'无{na[1][0]}{na[1][1]}数据记录-无法比较'):
                # 单位检查
                ux, uy = x[0]['r.unit'], y[0]['r.unit']
                if answer.add_if_is_equal_or_not(ux, uy, no=f'{n1[0]}的单位（{ux}）与{n2[0]}的单位（{uy}）不同-无法比较'):
                    answer.begin_sub_answers()
                    answer.add_sub_answers(f'{n1[0]}{x[0]["r.repr"]}的{n1[1]}为{x[0]["r.value"]}{x[0]["r.unit"]}，'
                                           f'{n2[0]}{x[0]["r.repr"]}的{n2[1]}为{y[0]["r.value"]}{y[0]["r.unit"]}')
                    res1 = answer.binary_calculation(x[0]['r.value'], y[0]['r.value'], operator)
                    if answer.add_if_is_not_none(res1, no=f'{n1[0][0]}{n1[0][1]}或{n2[1][0]}{n2[1][1]}非数值类型-无法比较'):
                        if qt == 'areas_m_compare':
                            answer.add_sub_answers(f'前者是后者的{res1}倍')
                        else:
                            answer.add_sub_answers(f'前者比后者{sign(res1)}{abs(res1)}{x[0]["r.unit"]}')
                    if qt == 'areas_m_compare':
                        res2 = answer.binary_calculation(y[0]['r.value'], x[0]['r.value'], truediv)
                        if answer.add_if_is_not_none(res2, no=f'{n1[0][0]}{n1[0][1]}或{n2[1][0]}{n2[1][1]}非数值类型-无法比较'):
                            answer.add_sub_answers(f'后者是前者的{res2}倍')
                    answer.end_sub_answers()
        elif qt in ('areas_2m_compare', 'areas_2n_compare'):
            data = self._search_direct(chain, unpack=True)
            answer.feed_data(data)
            operator = truediv if qt == 'areas_2m_compare' else sub
            for item, name in answer.product_data_with_name(result["area"], result["index"], flatten=True):
                x, y = item
                if answer.binary_decision(x, y,
                                          not_x=f'无关于{result["year"][0]}年的{name}的记录',
                                          not_y=f'无关于{result["year"][0]}年的{name}的记录'):
                    res = answer.binary_calculation(x[0]["r.value"], y[0]["r.value"], operator)
                    if answer.add_if_is_not_none(res, no=f'{name}的记录为无效的值类型-无法比较', to_sub=False):
                        if qt == 'areas_2m_compare':
                            line = f'{result["year"][0]}年的{name}（{x[0]["r.value"]}{x[0]["r.unit"]}）' \
                                   f'是{result["year"][1]}年的（{y[0]["r.value"]}{y[0]["r.unit"]}）{res}倍'
                        else:
                            line = f'{result["year"][0]}年的{name}（{x[0]["r.value"]}{x[0]["r.unit"]}）' \
                                   f'比{result["year"][1]}年的（{y[0]["r.value"]}{y[0]["r.unit"]}）' \
                                   f'{sign(res, ("减少", "增加"))}{abs(res)}{x[0]["r.unit"]}'
                        answer.add_answer(line)
        # 地区指标值同比比较
        elif qt == 'areas_g_compare':
            data = self._search_direct(chain)
            answer.feed_data(data)
            for item, name in answer.product_data_with_name(result['area'], result['index'], flatten=True):
                x, y = item
                if answer.binary_decision(x, y,
                                          not_x=f'无{result["year"][0]}年关于{name}的数据',
                                          not_y=f'无{result["year"][0]}前一年关于{name}的数据'):
                    res = answer.growth_calculation(y[0]["r.value"], x[0]["r.value"])
                    if answer.add_if_is_not_none(res, to_sub=False,
                                                 no=f'{result["year"][0]}年{name}的记录非数值类型，无法计算'):
                        answer.add_answer(f'{result["year"][0]}年的{name}为{y[0]["r.value"]}{y[0]["r.unit"]}，'
                                          f'其去年的为{x[0]["r.value"]}{y[0]["r.unit"]}，'
                                          f'同比{sign(res, ("减少", "增长"))}{abs(res)}%')
        # 两年目录的变化 & 两年指标的变化
        elif qt in ('catalog_change', 'index_change'):
            data = self._search_direct(chain)
            unpack_key_name = qt[0] + '.name'
            tag_name = '指标' if qt == 'index_change' else '目录'
            set1, set2 = set([n[unpack_key_name] for n in data[0]]), set([n[unpack_key_name] for n in data[1]])
            diff1, diff2 = set1.difference(set2), set2.difference(set1)
            n1, n2 = len(diff1), len(diff2)
            if answer.add_if_is_equal_or_not(n1, 0, equal=False,
                                             no=f'{result["year"][1]}年与{result["year"][0]}年的{tag_name}相同'):
                answer.add_answer(f'{result["year"][1]}年与{result["year"][0]}年相比，未统计{n1}个{tag_name}：' + '、'.join(diff1))
            if answer.add_if_is_equal_or_not(n2, 0, equal=False,
                                             no=f'{result["year"][0]}年与{result["year"][1]}年的{tag_name}相同'):
                answer.add_answer(f'{result["year"][0]}年与{result["year"][1]}年相比，未统计{n2}个{tag_name}：' + '、'.join(diff2))
        # 指标值变化(多年份)
        elif qt in ('indexes_trend', 'areas_trend'):
            if qt == 'areas_trend':
                unpack = True
                gen = answer.product_data_with_name(result['area'], result['index'], flatten=True)
            else:
                unpack = False
                gen = answer.product_data_with_name(result['index'])
            # collect
            data = self._search_direct(chain, unpack=unpack)
            answer.feed_data(data)
            ys = []
            unit = data[0][0][0]['r.unit']
            for item, name in gen:
                print(item, name)
                y = answer.group_mapping_to_float(item, 'r.value')
                if answer.add_if_is_not_none(y, no=f'指标“{name}”非数值类型，无法比较', to_sub=False):
                    ys.append((name, y))
            # paint
            if len(ys) != 0:
                painter = Painter(result['year'], *ys, title=f'单位：{unit}', sub_title=result.raw_question)
                path = painter.paint_bar()
                answer.add_answer(f'该问题的回答已渲染为图像，详见：{path}')

        return answer.to_string()
