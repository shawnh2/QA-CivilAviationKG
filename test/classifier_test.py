import os
import unittest

from question_classifier import QuestionClassifier

os.chdir(os.path.join(os.getcwd(), '..'))


class QCTest(unittest.TestCase):

    qc = QuestionClassifier()

    ys = 'year_status'
    cs = 'catalog_status'
    ec = 'exist_catalog'
    iv = 'index_value'
    iuc = 'index_up_compare'
    iic = 'index_index_compare'
    ic = 'index_compose'
    aiv = 'area_index_value'
    aic = 'area_index_compare'
    aac = 'area_area_compare'
    iac = 'index_area_compose'

    def check_question(self, question: str):
        return self.qc.classify(question).get('question_types')

    # 年度发展状况
    def test_year_status(self):
        self.assertEqual(self.check_question('2011年总体情况怎样？'), [self.ys])
        self.assertEqual(self.check_question('2011年发展形势怎样？'), [self.ys])
        self.assertEqual(self.check_question('2011年发展如何？'), [self.ys])
        self.assertEqual(self.check_question('11年形势怎样？'), [self.ys])

    # 年度某目录总体发展状况
    def test_catalog_status(self):
        self.assertEqual(self.check_question('2011年运输航空总体情况怎样？'), [self.cs])
        self.assertEqual(self.check_question('2011年航空安全发展形势怎样？'), [self.cs])
        self.assertEqual(self.check_question('2011年教育及科技发展如何？'), [self.cs])
        self.assertEqual(self.check_question('2011固定资产投资形势怎样？'), [self.cs])

    # 年度总体目录包括
    def test_exist_catalog(self):
        self.assertEqual(self.check_question('2011年有哪些指标目录？'), [self.ec])
        self.assertEqual(self.check_question('2011年有哪些基准？'), [self.ec])
        self.assertEqual(self.check_question('2011年有啥规格？'), [self.ec])
        self.assertEqual(self.check_question('2011年的目录有哪些？'), [self.ec])

    # 指标值
    def test_index_value(self):
        self.assertEqual(self.check_question('2011年的货邮周转量和游客周转量是多少？'), [self.iv])
        self.assertEqual(self.check_question('2011年的货邮周转量的值是？'), [self.iv])
        self.assertEqual(self.check_question('2011年的货邮周转量为？'), [self.iv])
        self.assertEqual(self.check_question('2011年的货邮周转量是'), [self.iv])

    # 指标与总指标的比较
    def test_index_up_compare(self):
        self.assertEqual(self.check_question('2011年的游客周转量占总体多少？'), [self.iuc])
        self.assertEqual(self.check_question('2011年的游客周转量占父指标多少份额？'), [self.iuc])
        self.assertEqual(self.check_question('2011年的游客周转量是总体的多少倍？'), [self.iuc])
        self.assertEqual(self.check_question('2011游客周转量占总体的百分之多少？'), [self.iuc])
        self.assertEqual(self.check_question('2011年的游客周转量为其总体的多少倍？'), [self.iuc])
        self.assertEqual(self.check_question('2011游客周转量占总量的多少？'), [self.iuc])
        self.assertEqual(self.check_question('2011年游客周转量占有总额的多少比例？'), [self.iuc])
        # 反例
        self.assertEqual(self.check_question('2011年总体是货邮周转量的百分之几？'), [])

    # 指标同类之间的比较
    def test_index_index_compare(self):
        self.assertEqual(self.check_question('2011年游客周转量是货邮周转量的几倍？'), [self.iic])
        self.assertEqual(self.check_question('2011年游客周转量是货邮周转量的百分之几？'), [self.iic])
        # 反例
        self.assertEqual(self.check_question('2011年总体是货邮周转量的几倍？'), [])
        self.assertEqual(self.check_question('2011年货邮周转量是货邮周转量的几倍？'), [])

    # 指标的组成
    def test_index_compose(self):
        self.assertEqual(self.check_question('2011年游客周转量的子集有？'), [self.ic])
        self.assertEqual(self.check_question('2011年游客周转量的组成？'), [self.ic])
        self.assertEqual(self.check_question('2011年游客周转量的子指标组成情况？'), [self.ic])

    # 地区指标值
    def test_area_index_value(self):
        self.assertEqual(self.check_question('11年国内的运输总周转量为？'), [self.aiv])
        self.assertEqual(self.check_question('11年国内和国际的运输总周转量为'), [self.aiv])
        self.assertEqual(self.check_question('11年国际方面运输总周转量是多少？'), [self.aiv])

    # 地区指标与总指标的比较
    def test_area_index_compare(self):
        self.assertEqual(self.check_question('11年国内的运输总周转量占总体的百分之几？'), [self.aic])
        self.assertEqual(self.check_question('11年国际运输总周转量占总值的多少？'), [self.aic])
        self.assertEqual(self.check_question('11年港澳台运输总周转量是全体的多少倍？'), [self.aic])
        # 反例
        self.assertEqual(self.check_question('11年父级是港澳台运输总周转量的多少倍？'), [])

    # 地区指标与地区指标的比较
    def test_area_area_compare(self):
        self.assertEqual(self.check_question('11年港澳台运输总周转量占国内的百分之几？'), [self.aac])
        self.assertEqual(self.check_question('11年国内的运输总周转量是港澳台的几倍？'), [self.aac])
        self.assertEqual(self.check_question('11年国际运输总周转量是国内的多少倍？'), [self.aac])
        self.assertEqual(self.check_question('11年港澳台运输总周转量是国际的多少倍？'), [self.aac])
        # 反例
        self.assertEqual(self.check_question('11年港澳台运输总周转量是国内游客周转量的多少倍？'), [])

    # 指标的地区组成
    def test_index_area_compose(self):
        self.assertEqual(self.check_question('11年运输总周转量各地情况如何？'), [self.iac])
        self.assertEqual(self.check_question('11年运输总周转量各地情况分布'), [self.iac])
        self.assertEqual(self.check_question('11年运输总周转量各地情况怎样？'), [self.iac])
        self.assertEqual(self.check_question('11年运输总周转量各区域情况怎样？'), [self.iac])
        self.assertEqual(self.check_question('11年运输总周转量组成地区情况'), [self.iac])
        self.assertEqual(self.check_question('11年运输总周转量和游客周转量的各组成地区情况'), [self.iac])


if __name__ == '__main__':
    unittest.main()
