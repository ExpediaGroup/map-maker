"""
Copyright 2020 Expedia, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import click
import csv
import sys
import webbrowser
import os

import bokeh.plotting as bp

from csv import DictReader

from bokeh.io import show

from map_maker.bokeh import make_map_plot as make_map_plot_bokeh
from map_maker.folium import make_map_plot as make_map_plot_folium

csv.field_size_limit(sys.maxsize)


@click.command()
@click.argument("map_data_files", type=str, nargs=-1)
@click.option(
    "--plot-height",
    "-h",
    type=int,
    help="The height of the plot. Default: 800",
    default=800,
)
@click.option(
    "--plot-width",
    "-w",
    type=int,
    help="The width of the plot. Default: 800",
    default=800,
)
@click.option(
    "--point-size",
    "-s",
    type=float,
    help="The size of the points. Default: 2.0.",
    default=2.0,
)
@click.option(
    "--polygon-line-width",
    "-l",
    type=float,
    help="Line width of the polygon outline.  Default 2.0. "
    "Set to 0 to disable polygon outlines.",
    default=2.0,
)
@click.option(
    "--linestring-width",
    "-L",
    type=float,
    help="Width of the linestrings. Default 2.0. ",
    default=2.0,
)
@click.option(
    "--output-file",
    "-o",
    type=str,
    help="The name of the output file for the map. Default: map.html.",
    default="map.html",
)
@click.option(
    "--tooltip",
    "-t",
    type=click.Choice(["points", "linestrings", "polygons"]),
    multiple=True,
    default={"points"},
    help="Whether to display tooltips for the points, linestrings, "
    "or polygons. Stackable. Default: points.",
)
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["bokeh", "folium"]),
    default="bokeh",
    help="The backend to draw the map with. Current choices are folium, bokeh."
    " Default: bokeh",
)
def cli(
    map_data_files,
    plot_height,
    plot_width,
    point_size,
    polygon_line_width,
    linestring_width,
    output_file,
    tooltip,
    backend,
):
    """
    Creates a map from the input files

    Arguments: \n
    MAP_DATA_FILES - The csv input file(s), requires the following columns:\n

        shape - The shape in WKT format, in EPSG:4326 lat/lon coordinates.\n
        color [optional] - The color as a string.\n
        alpha [optional] - The alpha as a float.\n
        size [optional] - For points, the size of the point. For linestrings
            and polygons, the width of the lines. \n
        others [optional] - Other fields turn into tooltips.\n

    Supports multiple files, which can be useful if the tooltip columns are
    different.
    """

    map_data = []
    for map_data_file in map_data_files:
        with open(map_data_file, "r") as map_file:
            reader = DictReader(map_file)
            map_data.extend([line for line in reader])

    if backend == "bokeh":
        map_plot = make_map_plot_bokeh(
            map_data,
            plot_height=plot_height,
            plot_width=plot_width,
            point_size=point_size,
            polygon_line_width=polygon_line_width,
            linestring_width=linestring_width,
            tooltips=tooltip,
        )

        bp.output_file(output_file)
        show(map_plot)
    elif backend == "folium":
        map_plot = make_map_plot_folium(
            map_data,
            plot_height=plot_height,
            plot_width=plot_width,
            point_size=point_size,
            polygon_line_width=polygon_line_width,
            linestring_width=linestring_width,
            tooltips=tooltip,
        )

        map_plot.save(output_file)
        webbrowser.open(
            "file://{}".format(os.path.realpath(output_file)), new=2
        )
