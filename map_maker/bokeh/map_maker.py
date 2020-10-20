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

import bokeh.plotting as bp
import json

from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import GeoJSONDataSource, HoverTool
from toolz import compose, dissoc
from map_maker.util import extract_geometries, get_bounds, to_geojson

listmap = compose(list, map)


def _get_tooltips(shape_datum):
    """ Generate the tooltip specifier for the plot.
    """
    return [
        (k, "@{}".format(k))
        for k in dissoc(
            shape_datum, "shape", "shape_obj", "color", "alpha", "size"
        )
    ]


def base_map_plot(
    x_range,
    y_range,
    tools="pan,wheel_zoom,reset",
    plot_height=800,
    plot_width=800,
    tiles=get_provider(Vendors.CARTODBPOSITRON_RETINA),
):

    """ Builds a blank map tile plot.

    Builds a blank figure with map tiles, but without axes, labels and ticks.

    Parameters
    ----------
    x_range : :obj:`list` of float
        The minimum and maximum x coordinates for the plot.

    y_range : :obj:`list` of float
        The minimum and maximum y coordinates for the plot.

    tools : str
        A comma separated list of strings defining the tools for the Bokeh
        plot widget.

    plot_height : float
        The height of the plot in px.

    plot_width : float
        The width of the plot in px.

    tiles : :obj:`bokeh.models.tiles.WMSTTileSource`
        The tile source for the blank map. Default is CartoDB Positron Retina.

    Returns
    -------
    fig : :obj:`bokeh.plotting.Figure`
        The Bokeh Figure for the blank map.
    """

    # Draw the main figure.
    p = bp.figure(
        tools=tools,
        plot_width=plot_width,
        plot_height=plot_height,
        x_range=x_range,
        y_range=y_range,
        # These are for axes and stuff.
        min_border=0,
        min_border_left=0,
        min_border_right=0,
        min_border_top=0,
        min_border_bottom=0,
    )

    p.axis.visible = False
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    # Now add the map tiles.
    p.add_tile(tiles)

    return p


def make_map_plot(
    map_data,
    plot_height=800,
    plot_width=800,
    tiles=get_provider(Vendors.CARTODBPOSITRON_RETINA),
    point_size=2,
    polygon_line_width=2,
    linestring_width=2,
    tooltips={"points"},
):
    """ Creates a Bokeh map from a list of dicts with geometry / style info.

    Takes a list of dictionaries, each of which has the following fields:

    .. code-block :: python

        {
            "shape": # WKT | GeoJSON String | Geo-Interface | Shapely Geometry
            "alpha": # Alpha value of the fill.
            "color": # Color of the shape
        }

    Parameters
    ----------
    map_data : :obj:`list` of :obj:`dict`
        A list of dictionaries defining the shape and style to map with the
        fields defined above.

    plot_height : int
        The height of the plot in px.

    plot_width : int
        The width of the plot in px.

    tiles : :obj:`bokeh.models.tiles.WMSTTileSource`
        The tile source for the map. Default is CartoDB Positron Retina.

    point_size : float, default 2.
        The size of the points to plot, if there are any points present.

    polygon_line_width: float, default 2.
        The line width of the polygon outline, if there are any polygons
        present.  Set to 0 to disable polygon outlines.

    linestring_width : float, default 2.
        The line width of the linestring, if there are any linestrings present.

    tooltips : set
        The labels of tooltips to display, can be "points", "linestrings",
        "polygons" or both any combination.

    Returns
    -------
    fig : :obj:`bokeh.plotting.Figure`
        The Bokeh Figure for the map.
    """
    # Collect the points and polygons.
    # The data's the same, with a 'shape_obj' field containing the shape
    # object.
    points, linestrings, polygons = extract_geometries(map_data)

    min_x, min_y, max_x, max_y = get_bounds(points + polygons)

    map_figure = base_map_plot(
        [min_x, max_x],
        [min_y, max_y],
        plot_height=plot_height,
        plot_width=plot_width,
        tiles=tiles,
    )

    # NOTE This assumes the first point / polygon is representative of all
    # fields. For CLI this is true, for a library call this may not be true.
    point_tooltips = _get_tooltips(points[0]) if points else None
    linestring_tooltips = (
        _get_tooltips(linestrings[0]) if linestrings else None
    )
    polygon_tooltips = _get_tooltips(polygons[0]) if polygons else None

    if point_tooltips and ("points" in tooltips):
        hover = HoverTool(tooltips=point_tooltips, names=["points"])

        map_figure.add_tools(hover)

    if linestring_tooltips and ("linestrings" in tooltips):
        hover = HoverTool(tooltips=linestring_tooltips, names=["linestrings"])

        map_figure.add_tools(hover)

    if polygon_tooltips and ("polygons" in tooltips):
        hover = HoverTool(tooltips=polygon_tooltips, names=["polygons"])

        map_figure.add_tools(hover)

    if points:
        map_figure.circle(
            x="x",
            y="y",
            size="size",
            alpha="alpha",  # Pulled from geojson properties.
            color="color",  # Pulled from geojson properties.
            line_width=0,
            source=GeoJSONDataSource(
                geojson=json.dumps(
                    to_geojson(points, "black", 0.3, point_size)
                )
            ),
            name="points",
        )
    if linestrings:
        map_figure.multi_line(
            xs="xs",
            ys="ys",
            line_alpha="alpha",
            color="color",
            line_width="size",
            source=GeoJSONDataSource(
                geojson=json.dumps(
                    to_geojson(linestrings, "black", 0.3, linestring_width)
                )
            ),
            name="linestrings",
        )
    if polygons:
        map_figure.patches(
            xs="xs",
            ys="ys",
            fill_alpha="alpha",  # Pulled from geojson properties.
            color="color",  # Pulled from geojson properties.
            line_width="size",
            source=GeoJSONDataSource(
                geojson=json.dumps(
                    to_geojson(polygons, "lightblue", 0.3, polygon_line_width)
                )
            ),
            name="polygons",
        )

    return map_figure
