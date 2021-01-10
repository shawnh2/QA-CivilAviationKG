import os
import unittest

from run_cmd import CAChatBot

os.chdir(os.path.join(os.getcwd(), '..'))


class QCErrTest(unittest.TestCase):
    bot = CAChatBot()

    def query(self, question: str):
        return self.bot.query(question)

    def test_order_err(self):
        self.assertEqual(self.query('11年总量是港澳台运输总周转量的多少倍？'), '不明白你所指的“总量”。是问反了吗？')

    def test_overstep_err(self):
        self.assertEqual(self.query('11年游客周转量同比增长？'), '年报中并未记录“2010”年的数据！')


if __name__ == '__main__':
    unittest.main()
