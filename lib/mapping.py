# 存放相关映射

# 前缀-标签映射字典
PREFIX_LABEL_MAP = {
    'Y': "Year",     # 年份
    'C': "Catalog",  # 目录
    'I': "Index",    # 指标
    'A': "Area"      # 地区/机场/公司集团
}
# 前缀-结构关系映射字典
PREFIX_S_REL_MAP = {'Y-C': "include", 'C-I': "include", 'I-I': "contain",
                    'I-A': "locate", 'A-A': "contain", 'A-I': "of"}
# 前缀-值关系映射字典
PREFIX_V_REL_MAP = {'Y-C': "info", 'Y-I': "value", 'Y-A': None}

# 数字字符映射
Char2Digit = {'零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
              '六': '6', '七': '7', '八': '8', '九': '9', '两': '2', '千': '0', '十': ''}
# 指代字符映射
Ref2Digit = {'去': -1, '上': -1, '前': -2, '大': -1}
