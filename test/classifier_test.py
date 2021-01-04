import os
import unittest

from question_classifier import QuestionClassifier
from lib.errors import QuestionError

os.chdir(os.path.join(os.getcwd(), '..'))


class QCTest(unittest.TestCase):

    qc = QuestionClassifier()

    def check_question(self, question: str):
        try:
            res = self.qc.classify(question).question_types
            return res if res else []
        except QuestionError:
            return []

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

    # 对比两年变化的目录
    def test_catalog_change(self):
        self.assertEqual(self.check_question('12年比11年多了哪些目录'), ['catalog_change'])
        self.assertEqual(self.check_question('12年比去年增加了哪些目录'), ['catalog_change'])
        self.assertEqual(self.check_question('12年比去年少了哪些标准？'), ['catalog_change'])
        self.assertEqual(self.check_question('12年与去年相比，目录变化如何？'), ['catalog_change'])

    # 对比两年变化的指标
    def test_index_change(self):
        self.assertEqual(self.check_question('12年比11年多了哪些指标'), ['index_change'])
        self.assertEqual(self.check_question('12年比去年增加了哪些指标'), ['index_change'])
        self.assertEqual(self.check_question('12年比去年少了哪些指标？'), ['index_change'])
        self.assertEqual(self.check_question('12年与去年相比，指标变化如何？'), ['index_change'])

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
    def test_index_1_overall(self):
        self.assertEqual(self.check_question('2011年的游客周转量占总体多少？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年的游客周转量占父指标多少份额？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年的游客周转量是总体的多少倍？'), ['index_overall'])
        self.assertEqual(self.check_question('2011游客周转量占总体的百分之多少？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年的游客周转量为其总体的多少倍？'), ['index_overall'])
        self.assertEqual(self.check_question('2011游客周转量占总量的多少？'), ['index_overall'])
        self.assertEqual(self.check_question('2011年游客周转量占有总额的多少比例？'), ['index_overall'])
        # 反例
        self.assertEqual(self.check_question('2011年总体是货邮周转量的百分之几？'), [])

    def test_index_2_overall(self):
        self.assertEqual(self.check_question('2012年游客周转量占总体的百分比比去年变化多少？'), ['index_2_overall'])
        self.assertEqual(self.check_question('2012年游客周转量占总体的百分比，相比11年变化多少？'), ['index_2_overall'])
        self.assertEqual(self.check_question('2012年相比11年，游客周转量占总体的百分比变化多少？'), ['index_2_overall'])
        self.assertEqual(self.check_question('2012年的游客周转量占总计比例比去年增加多少？'), ['index_2_overall'])
        self.assertEqual(self.check_question('2013年的游客周转量占父级的倍数比11年降低多少？'), ['index_2_overall'])

    # 指标同类之间的比较
    def test_indexes_1_compare(self):
        # 倍数比较
        self.assertEqual(self.check_question('2011年游客周转量是货邮周转量的几倍？'), ['indexes_m_compare'])
        self.assertEqual(self.check_question('2011年游客周转量是货邮周转量的百分之几？'), ['indexes_m_compare'])
        # 反例
        self.assertEqual(self.check_question('2011年总体是货邮周转量的几倍？'), [])
        self.assertEqual(self.check_question('2011年货邮周转量是货邮周转量的几倍？'), [])

        # 数量比较
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量多多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量大？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量少多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量增加了多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量降低了？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量降低了？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量变化了多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量比货邮周转量变了？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量与货邮周转量相比降低了多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量与货邮周转量比，降低了多少？'), ['indexes_n_compare'])
        self.assertEqual(self.check_question('11年旅客周转量与货邮周转量比较 降低了多少？'), ['indexes_n_compare'])
        # 反例
        self.assertEqual(self.check_question('2011年旅客周转量,货邮周转量比运输总周转量降低了？'), [])

        # 同比变化（只与前一年比较）
        self.assertEqual(self.check_question('2012年旅客周转量同比增长多少？'), ['indexes_g_compare'])
        self.assertEqual(self.check_question('2012年旅客周转量同比下降百分之几？'), ['indexes_g_compare'])
        self.assertEqual(self.check_question('2012年旅客周转量和货邮周转量同比下降百分之几？'), ['indexes_g_compare'])
        # 反例
        self.assertEqual(self.check_question('2012年旅客周转量同比13年下降百分之几？'), [])

    def test_indexes_2_compare(self):
        self.assertEqual(self.check_question('2011年游客周转量是12年的百分之几？'), ['indexes_2m_compare'])
        self.assertEqual(self.check_question('2011年的是12年游客周转量的百分之几？'), ['indexes_2m_compare'])
        self.assertEqual(self.check_question('2011年游客周转量占12的百分之？'), ['indexes_2m_compare'])
        self.assertEqual(self.check_question('2011年游客周转量是12年的几倍？'), ['indexes_2m_compare'])
        self.assertEqual(self.check_question('2011年游客周转量为12年的多少倍？'), ['indexes_2m_compare'])

        self.assertEqual(self.check_question('2011年游客周转量比12年降低了？'), ['indexes_2n_compare'])
        self.assertEqual(self.check_question('2012年游客周转量比去年增加了？'), ['indexes_2n_compare'])
        self.assertEqual(self.check_question('2012年游客周转量比去年多了多少？'), ['indexes_2n_compare'])
        self.assertEqual(self.check_question('12年的货邮周转量比去年变化了多少？'), ['indexes_2n_compare'])
        self.assertEqual(self.check_question('12年的货邮周转量同去年相比变化了多少？'), ['indexes_2n_compare'])
        self.assertEqual(self.check_question('13年的货邮周转量同2年前相比变化了多少？'), ['indexes_2n_compare'])
        self.assertEqual(self.check_question('12年同去年相比，货邮周转量变化了多少？'), ['indexes_2n_compare'])

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
    def test_area_1_overall(self):
        self.assertEqual(self.check_question('11年国内的运输总周转量占总体的百分之几？'), ['area_overall'])
        self.assertEqual(self.check_question('11年国际运输总周转量占总值的多少？'), ['area_overall'])
        self.assertEqual(self.check_question('11年港澳台运输总周转量是全体的多少倍？'), ['area_overall'])
        # 反例
        self.assertEqual(self.check_question('11年父级是港澳台运输总周转量的多少倍？'), [])

    def test_area_2_overall(self):
        self.assertEqual(self.check_question('2012年国内的游客周转量占总体的百分比比去年变化多少？'), ['area_2_overall'])
        self.assertEqual(self.check_question('2012年国际游客周转量占总体的百分比，相比11年变化多少？'), ['area_2_overall'])
        self.assertEqual(self.check_question('2012年相比11年，港澳台游客周转量占总体的百分比变化多少？'), ['area_2_overall'])
        self.assertEqual(self.check_question('2012年的国内游客周转量占总计比例比去年增加多少？'), ['area_2_overall'])
        self.assertEqual(self.check_question('2013年的国际游客周转量占父级的倍数比11年降低多少？'), ['area_2_overall'])

    # 地区指标与地区指标的比较
    def test_areas_1_compare(self):
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
        self.assertEqual(self.check_question('2011年港澳台游客周转量与国内的相比降低多少？'), ['areas_n_compare'])
        self.assertEqual(self.check_question('2011年港澳台与国内的相比游客周转量降低多少？'), ['areas_n_compare'])
        # 反例
        self.assertEqual(self.check_question('2011年国内比国际游客周转量少了？'), [])

        # 同比变化（只与前一年比较, 单地区多指标）
        self.assertEqual(self.check_question('2012年国内游客周转量同比增长了？'), ['areas_g_compare'])
        self.assertEqual(self.check_question('2012年国内游客周转量同比下降了多少？'), ['areas_g_compare'])
        self.assertEqual(self.check_question('2012年国内游客周转量和货邮周转量同比变化了多少？'), ['areas_g_compare'])
        # 反例
        self.assertEqual(self.check_question('2012年国内游客周转量和国际货邮周转量同比变化了多少？'), [])
        self.assertEqual(self.check_question('2012年国内游客周转量同比13年变化了多少？'), [])

    def test_areas_2_compare(self):
        self.assertEqual(self.check_question('11年港澳台运输总周转量是12年的多少倍？'), ['areas_2m_compare'])
        self.assertEqual(self.check_question('12年的是11年港澳台运输总周转量的多少倍？'), ['areas_2m_compare'])
        self.assertEqual(self.check_question('12年港澳台运输总周转量占11年百分之几？'), ['areas_2m_compare'])
        self.assertEqual(self.check_question('12年港澳台运输总周转量是11年比例？'), ['areas_2m_compare'])

        self.assertEqual(self.check_question('2011年国内游客周转量比一二年多多少？'), ['areas_2n_compare'])
        self.assertEqual(self.check_question('2012年港澳台游客周转量比上一年的少多少？'), ['areas_2n_compare'])
        self.assertEqual(self.check_question('2011年港澳台与国内的游客周转量相比12降低多少？'), ['areas_2n_compare'])
        self.assertEqual(self.check_question('2011年港澳台的游客周转量同2012相比降低多少？'), ['areas_2n_compare'])
        self.assertEqual(self.check_question('2012年的港澳台与去年相比，游客周转量降低多少？'), ['areas_2n_compare'])
        self.assertEqual(self.check_question('2013年的港澳台与两年前相比，游客周转量降低多少？'), ['areas_2n_compare'])
        # 反例
        self.assertEqual(self.check_question('2012年港澳台游客周转量比上一年的货邮周转量少多少？'), [])

    # 指标值变化(多年份)
    def test_indexes_trend(self):
        self.assertEqual(self.check_question('2011-13年运输总周转量的变化趋势如何？'), ['indexes_trend'])
        self.assertEqual(self.check_question('2011-13年运输总周转量情况？'), ['indexes_trend'])
        self.assertEqual(self.check_question('2011-13年运输总周转量值分布状况？'), ['indexes_trend'])
        self.assertEqual(self.check_question('2013年运输总周转量值与前两年相比变化状况如何？'), ['indexes_trend'])
        # 反例
        self.assertEqual(self.check_question('2011-12年运输总周转量的变化趋势如何？'), [])

    # 地区指标值变化(多年份)
    def test_areas_trend(self):
        self.assertEqual(self.check_question('2011-13年国内运输总周转量的变化趋势如何？'), ['areas_trend'])
        self.assertEqual(self.check_question('2011-13年国际运输总周转量情况？'), ['areas_trend'])
        self.assertEqual(self.check_question('2011-13年港澳台运输总周转量值分布状况？'), ['areas_trend'])

    # 占总指标比的变化
    def test_indexes_overall_trend(self):
        self.assertEqual(self.check_question('2011-13年运输总周转量占总体的比例的变化形势？'), ['indexes_overall_trend'])
        self.assertEqual(self.check_question('2011-13年运输总周转量占父级指标比的情况？'), ['indexes_overall_trend'])
        self.assertEqual(self.check_question('2011-13年运输总周转量值占总比的分布状况？'), ['indexes_overall_trend'])

    def test_areas_overall_trend(self):
        self.assertEqual(self.check_question('2011-13年国内运输总周转量占总体的比例的变化形势？'), ['areas_overall_trend'])
        self.assertEqual(self.check_question('2011-13年国际运输总周转量占父级指标比的情况？'), ['areas_overall_trend'])
        self.assertEqual(self.check_question('2011-13年港澳台运输总周转量值占总比的分布状况？'), ['areas_overall_trend'])

    # 指标的变化
    def test_indexes_change(self):
        self.assertEqual(self.check_question('2011-13年指标变化情况？'), ['indexes_change'])
        self.assertEqual(self.check_question('2011-13年指标变化趋势情况？'), ['indexes_change'])

    # 目录的变化
    def test_catalogs_change(self):
        self.assertEqual(self.check_question('2011-13年目录变化情况？'), ['catalogs_change'])
        self.assertEqual(self.check_question('2011-13年规范趋势情况变化？'), ['catalogs_change'])

    # 几个年份中的最值
    def test_indexes_and_areas_max(self):
        self.assertEqual(self.check_question('2011-13年运输总周转量最大值是？'), ['indexes_max'])
        self.assertEqual(self.check_question('2011-13年运输总周转量最小值是哪一年？'), ['indexes_max'])
        self.assertEqual(self.check_question('2011-13年国内运输总周转量最大值是？'), ['areas_max'])

    # 何时开始统计此指标
    def test_begin_stats(self):
        self.assertEqual(self.check_question('哪年统计了航空严重事故征候？'), ['begin_stats'])
        self.assertEqual(self.check_question('在哪一年出现了航空公司营业收入数据？'), ['begin_stats'])
        self.assertEqual(self.check_question('航空事故征候数据统计出现在哪一年？'), ['begin_stats'])
        self.assertEqual(self.check_question('运输周转量数据统计出现在哪一年？'), ['begin_stats'])


if __name__ == '__main__':
    unittest.main()
