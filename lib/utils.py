
def read_words(path: str) -> list:
    # 加载词汇
    with open(path, encoding='utf-8') as f:
        return [w.strip('\n') for w in f]
