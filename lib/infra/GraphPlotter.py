from __future__ import annotations
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lib.infra.FolderStructure import FolderStructure


class GraphPlotter:
    def __init__(self, df):
        # type: (pd.DataFrame) -> GraphPlotter
        self.__df = df

    @staticmethod
    def createNew(df: pd.DataFrame, folder_struct: FolderStructure) -> GraphPlotter:
        plotter = GraphPlotter(df)
        plotter.__folder_struct = folder_struct
        return plotter

    #TODO: convert all users of GraphPlotter class to use createNew factory method above and this more concise generateGraph() function instead of saveGraphToFile
    def generate_graph(self, graph_title_suffix: str, columns_y: List):
        videofile_name = self.__folder_struct.getVideoFilename()
        graph_title = videofile_name + "_" + graph_title_suffix
        filename = self.__folder_struct.getSubDirpath() + "graph_" + videofile_name+ "_" + graph_title_suffix + ".png"
        x_axis_column = ["frameNumber"]
        self.saveGraphToFile(x_axis_column, columns_y, graph_title, filename)

    def saveGraphToFile(self, xColumns, yColumns, graphTitle, filePath):
        fig, ax = plt.subplots(figsize=(15,7))
        ax.title.set_text(graphTitle)

        # add all y columns to the graph
        for i in range (0, len(yColumns)):
            column_name = yColumns[i]
            plot = ax.plot(self.__df[xColumns[0]], self.__df[column_name])
            plot[0].set_label(column_name)

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


    def saveGraph_numpy(self, filepath_image: str, nparr: np):
        plt.figure(num=None, figsize=(30, 6), facecolor='w', edgecolor='k')
        plt.plot(nparr)
        plt.gca().grid(which='major', axis='both', linestyle='--', )  # specify grid lines
        plt.savefig(filepath_image, format='png', dpi=300)
