# 存放相关正则表达式

# 值的倍数关系比较
MultipleCmp = r'[\d]+年*的*([\D]+)(占[有据]*|是|为)([\D]+)'
# 值的多少关系比较
NumberCmp = r'[\d]+年*的*([\D]+)比([\D]+)(?:多(?!少)|(?<!多)少|增|长|加|高|减|低|降|大|小|变)+'

# 年份
Year = r'[\d零一二两三四五六七八九十千]+年*'
FormerYear = r'(去|大*前|上*)一*年'
# 年份范围
RangeYear = rf'({Year}([直至到往\-~—])*{Year})'
# 年份指代
RefsYear = (rf'({Year})[\D]*比{FormerYear}',
            rf'({Year})[与和同]+{FormerYear}相*比较*')
