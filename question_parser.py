# 问题解析器
from functools import partial

from lib.result import Result


translation_dict = {}


def translation(func):
    """ 用于解析器翻译sql语句函数的装饰器 """
    translation_dict[func.__name__[6:]] = func


@translation  # 年度总体状况
def trans_year_status(years):
    return [f'match (y:Year) where y.name="{y}" return y.info' for y in years]


@translation  # 年度目录状况
def trans_catalog_status(years, catalogs):
    return [f'match (y:Year)-[r:info]->(c:Catalog) where y.name="{y}" and c.name="{c}" return r.info'
            for y in years for c in catalogs]


@translation  # 年度目录包含哪些
def trans_exist_catalog(years):
    return [f'match (y:Year)-[r:include]->(c:Catalog) where y.name="{y}" return c.name' for y in years]


@translation  # 指标值
def trans_index_value(years, indexes):
    return [f'match (y:Year)-[r:value]->(i:Index) where y.name="{y}" and i.name="{i}" return r.value, r.unit'
            for y in years for i in indexes]


class QuestionParser:

    def parse(self, result: Result) -> Result:
        for qt in result.question_types:
            sql = []
            # 查询语句翻译
            if qt == 'year_status':
                sql = self._sql_translate(qt, result['year'])
            elif qt == 'catalog_status':
                sql = self._sql_translate(qt, result['year'], result['catalog'])
            elif qt == 'exist_catalog':
                sql = self._sql_translate(qt, result['year'])
            elif qt == 'index_value':
                sql = self._sql_translate(qt, result['year'], result['index'])
            elif qt == '':
                pass

            result.add_sql(qt, sql)
            print(qt, sql)
        return result

    def _sql_translate(self, question_type: str, *args):
        # 查找对应翻译函数
        sql = []
        if not all(args):
            return sql
        translate_method = translation_dict.get(question_type)
        if translate_method:
            sql = partial(translate_method, *args)()
        return sql
