import pandas as pd
import matplotlib
import matplotlib.pyplot as plot

matplotlib.interactive(True)


class Diagram:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def plot_line(self, col1: str, col2: str) -> None:
        plot.title(str(col1) + " - " + str(col2))
        plot.xlabel(col1)
        plot.ylabel(col2)
        plot.xticks(rotation=75)
        plot.plot(self.data.groupby(col1)[col2].mean())
        plot.show()

    def plot_scatter(self, col1: str, col2: str) -> None:
        plot.title(str(col1) + " - " + str(col2))
        plot.xlabel(col1)
        plot.ylabel(col2)
        plot.xticks(rotation=75)
        plot.scatter(self.data[col1].values, self.data[col2].values)
        plot.show()

    def plot_hist(self, col: str) -> None:
        plot.title(col + ' Histogram')
        plot.xlabel(col)
        plot.ylabel('Count')
        plot.xticks(rotation=90)
        if self.data[col].dtype == object:
            plot.hist(self.data[col], bins=len(self.data[col].unique())+1)
        else:
            plot.hist(self.data[col], bins=40)

        plot.show()

    def plot_box(self, col1: str, col2: str) -> None:
        x = sorted(self.data[col1].unique())
        t = [self.data[self.data[col1] == i][col2].values for i in x]
        fig, ax = plot.subplots(figsize=(10, 7))
        ax.set_title(str(col1) + " - " + str(col2))
        ax.set_xlabel(col1)
        ax.set_ylabel(col2)
        ax.set_xticklabels(x, rotation=90)
        ax.boxplot(t)
        plot.show()

    def plot_pie(self, col: str) -> None:
        labels = self.data[col].unique()
        sizes = [self.data[self.data[col] == i][col].count() for i in labels]
        theme = plot.get_cmap('jet')
        fig, ax = plot.subplots()
        ax.set_title(str(col) + ' Pie')
        patches, texts = ax.pie(sizes, colors=[theme(1. * i / len(sizes)) for i in range(len(labels))])
        ax.legend(patches, labels, title=col, loc='best',)
        plot.show()

    def plot_diagrams(self, col1: str, col2: str = None) -> None:
        if col2 is None:
            self.plot_pie(col1)
            self.plot_hist(col1)
        else:
            self.plot_line(col1, col2)
            self.plot_box(col1, col2)
            self.plot_scatter(col1, col2)
