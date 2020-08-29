from lib.errors import QuestionError


def read_words(path: str) -> list:
    # 加载词汇
    with open(path, encoding='utf-8') as f:
        return [w.strip('\n') for w in f]


def write_to_file(filepath: str, lines: list):
    # 保存关键字词典到本地
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')


class InterruptAnswer(QuestionError):
    """ QuestionError对ChatBot有中断作用， 可用其做中断，提前返回一些回答。 """
    pass
