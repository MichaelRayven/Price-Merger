from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from scipy.interpolate import pchip
import numpy as np
import calendar


class GraphBuilder():
    def __init__(self, graph_data) -> None:
        self._data = self.__prepare_graph_data(graph_data)
        self.__configure_graph()
        self.__display_graph()

    def __prepare_graph_data(self, graph_data):
        graph_data["unixtime"] = list(map(lambda date: calendar.timegm(date.timetuple()), graph_data["dates"]))
        return graph_data

    def __configure_graph(self):
        plt.style.use('dark_background')

        plt.title("Price / Average Price Percentage")
        plt.ylabel("Price Percent")
        plt.xlabel("Month, Day")

        smooth_dates = np.linspace(
            self._data["unixtime"][0], self._data["unixtime"][-1], len(self._data["unixtime"]) * 20)
        smooth_prices = np.round(pchip(
            self._data["unixtime"], self._data["prices"])(smooth_dates), 2)
        smooth_dates = list(map(lambda unixtime: datetime.utcfromtimestamp(round(unixtime, 2)), smooth_dates))

        plt.plot_date(self._data["dates"], self._data["prices"], color="#fcba03", linestyle="solid", linewidth=3, label='Raw data')
        self._line, = plt.plot_date(smooth_dates, smooth_prices, fmt="", linewidth=1, color="#c934eb", linestyle="solid", label='Interpolated data')

        plt.gcf().autofmt_xdate()
        self._annot = plt.gca().annotate("", xy=(0, 0), xytext=(-20, 20), textcoords="offset points",
                                        bbox=dict(boxstyle="round", fc="w"),
                                        arrowprops=dict(arrowstyle="->"))

        plt.gcf().canvas.mpl_connect("motion_notify_event", self.__hover)
        plt.tight_layout()
        
        date_format = mpl_dates.DateFormatter('%b, %d')
        plt.gca().xaxis.set_major_formatter(date_format)

        plt.legend()

    def __update_annot(self, ind):
        x, y = self._line.get_data()
        self._annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = f"{self._annot.xy[1]}%"
        self._annot.set_text(text)
        self._annot.get_bbox_patch().set_alpha(0.6)

    def __hover(self, event):
        vis = self._annot.get_visible()
        if event.inaxes == plt.gca():
            cont, ind = self._line.contains(event)
            if cont:
                self.__update_annot(ind)
                self._annot.set_visible(True)
                plt.gcf().canvas.draw_idle()
            else:
                if vis:
                    self._annot.set_visible(False)
                    plt.gcf().canvas.draw_idle()

    def __display_graph(self):
        plt.show()
