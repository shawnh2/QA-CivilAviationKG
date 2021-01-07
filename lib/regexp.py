# 存放相关正则表达式
__all__ = ['MultipleCmp1', 'MultipleCmp2',
           'NumberCmp1', 'NumberCmp2',
           'GrowthCmp',
           'RangeYear', 'RefsYear']

# 值的倍数关系比较
MultipleCmp1 = r'[\d]+年*的*([\D]+)(占[有据]*|是|为)([\D]+)'
MultipleCmp2 = r'[\d]+年*的*([\D]*)(?:占[有据]*|是|为)[\d]+年*的*([\D]+)'
# 值的多少关系比较
NumberChange = r'(?:多(?!少)|(?<!多)少|增|长|加|高|减|低|降|大|小|变)+'
NumberCmp1 = rf'[\d]+年*的*([\D]+)(?<!同)比([\D]+){NumberChange}'  # 一元
NumberCmp2 = (rf'[\d]+年*的*([\D]+)(?<!同)比[\d]+年*的*{NumberChange}',
              rf'[\d]+年*的*([\D\d]+)年*的*(?<!同)比{NumberChange}',
              rf'[\d]+年*比[\d]+年*([\D]+){NumberChange}',
              rf'[\d]+年*([\D\d]+)(?<!同)比[，。,.]?([\D]+){NumberChange}')  # 二元
# 值的同比关系比较
GrowthCmp = r'[\d]+年*的*([\D]*)同比[增减上下升降变]+'

# 年份
Year = r'[\d零一二两三四五六七八九十千壹贰叁肆伍陆柒捌玖拾]+'
FormerYear = r'(去|大*前一*|上*一*)年'
# 年份范围
RangeYear = rf'({Year}年*([直至到往\-~—])*{Year})(?!年*前)'
# 年份指代
RefsYear = (rf'({Year})年*[\D]*[比是]+{FormerYear}',
            rf'({Year})年*[\D]*[与和同]+{FormerYear}相*比较*',
            rf'({Year})年*[\D]*[与和同]+({Year}年前)相*比较*',
            rf'({Year})年*[\D]*[与和同]+(前{Year}年)相*比较*')
