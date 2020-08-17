# 问题的填充
import re

from lib.regexp import RangeYear, RefsYear
from lib.mapping import Char2Digit, Ref2Digit


def year_complement(question: str) -> str:
    """ 年份自动填充，转换各种表示为数字表示。
    例：11年 -> 2011年
       两千一十一年 -> 2011年
       11-15年 -> 2011年,2012年,2013年,2014年,2015年
       13到15年 -> 2011年,2014年,2015年

       13年比前年 -> 2013年比2011年
       15年比大大前年 -> 2015年比2011年
    """
    complemented = question

    # 先填充范围
    range_years = re.compile(RangeYear).findall(question)

    def fill_range(y: str) -> str:
        # 替换
        for k, v in Char2Digit.items():
            y = y.replace(k, v)
        # 填充
        if len(y) == 2:
            y = '20' + y
        return y

    last_year = ''
    for (year, gap) in range_years:
        year = year.strip('年')
        if not gap:
            new_year = fill_range(year)
        else:
            start, end = year.split(gap)
            start_year, end_year = int(fill_range(start)), int(fill_range(end))
            new_year = ','.join([str(start_year + i) for i in range(end_year - start_year + 1)])
        last_year = new_year
        complemented = complemented.replace(year, new_year)

    # 后填充指代
    for pattern in RefsYear:
        ref_years = re.compile(pattern).findall(complemented)
        if ref_years:
            year = ref_years[0][-1]
            n = 0
            for ch in year:
                d = Ref2Digit.get(ch)
                if d:
                    n += d
            new_year = str(int(last_year) + n)
            complemented = complemented.replace(year, new_year)
            break

    return complemented


def index_complement(question: str, words: list):
    """ 对问题中的指标进行模糊查询 """
    charset = set("".join(words))
    pattern = re.compile(f'([{charset}]+)')

    for result in pattern.findall(question):
        scores = []
        for word in words:
            score = 0
            for c in result:
                if c in word:
                    score += 1
            scores.append(score*0.6 + score/len(word)*0.4)
        # 得分最高的最近似
        max_score = max(scores)
        if max_score > 0:
            indexes = [i for i, s in enumerate(scores) if s == max_score]
            yield list(map(lambda i: words[i], indexes))
