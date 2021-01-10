from question_classifier import QuestionClassifier
from question_parser import QuestionParser
from answer_search import AnswerSearcher
from lib.errors import QuestionError


class CAChatBot:

    def __init__(self, mode: str = 'cmd'):
        assert mode in ('cmd', 'notebook', 'web')

        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
        self.searcher = AnswerSearcher()

        self.mode = mode

        print("欢迎与小航对话，请问有什么可以帮助您的？")

        self.default_answer = '抱歉！小航能力有限，无法回答您这个问题。可以联系开发者哟！'
        self.goodbye = '小航期待与你的下次见面，拜拜！'

    def query(self, question: str):
        try:
            final_ans = ''
            # 开始查询
            result = self.classifier.classify(question)
            if result is None or result.is_qt_null():
                return self.default_answer
            result = self.parser.parse(result)
            answers = self.searcher.search(result)
            # 合并回答与渲染图表
            for answer in answers:
                final_ans += (answer.to_string().rstrip('。') + '。')
                if answer.have_charts() and self.mode != 'web':
                    answer.combine_charts()
                    answer.render_chart(result.raw_question)
            # 依不同模式返回
            if self.mode == 'notebook':
                return final_ans, answers[0].get_chart()  # None or chart
            elif self.mode == 'web':
                return final_ans, answers[0].get_charts()  # chart list
            else:  # default: 'cmd'
                return final_ans
        except QuestionError as err:
            return err.args[0]

    def run(self):
        while 1:
            question = input('[我]: ')
            if question.lower() == 'q':
                print(self.goodbye)
                break
            answer = self.query(question)
            print('[小航]: ', answer)
