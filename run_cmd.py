from question_classifier import QuestionClassifier
from question_parser import QuestionParser
from answer_search import AnswerSearcher


class CAChatBot:

    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
        self.searcher = AnswerSearcher()

        self.default_answer = ''

    def run(self, q: str) -> str:
        classifier_result = self.classifier.classify(q)
        if not classifier_result:
            return self.default_answer
        sql_result = self.parser.parse(classifier_result)


if __name__ == '__main__':
    chatbot = CAChatBot()
    while 1:
        question = input('输入问题: ')
        answer = chatbot.run(question)
        print('[-]:', answer)
