import os

from question_classifier import QuestionClassifier
from question_parser import QuestionParser

os.chdir(os.path.join(os.getcwd(), '..'))


class QPTest:
    qc = QuestionClassifier()
    qp = QuestionParser()

    def parse(self, question: str):
        res = self.qc.classify(question)
        if res.is_qt_null():
            print('[err]', question)
        else:
            print(self.qp.parse(res).sqls)

    def test(self):
        self.test_year_status()
        self.test_catalog_status()
        self.test_exist_catalog()
        self.test_index_overall()
        self.test_area_overall()
        self.test_index_compose()
        self.test_indexes_2mn_compare()
        self.test_areas_2mn_compare()
        self.test_indexes_g_compare()
        self.test_areas_g_compare()
        self.test_index_2_overall()
        self.test_area_2_overall()
        self.test_indexes_trend()
        self.test_areas_trend()

    def test_year_status(self):
        self.parse('2011年总体情况怎样？')
        self.parse('2011年发展形势怎样？')
        self.parse('2011年发展如何？')
        self.parse('11年形势怎样？')

    def test_catalog_status(self):
        self.parse('2011年运输航空总体情况怎样？')
        self.parse('2011年航空安全发展形势怎样？')
        self.parse('2011年教育及科技发展如何？')
        self.parse('2011固定资产投资形势怎样？')

    def test_exist_catalog(self):
        self.parse('2011年有哪些指标目录？')
        self.parse('2011年有哪些基准？')
        self.parse('2011年有啥规格？')
        self.parse('2011年的目录有哪些？')

    def test_index_overall(self):
        self.parse('2011年的游客周转量占总体多少？')
        self.parse('2011年的游客周转量占父指标多少份额？')
        self.parse('2011年的游客周转量是总体的多少倍？')
        self.parse('2011游客周转量占总体的百分之多少？')
        self.parse('2011年的游客周转量为其总体的多少倍？')
        self.parse('2011年游客周转量占有总额的多少比例？')
        self.parse('2011游客周转量占总量的多少？')

    def test_area_overall(self):
        self.parse('11年国内的运输总周转量占总体的百分之几？')
        self.parse('11年国际运输总周转量占总值的多少？')
        self.parse('11年港澳台运输总周转量是全体的多少倍？')

    def test_index_compose(self):
        self.parse('2011年游客周转量的子集有？')
        self.parse('2011年游客周转量的组成？')
        self.parse('2011年游客周转量的子指标组成情况？')

    def test_indexes_2mn_compare(self):
        self.parse('2011年游客周转量是12年的百分之几？')
        self.parse('2011年的是12年游客周转量的百分之几？')
        self.parse('2011年游客周转量占12年的百分之？')
        self.parse('2011年游客周转量是12年的几倍？')
        self.parse('2011年游客周转量比12年降低了？')
        self.parse('12年的货邮周转量比去年变化了多少？')
        self.parse('2012年游客周转量比去年多了多少？')
        self.parse('12年的货邮周转量同去年相比变化了多少？')
        self.parse('2011年游客周转量和货邮周转量为12年的多少倍？')

    def test_areas_2mn_compare(self):
        self.parse('11年港澳台运输总周转量是12年的多少倍？')
        self.parse('12年的是11年港澳台运输总周转量的多少倍？')
        self.parse('12年港澳台运输总周转量占11年百分之几？')
        self.parse('12年港澳台运输总周转量和游客周转量是11年比例？')
        self.parse('2011年国内游客周转量比一二年多多少？')
        self.parse('2012年港澳台游客周转量比上一年的少多少？')
        self.parse('2011年港澳台与国内的游客周转量相比12降低多少？')
        self.parse('2011年港澳台的游客周转量同2012相比降低多少？')

    def test_indexes_g_compare(self):
        self.parse('2012年游客周转量同比增长多少？')
        self.parse('2012年游客周转量同比下降百分之几？')
        self.parse('2012年游客周转量和货邮周转量同比下降百分之几？')

    def test_areas_g_compare(self):
        self.parse('2012年国内游客周转量同比增长了？')
        self.parse('2012年国内游客周转量同比下降了多少？')
        self.parse('2012年国内游客周转量和货邮周转量同比变化了多少？')

    def test_index_2_overall(self):
        self.parse('2012年游客周转量占总体的百分比比去年变化多少？')
        self.parse('2012年游客周转量占总体的百分比，相比11年变化多少？')
        self.parse('2012年相比11年，游客周转量占总体的百分比变化多少？')
        self.parse('2012年的游客周转量占总计比例比去年增加多少？')
        self.parse('2013年的游客周转量占父级的倍数比11年降低多少？')

    def test_area_2_overall(self):
        self.parse('2012年国内的游客周转量占总体的百分比比去年变化多少？')
        self.parse('2012年国际游客周转量占总体的百分比，相比11年变化多少？')
        self.parse('2012年相比11年，港澳台游客周转量占总体的百分比变化多少？')
        self.parse('2012年的国内游客周转量占总计比例比去年增加多少？')
        self.parse('2013年的国际游客周转量占父级的倍数比11年降低多少？')
        self.parse('2013年的国际和国内游客周转量占父级的倍数比11年降低多少？')

    def test_indexes_trend(self):
        self.parse('2011-13年运输总周转量的变化趋势如何？')
        self.parse('2011-13年运输总周转量情况？')
        self.parse('2011-13年运输总周转量值分布状况？')
        self.parse('2011-13年运输总周转量和游客周转量值分布状况？')

        self.parse('2011-13年运输总周转量占总体的比例的变化形势？')
        self.parse('2011-13年运输总周转量占父级指标比的情况？')
        self.parse('2011-13年运输总周转量值占总比的分布状况？')
        self.parse('2011-13年运输总周转量和游客周转量值占总比的分布状况？')

    def test_areas_trend(self):
        self.parse('2011-13年国内运输总周转量的变化趋势如何？')
        self.parse('2011-13年国际运输总周转量情况？')
        self.parse('2011-13年港澳台运输总周转量值分布状况？')
        self.parse('2011-13年港澳台和国际运输总周转量值分布状况？')

        self.parse('2011-13年国内运输总周转量占总体的比例的变化形势？')
        self.parse('2011-13年国际运输总周转量占父级指标比的情况？')
        self.parse('2011-13年港澳台运输总周转量值占总比的分布状况？')


if __name__ == '__main__':
    qp = QPTest()
    qp.test()
