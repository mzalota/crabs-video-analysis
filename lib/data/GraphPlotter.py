import matplotlib.pyplot as plt

class GraphPlotter:
    def __init__(self, df):
        # type: (pd.DataFrame) -> GraphPlotter
        self.__df = df

    def saveGraphToFile(self, xColumn, yColumns, graphTitle, filePath):
        self.__df.plot(x=xColumn, y=yColumns, figsize=(15, 7), title=graphTitle)
        plt.gca().grid(which='major', axis='both', linestyle='--')  # specify grid lines
        plt.savefig(filePath, format='png', dpi=300)