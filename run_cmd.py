from question_classifier import QuestionClassifier
from question_parser import QuestionParser
from answer_search import AnswerSearcher
from lib.errors import QuestionError


class CAChatBot:

    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
        self.searcher = AnswerSearcher()

        self.max_fail_count = 3  # 记录最大失败次数，以便提示帮助
        self.count = 0

        print("欢迎与小航对话，请问有什么可以帮助您的？")

        self.default_answer = '抱歉！小航能力有限，无法回答您这个问题。可以联系开发者哟！'
        self.goodbye = '小航期待与你的下次见面，拜拜！'
        self.help = "help"

    def query(self, question: str) -> str:
        if self.count == self.max_fail_count:
            self.count = 0
            print(self.help)
        try:
            result = self.classifier.classify(question)
            if result is None or result.is_qt_null():
                self.count += 1
                return self.default_answer
            result = self.parser.parse(result)
            # self.searcher.search(sql_result)
            return 'answer'
        except QuestionError as err:
            self.count += 1
            return err.args[0]

    def run(self):
        while 1:
            question = input('[我]: ')
            if question.lower() == 'q':
                print(self.goodbye)
                break
            answer = self.query(question)
            print('[小航]: ', answer)


if __name__ == '__main__':
    chatbot = CAChatBot()
    chatbot.run()
