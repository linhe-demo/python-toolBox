from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Line
import webbrowser


class Highcharts:
    def __init__(self, tableType=None, name="chart", title=None, x_data=None, y_data=None):
        self.tableType = tableType
        self.path = "{}.html".format(name)
        self.title = title
        self.x_data = x_data
        self.y_data = y_data

    def draw(self):
        if self.tableType == "bar":
            # 创建柱状图对象
            bar = Bar()
            bar.add_xaxis(self.x_data)
            for i in self.y_data:
                bar.add_yaxis(i.get('name'), i.get('data'))
            bar.set_global_opts(title_opts=opts.TitleOpts(title=self.title))
            bar.render(self.path)

        elif self.tableType == 'line':
            # 创建折线图
            line = Line()
            line.add_xaxis(self.x_data)
            for i in self.y_data:
                line.add_yaxis(i.get('name'), i.get('data'))
            line.set_global_opts(title_opts=opts.TitleOpts(title=self.title))
            line.render(self.path)

        webbrowser.open(self.path)
