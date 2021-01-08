# 图表绘制器
import os

from pyecharts.charts import Bar, Pie, Page, Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType


class Painter:

    def __init__(self, ):
        self.path = 'results/qa-cakg-{}.html'

        if not os.path.exists('results'):
            os.mkdir('results')

    def paint_bar(self, x: list, *y: tuple, unit: str, title: str,  mark_point: bool = False):
        bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        bar.add_xaxis(x)
        for name, data in y:
            bar.add_yaxis(name, data)
        bar.set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                pos_left='5%'
            ),
            legend_opts=opts.LegendOpts(pos_bottom='0')
        )
        bar.set_series_opts(
            label_opts=opts.LabelOpts(position='top'),
            tooltip_opts=opts.TooltipOpts(formatter=f'{{b}}年{{a}}：{{c}}{unit}')
        )
        if mark_point:
            bar.set_series_opts(
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_='max', name='最大值'),
                        opts.MarkPointItem(type_='min', name='最小值')
                    ],
                    symbol_size=80
                )
            )
        return bar

    def paint_pie(self, data_pairs: list, units: list, title: str, sub_titles: list):
        page = Page()
        old_i = i = 10
        j = 60
        for data_pair, unit, sub_title in zip(data_pairs, units, sub_titles):
            pie = Pie(init_opts=opts.InitOpts(height='300px', width='auto'))
            for pairs in data_pair.values():
                pie.add(
                    unit, pairs,
                    radius=[60, 80], center=[f'{i}%', f'{j}%']
                )
                i += 20
            pie.set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title,
                    pos_left='5%',
                    subtitle=sub_title
                ),
                legend_opts=opts.LegendOpts(
                    pos_top='20%',
                    pos_left='5%'
                )
            )
            pie.set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),
                tooltip_opts=opts.TooltipOpts(formatter='{b}：{c}{a}（{d}%）')
            )
            page.add(pie)
            i = old_i
        return page

    def paint_bar_stack_with_line(self, x: list, children: dict, parents: dict, sub_title: str):
        page = Page()
        for (parent_name, unit), item in children.items():
            bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
            bar.add_xaxis(x)
            line = Line()
            line.add_xaxis(x)
            child_names = []
            for child_name, data, overall in item:
                bar.add_yaxis(child_name, data, stack='stack1')
                line.add_yaxis(f'{child_name}占比', overall, yaxis_index=1)
                child_names.append(child_name)
            bar.add_yaxis(
                parent_name,
                parents[parent_name],
                stack='stack1',
                yaxis_index=0
            )
            bar.set_global_opts(
                title_opts=opts.TitleOpts(
                    title='，'.join(child_names),
                    subtitle=sub_title,
                    pos_left='5%'
                ),
                legend_opts=opts.LegendOpts(pos_bottom='0')
            )
            bar.set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),
                tooltip_opts=opts.TooltipOpts(formatter=f'{{b}}年{{a}}：{{c}}{unit}'),
                itemstyle_opts=opts.ItemStyleOpts(opacity=0.5)
            )
            bar.extend_axis(
                yaxis=opts.AxisOpts(
                    type_='value',
                    name='所占比例',
                    min_=0,
                    max_=1,
                    position='right',
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True,
                        linestyle_opts=opts.LineStyleOpts(opacity=1)
                    )
                )
            )
            bar.overlap(line)
            page.add(bar)
        return page

    def paint_line(self, x: list, tag: str, y: list, title: str):
        line = Line()
        line.add_xaxis(x)
        line.add_yaxis(tag, y)
        line.set_global_opts(title_opts=opts.TitleOpts(title=title))
        return line

    # render

    def render_html(self, chart, name: str) -> str:
        path = self.path.format(name)
        chart.render(path)
        return path
