# 问题解析器
from copy import deepcopy

from lib.result import Result
from lib.chain import TranslationChain
from lib.errors import QuestionYearOverstep


class QuestionParser:

    def __init__(self):
        self.chain = TranslationChain()

        # 基本sql语句, 供翻译方法使用
        self.sql_Y_status = 'match (y:Year) where y.name="{y}" return y.info'
        self.sql_C_status = 'match (y:Year)-[r:info]->(c:Catalog) where y.name="{y}" and c.name="{c}" return r.info'
        self.sql_I_value = 'match (y:Year)-[r:value]->(i:Index) where y.name="{y}" and i.name="{i}" return r.value,r.unit'
        self.sql_A_value = 'match (y:Year)-[r:`{i}`]->(n:Area) where y.name="{y}" and n.name="{a}" return r.value,r.unit,r.repr'

        self.sql_find_I_parent = 'match (n:Index)-[r:contain]->(m:Index) where m.name="{i}" return n.name,r.life'
        self.sql_find_A_parent = 'match (n:Area)-[r:contain]->(m:Area) where m.name="{a}" return n.name,r.life'
        self.sql_find_I_child = 'match (n:Index)-[r]->(m) where n.name="{i}" return m.name,labels(m)[0],r.life'
        self.sql_find_Is = 'match (y:Year)-[r:value]->(i:Index) where y.name="{y}" return i.name'
        self.sql_find_Cs = 'match (y:Year)-[r:include]->(c:Catalog) where y.name="{y}" return c.name'
        self.sql_find_begin_stats_Ys = 'match (y:Year)-[r:value]->(i:Index) where i.name="{i}" return y.name'

    def parse(self, result: Result) -> Result:
        for qt in result.question_types:
            # 查询语句翻译
            if qt == 'year_status':
                self.trans_year_status(result['year'])
            elif qt == 'catalog_status':
                self.trans_catalog_status(result['year'], result['catalog'])
            elif qt == 'exist_catalog':
                self.trans_exist_catalog(result['year'])
            elif qt in ('index_value', 'indexes_m_compare', 'indexes_n_compare'):
                self.trans_index_value(result['year'], result['index'])
            elif qt == 'index_overall':
                self.trans_index_overall(result['year'], result['index'])
            elif qt in ('index_2_overall', 'indexes_overall_trend'):
                self.trans_indexes_overall(result['year'], result['index'])
            elif qt == 'index_compose':
                self.trans_index_compose(result['year'], result['index'])
            elif qt in ('indexes_2m_compare', 'indexes_2n_compare'):
                self.trans_indexes_mn_compare(result['year'], result['index'])
            elif qt == 'indexes_g_compare':
                self.trans_indexes_g_compare(result['year'], result['index'])
            elif qt in ('area_value', 'areas_m_compare', 'areas_n_compare'):
                self.trans_area_value(result['year'], result['area'], result['index'])
            elif qt == 'area_overall':
                self.trans_area_overall(result['year'], result['area'], result['index'])
            elif qt in ('area_2_overall', 'areas_overall_trend'):
                self.trans_areas_overall(result['year'], result['area'], result['index'])
            elif qt in ('areas_2m_compare', 'areas_2n_compare'):
                self.trans_areas_mn_compare(result['year'], result['area'], result['index'])
            elif qt == 'areas_g_compare':
                self.trans_areas_g_compare(result['year'], result['area'], result['index'])
            elif qt in ('indexes_trend', 'indexes_max'):
                self.trans_indexes_value(result['year'], result['index'])
            elif qt in ('areas_trend', 'areas_max'):
                self.trans_areas_value(result['year'], result['area'], result['index'])
            elif qt in ('index_change', 'indexes_change'):
                self.trans_index_change(result['year'])
            elif qt in ('catalog_change', 'catalogs_change'):
                self.trans_catalog_change(result['year'])
            elif qt == 'begin_stats':
                self.trans_begin_stats(result['index'])

            result.add_sql(qt, deepcopy(self.chain))
            self.chain.reset()
        return result

    # 年度总体状况
    def trans_year_status(self, years):
        self.chain.make([self.sql_Y_status.format(y=years[0])])

    # 年度目录状况
    def trans_catalog_status(self, years, catalogs):
        self.chain.make([self.sql_C_status.format(y=years[0], c=c) for c in catalogs])

    # 指标变化情况
    def trans_index_change(self, years):
        self.chain.make([self.sql_find_Is.format(y=y) for y in years])

    # 目录变化情况
    def trans_catalog_change(self, years):
        self.chain.make([self.sql_find_Cs.format(y=y) for y in years])

    # 年度目录包含哪些
    def trans_exist_catalog(self, years):
        self.chain.make([self.sql_find_Cs.format(y=years[0])])

    # 指标值
    def trans_index_value(self, years, indexes):
        self.chain.make([self.sql_I_value.format(y=years[0], i=i) for i in indexes])

    # 多个年份指标值变化趋势
    def trans_indexes_value(self, years, indexes):
        self.chain.make([[self.sql_I_value.format(y=y, i=i) for y in years] for i in indexes])

    # 两个年份下的指标值的各种比较
    def trans_indexes_mn_compare(self, years, indexes):
        self.chain.make([[self.sql_I_value.format(y=y, i=i) for y in years] for i in indexes])

    # 指标值同比比较
    def trans_indexes_g_compare(self, years, indexes):
        last_year = int(years[0])-1
        QuestionYearOverstep.check(last_year)
        self.chain.make([[self.sql_I_value.format(y=last_year, i=i),
                          self.sql_I_value.format(y=years[0], i=i)] for i in indexes])

    # 指标占总比
    def trans_index_overall(self, years, indexes):
        self.chain.make([self.sql_I_value.format(y=years[0], i=i) for i in indexes])\
                  .then([self.sql_find_I_parent.format(i=i) for i in indexes])\
                  .then([self.sql_I_value.format(y=years[0], i='{}')])

    # 两或多个年份指标占总比的变化
    def trans_indexes_overall(self, years, indexes):
        self.chain.make([[self.sql_I_value.format(y=y, i=i) for y in years] for i in indexes])\
                  .then([self.sql_find_I_parent.format(i=i) for i in indexes])\
                  .then([self.sql_I_value.format(y=y, i='{}') for y in years])

    # 指标组成
    def trans_index_compose(self, years, indexes):
        self.chain.make([self.sql_find_I_child.format(i=i) for i in indexes]) \
                  .then([self.sql_I_value.format(y=years[0], i='{}') + ',r.child_id']) \
                  .then([self.sql_A_value.format(y=years[0], i='{}', a='{}') + ',r.child_id']) \
                  .then([self.sql_I_value.format(y=years[0], i=i) for i in indexes])  # overall

    # 地区指标值
    def trans_area_value(self, years, areas, indexes):
        self.chain.make([self.sql_A_value.format(y=years[0], i=i, a=a) for a in areas for i in indexes])

    def trans_areas_value(self, years, areas, indexes):
        self.chain.make([[[self.sql_A_value.format(y=y, i=i, a=a) for y in years] for a in areas] for i in indexes])

    # 两个年份下地区的指标值的各种比较
    def trans_areas_mn_compare(self, years, areas, indexes):
        self.chain.make([[[self.sql_A_value.format(y=y, a=a, i=i) for y in years] for a in areas] for i in indexes])

    # 地区指标值同比比较
    def trans_areas_g_compare(self, years, areas, indexes):
        last_year = int(years[0]) - 1
        QuestionYearOverstep.check(last_year)
        self.chain.make([[self.sql_A_value.format(y=last_year, a=areas[0], i=i),
                          self.sql_A_value.format(y=years[0], a=areas[0], i=i)] for i in indexes])

    # 地区指标占总比
    def trans_area_overall(self, years, areas, indexes):
        self.chain.make([self.sql_A_value.format(y=years[0], i=i, a=a) for a in areas for i in indexes])\
                  .then([self.sql_find_A_parent.format(a=a) for a in areas])\
                  .then([self.sql_A_value.format(y=years[0], i=i, a='{}') for i in indexes])

    # 地区两或多个年份指标占总比的变化
    def trans_areas_overall(self, years, areas, indexes):
        self.chain.make([[[self.sql_A_value.format(y=y, i=i, a=a) for y in years] for a in areas] for i in indexes])\
                  .then([self.sql_find_A_parent.format(a=a) for a in areas])\
                  .then([[self.sql_A_value.format(y=y, i=i, a='{}') for y in years] for i in indexes])

    # 何时开始统计此项指标
    def trans_begin_stats(self, indexes):
        self.chain.make([self.sql_find_begin_stats_Ys.format(i=i) for i in indexes])
