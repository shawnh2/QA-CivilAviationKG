import os
import unittest

from question_classifier import QuestionClassifier

os.chdir(os.path.join(os.getcwd(), '..'))


class QCTest(unittest.TestCase):

    qc = QuestionClassifier()

    def check_question(self, question: str):
        return self.qc.classify(question).question_types

    # 年度发展状况
    def test_year_status(self):
        self.assertEqual(self.check_question('2011年总体情况怎样？'), ['year_status'])
        self.assertEqual(self.check_question('2011年发展形势怎样？'), ['year_status'])
        self.assertEqual(self.check_question('2011年发展如何？'), ['year_status'])
        self.assertEqual(self.check_question('11年形势怎样？'), ['year_status'])

    # 年度某目录总体发展状况
    def test_catalog_status(self):
        self.assertEqual(self.check_question('2011年运输航空总体情况怎样？'), ['catalog_status'])
        self.assertEqual(self.check_question('2011年航空安全发展形势怎样？'), ['catalog_status'])
        self.assertEqual(self.check_question('2011年教育及科技发展如何？'), ['catalog_status'])
        self.assertEqual(self.check_question('2011固定资产投资形势怎样？'), ['catalog_status'])

    # 年度总体目录包括
    def test_exist_catalog(self):
        self.assertEqual(self.check_question('2011年有哪些指标目录？'), ['exist_catalog'])
        self.assertEqual(self.check_question('2011年有哪些基准？'), ['exist_catalog'])
        self.assertEqual(self.check_question('2011年有啥规格？'), ['exist_catalog'])
        self.assertEqual(self.check_question('2011年的目录有哪些？'), ['exist_catalog'])

    # 指标值
    def test_index_value(self):
        self.assertEqual(self.check_question('2011年的货邮周转量和游客周转量是多少？'), ['index_value'])
        self.assertEqual(self.check_question('2011年的货邮周转量的值是？'), ['index_value'])
        self.assertEqual(self.check_question('2011年的货邮周转量为？'), ['index_value'])
        self.assertEqual(self.check_question('2011年的货邮周转量是'), ['index_value'])

    # 指标与总指标的比较
    def test_index_overall(self):
        self.assertEqual(self.check_question('2011年的游客周转量占总体多少？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年的游客周转量占父指标多少份额？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年的游客周转量是总体的多少倍？'), ['index_overall'])
        self.assertEqual(self.check_question('2011游客周转量占总体的百分之多少？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年的游客周转量为其总体的多少倍？'), ['index_overall'])
        self.assertEqual(self.check_question('2011游客周转量占总量的多少？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年游客周转量占有总额的多少比例？'), ['index_overall'])
        # 反例
        self.assertEqual(self.check_question('2011年总体是货邮周转量的百分之几？'), [])

    # 指标同类之间的比较
    def test_indexes_compare(self):
        # 倍数比较
        self.assertEqual(self.check_question('2011年游客周转量是货邮周转量的几倍？'), ['indexes_m_compare'])
        self.assertEqual(self.check_question('2011年游客周转量是货邮周转量的百分之几？'), ['indexes_m_compare'])
        # 反例
        self.assertEqual(self.check_question('2011年总体是货邮周转量的几倍？'), [])
        self.assertEqual(self.check_question('2011年货邮周转量是货邮周转量的几倍？'), [])
        # 数量比较
        self.assertEqual(self.check_question('2011年游客周转量比货邮周转量多多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('2011年游客周转量比货邮周转量大？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('2011年游客周转量比货邮周转量少多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('2011年游客周转量比货邮周转量增加了多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('2011年游客周转量比货邮周转量降低了？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('2011年游客周转量比货邮周转量降低了？'), ['indexes_n_compare'])
        # 反例
        self.assertEqual(self.check_question('2011年游客周转量,货邮周转量比某某某降低了？'), [])

    # 指标的组成
    def test_index_compose(self):
        self.assertEqual(self.check_question('2011年游客周转量的子集有？'), ['index_compose'])
        self.assertEqual(self.check_question('2011年游客周转量的组成？'), ['index_compose'])
        self.assertEqual(self.check_question('2011年游客周转量的子指标组成情况？'), ['index_compose'])

    # 地区指标值
    def test_area_value(self):
        self.assertEqual(self.check_question('11年国内的运输总周转量为？'), ['area_value'])
        self.assertEqual(self.check_question('11年国内和国际的运输总周转量为'), ['area_value'])
        self.assertEqual(self.check_question('11年国际方面运输总周转量是多少？'), ['area_value'])

    # 地区指标与总指标的比较
    def test_area_overall(self):
        self.assertEqual(self.check_question('11年国内的运输总周转量占总体的百分之几？'), ['area_overall'])
        self.assertEqual(self.check_question('11年国际运输总周转量占总值的多少？'), ['area_overall'])
        self.assertEqual(self.check_question('11年港澳台运输总周转量是全体的多少倍？'), ['area_overall'])
        # 反例
        self.assertEqual(self.check_question('11年父级是港澳台运输总周转量的多少倍？'), [])

    # 地区指标与地区指标的比较
    def test_areas_compare(self):
        # 倍数比较
        self.assertEqual(self.check_question('11年港澳台运输总周转量占国内的百分之几？'), ['areas_m_compare'])
        self.assertEqual(self.check_question('11年国内的运输总周转量是港澳台的几倍？'), ['areas_m_compare'])
        self.assertEqual(self.check_question('11年国际运输总周转量是国内的多少倍？'), ['areas_m_compare'])
        self.assertEqual(self.check_question('11年港澳台运输总周转量是国际的多少倍？'), ['areas_m_compare'])
        # 反例
        self.assertEqual(self.check_question('11年港澳台运输总周转量是国内游客周转量的多少倍？'), [])
        self.assertEqual(self.check_question('11年港澳台是国内游客周转量的多少倍？'), [])
        # 数量比较
        self.assertEqual(self.check_question('2011年国内游客周转量比国际多多少？'), ['areas_n_compare'])
        self.assertEqual(self.check_question('2011年港澳台游客周转量比国内的少多少？'), ['areas_n_compare'])
        # 反例
        self.assertEqual(self.check_question('2011年国内比国际游客周转量少了？'), [])

    # 指标的地区组成
    def test_area_compose(self):
        self.assertEqual(self.check_question('11年运输总周转量各地情况如何？'), ['area_compose'])
        self.assertEqual(self.check_question('11年运输总周转量各地情况分布'), ['area_compose'])
        self.assertEqual(self.check_question('11年运输总周转量各地情况怎样？'), ['area_compose'])
        self.assertEqual(self.check_question('11年运输总周转量各区域情况怎样？'), ['area_compose'])
        self.assertEqual(self.check_question('11年运输总周转量组成地区情况'), ['area_compose'])
        self.assertEqual(self.check_question('11年运输总周转量和游客周转量的各组成地区情况'), ['area_compose'])


if __name__ == '__main__':
    unittest.main()
