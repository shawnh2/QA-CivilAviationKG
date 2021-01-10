from const import DEBUG


def read_words(path: str) -> list:
    # 加载词汇
    with open(path, encoding='utf-8') as f:
        return [w.strip('\n') for w in f]


def write_to_file(filepath: str, lines: list):
    # 保存关键字词典到本地
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')


def sign(n: float, repr_: tuple = ('少', '多')):
    """ 以字符串的形式返回浮点数的正负号 """
    return repr_[0] if n < 0 else repr_[1]


def debug(*args):
    if DEBUG:
        print('DEBUG:', *args)
