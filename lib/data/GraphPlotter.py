import matplotlib.pyplot as plt


class GraphPlotter:
    def __init__(self, df):
        # type: (pd.DataFrame) -> GraphPlotter
        self.__df = df

    def saveGraphToFile(self, xColumns, yColumns, graphTitle, filePath):
        fig, ax = plt.subplots(figsize=(15,7))
        ax.title.set_text(graphTitle)

        # add all y columns to the graph
        for i in range (0, len(yColumns)):
            ax.plot(self.__df[xColumns[0]], self.__df[yColumns[i]])

        ax.grid(which='major', axis='both', linestyle='--')  # specify grid lines

        if len(yColumns) == 1:
            plt.ylabel(yColumns[0])

        if len(yColumns) == 1:
            # Hide legend because we added the name of y column as label to y axis
            ax.legend().set_visible(False)
        else:
            ax.legend().set_visible(True)

        self.__add_second_x_axis_if_necessary(ax, graphTitle, xColumns, yColumns)

        # save to file
        plt.savefig(filePath, format='png', dpi=300)

    def __add_second_x_axis_if_necessary(self, ax, graphTitle, xColumn, yColumns):
        if isinstance(xColumn, list):
            if len(xColumn) == 2:
                plt.title(graphTitle, y=1.08)
                axes_x_second = ax.twiny()
                axes_x_second.set_xlabel(xColumn[1])
                axes_x_second.plot(self.__df[xColumn[1]], self.__df[yColumns[0]])
                ax.set_xlabel(xColumn[0])
            else:
                plt.xlabel(xColumn)
        else:
            plt.xlabel(xColumn)

    def saveGraphToFileVertical(self, xColumn, yColumns, graphTitle, filePath):
        self.__df.plot(x=xColumn, y=yColumns, figsize=(10, 30), title=graphTitle)
        axis = plt.gca()

        # specify grid lines
        axis.grid(which='major', axis='both', linestyle='--')

        # add label to y-axis
        if (len(yColumns) == 1):
            plt.ylabel(yColumns[0])

        # Hide legend
        axis.legend().set_visible(False)

        # save to file
        plt.savefig(filePath, format='png', dpi=300)
