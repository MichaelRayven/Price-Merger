from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from scipy.interpolate import pchip
import numpy as np
import mplcursors


class GraphBuilder():
    def __init__(self, graph_data, barchart_data) -> None:
        self._graph_data = graph_data
        self._barchart_data = barchart_data
        self.__configure_graphs()
        self.__display_graph()

    def __calculate_unix(self, dates):
        return list(map(lambda date:  date.timestamp(), dates))

    def __month_barchart(self, ax, fig, y):
        x = range(12)
        bar = ax.bar(x, y, label="Monthly average")

        ax.set_xticks(x)
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May',
                           'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

        cursor = mplcursors.cursor(bar, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.arrow_patch.set(
                arrowstyle="simple", fc="white", alpha=.5)
            sel.annotation.get_bbox_patch().set(fc="gray", alpha=0.6)
            sel.annotation.set(text=y[sel.index])

    def __week_plot(self, ax, fig, x, y):
        unixtimes = self.__calculate_unix(x)
        smooth_dates = np.linspace(
            unixtimes[0], unixtimes[-1], len(unixtimes) * 20)
        smooth_prices = pchip(unixtimes, y)(smooth_dates)
        smooth_dates = list(
            map(lambda unix: datetime.utcfromtimestamp(round(unix, 2)), smooth_dates))

        ax.plot_date(x, y, color="#fcba03", linestyle="solid",
                     linewidth=3, label='Raw data')
        line, = ax.plot_date(smooth_dates, smooth_prices, marker="", linewidth=1,
                             color="#c934eb", linestyle="solid", label='Interpolated data')

        cursor = mplcursors.cursor(line, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.arrow_patch.set(
                arrowstyle="simple", fc="white", alpha=.5)
            sel.annotation.get_bbox_patch().set(fc="gray", alpha=0.6)
            sel.annotation.set(text=f"{round(sel.target[1], 2)}%")

        date_format = mpl_dates.DateFormatter('%b, %d')
        ax.xaxis.set_major_formatter(date_format)

    def __configure_graphs(self):
        plt.style.use('dark_background')
        # plt.style.use('seaborn')
        fig, ax = plt.subplots(nrows=2)

        self.__week_plot(ax[1], fig, self._graph_data["weeks"],
                         self._graph_data["prices"])
        self.__month_barchart(ax[0], fig, self._barchart_data["prices"])

        fig.suptitle("Price / Average Price Percentage")

        fig.supxlabel('Month and Day')
        fig.supylabel('Price Percentage')

        # fig.tight_layout()
        fig.legend()

    def __display_graph(self):
        plt.show()
