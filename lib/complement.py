# 问题的填充
import re

import Levenshtein

from lib.utils import read_words
from lib.regexp import RangeYear, RefsYear
from lib.mapping import map_digits, map_refs


def year_complement(question: str) -> str:
    """ 年份自动填充，转换各种表示为数字表示。
    例：11年 -> 2011年
       两千一十一年 -> 2011年
       11-15年 -> 2011年,2012年,2013年,2014年,2015年
       13到15年 -> 2013年,2014年,2015年

       13年比前年 -> 2013年比2011年
       15年比大大前年 -> 2015年比2011年

       16年比3年前 -> 2016年比2013年
       16年与前三年相比 -> 2016年与2015年,2014年,2013年相比
    """
    complemented = question

    # 先填充范围
    range_years = re.compile(RangeYear).findall(question)
    last_year = ''
    for (year, gap) in range_years:
        year = year.strip('年')
        if not gap:
            new_year = map_digits(year)
        else:
            start, end = year.split(gap)
            start_year, end_year = int(map_digits(start)), int(map_digits(end))
            new_year = ','.join([str(start_year + i) for i in range(end_year - start_year + 1)])
        last_year = new_year
        complemented = complemented.replace(year, new_year)

    # 后填充指代
    for i, pattern in enumerate(RefsYear):
        ref_years = re.compile(pattern).findall(complemented)
        if ref_years:
            year = ref_years[0][-1]
            new_year = map_refs(year, i, int(last_year))
            complemented = complemented.replace(year, new_year)
            break

    return complemented


def index_complement(question: str, words: list,
                     len_threshold: int = 4,
                     ratio_threshold: float = 0.5) -> tuple:
    """对问题中的指标名词进行模糊查询并迭代返回最接近的项.

    :param question: 问题
    :param words: 查询范围(词集)
    :param len_threshold: 最小的有效匹配长度
    :param ratio_threshold: 最小匹配率
    :return: 首次匹配结果
    """
    charset = read_words('./data/dicts/fast_index_table.txt')[0]
    pattern = re.compile(f'([{charset}]+)')

    for result in pattern.findall(question):
        if len(result) < len_threshold or result in words:
            continue
        scores = []
        for word in words:
            score = Levenshtein.ratio(word, result)
            scores.append(score)
        # 得分最高的最近似
        max_score = max(scores)
        if max_score >= ratio_threshold:
            return words[scores.index(max_score)], result
    return None, None
