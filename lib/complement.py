# 问题的填充
import re

from lib.regexp import Year
from lib.mapping import Char2Digit


def year_complement(question: str) -> str:
    """ 年份自动填充，转换各种表示为数字表示。
    例：11年 -> 2011年 ； 两千一十一年 -> 2011年 """

    years = re.compile(Year).findall(question)
    complemented = question

    def replace_and_padding(y: str) -> str:
        # 替换
        for k, v in Char2Digit.items():
            y = y.replace(k, v)
        # 填充
        if len(y) == 2:
            y = '20' + y
        return y

    for (year, gap) in years:
        year = year.strip('年')
        if not gap:
            new_year = replace_and_padding(year)
        else:
            start, end = year.split(gap)
            start_year, end_year = int(replace_and_padding(start)), int(replace_and_padding(end))
            new_year = ','.join([str(start_year + i) for i in range(end_year - start_year + 1)])
        complemented = complemented.replace(year, new_year)

    return complemented
