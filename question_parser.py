# 问题解析器
from lib.result import Result


class QuestionParser:

    def __init__(self):
        pass

    def parse(self, result: Result) -> Result:
        for qt in result.question_types:
            sql_dict = {'question_type': qt}
            sql = []

            if qt == '':
                sql = self._sql_translate(qt, )
            elif qt == '':
                pass

            sql_dict['sql'] = sql
            result.add_sql(sql_dict)

        return result

    def _sql_translate(self, question_type: str, entities: list):
        sql = []
        if not entities:
            return sql

        # 查询语句翻译
        if question_type == '':
            pass
