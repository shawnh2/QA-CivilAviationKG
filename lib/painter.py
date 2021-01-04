# 图表绘制器
import os

from pyecharts.charts import Bar, Pie, Page
from pyecharts import options as opts
from pyecharts.globals import ThemeType


class Painter:

    def __init__(self, ):
        self.path = 'results/qa-cakg-{}.html'

        if not os.path.exists('results'):
            os.mkdir('results')

    def paint_bar(self, x: list, *y: tuple, unit: str, title: str):
        bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        bar.add_xaxis(x)
        for name, data in y:
            bar.add_yaxis(name, data)
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title=title, pos_left='5%'),
            legend_opts=opts.LegendOpts(pos_top='5%', pos_left='5%')
        )
        bar.set_series_opts(
            label_opts=opts.LabelOpts(position='top'),
            tooltip_opts=opts.TooltipOpts(formatter=f'{{b}}年{{a}}：{{c}}{unit}')
        )
        return bar

    def paint_pie(self, data_pairs: list, units: list, title: str, sub_titles: list):
        pies = []
        page = Page()
        old_i, i, j = 10, 10, 60
        for data_pair, unit, sub_title in zip(data_pairs, units, sub_titles):
            pie = Pie(init_opts=opts.InitOpts(height='300px', width='auto'))
            for pairs in data_pair.values():
                pie.add(unit, pairs, radius=[60, 80], center=[f'{i}%', f'{j}%'])
                i += 10
            pie.set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left='5%', subtitle=sub_title),
                legend_opts=opts.LegendOpts(pos_top='20%', pos_left='5%')
            )
            pie.set_series_opts(
                label_opts=opts.LabelOpts(formatter='{b}：{c}', is_show=False),
                tooltip_opts=opts.TooltipOpts(formatter='{b}：{c}{a}（{d}%）')
            )
            pies.append(pie)
            i = old_i
        page.add(*pies)
        return page

    # render

    def render_html(self, graph, name: str) -> str:
        path = self.path.format(name)
        graph.render(path)
        return path
