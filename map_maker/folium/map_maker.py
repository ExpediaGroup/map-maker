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

import folium

from map_maker.util import extract_geometries, get_bounds, to_geojson
from toolz import dissoc


def _get_tooltip_keys(shape_datum):
    return list(
        dissoc(
            shape_datum, "shape", "shape_obj", "color", "alpha", "size"
        ).keys()
    )


def _get_tooltip_values(shape_datum):
    return [
        f"{k}: {v}"
        for k, v in dissoc(
            shape_datum, "shape", "shape_obj", "color", "alpha", "size"
        ).items()
    ]


def make_map_plot(
    map_data,
    plot_height=800,
    plot_width=800,
    tiles="cartodbpositron",
    point_size=2,
    polygon_line_width=2,
    linestring_width=2,
    tooltips={"points"},
):
    """ Creates a Folium map from a list of dicts with geometry / style info.

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

    tiles : str
        The tile source for the map. Default is CartoDB Positron.

    point_size : float, default 2.
        The size of the points to plot, if there are any points present.

    polygon_line_width: float, default 2.
        The line width of the polygon outline, if there are any polygons
        present.  Set to 0 to disable polygon outlines.

    linestring_width : float, default 2.
        The line with of the linestring, if there are any linestrings present.

    tooltips : set
        The labels of tooltips to display, can be "points", "linestrings",
        "polygons" or any combination of those.

    Returns
    -------
    fig : :obj:`folium.Map`
        The Folium object for the map.
    """
    # Collect the points and polygons.
    points, linestrings, polygons = extract_geometries(map_data, project=False)
    min_x, min_y, max_x, max_y = get_bounds(points + polygons)

    m = folium.Map(
        location=[(min_y + max_y) / 2, (min_x + max_x) / 2],
        tiles=tiles,
        height=plot_height,
        width=plot_width,
    )

    m.fit_bounds([(min_y, min_x), (max_y, max_x)])

    if polygons:
        polygon_geojson = to_geojson(
            polygons, "lightblue", 0.3, polygon_line_width
        )
        folium.GeoJson(
            polygon_geojson,
            style_function=lambda x: {
                "fillColor": x["properties"]["color"],
                "color": x["properties"]["color"],
                "weight": x["properties"]["size"],
                "fillOpacity": x["properties"]["alpha"],
            },
            tooltip=folium.GeoJsonTooltip(
                _get_tooltip_keys(polygon_geojson["features"][0]["properties"])
            )
            if "polygons" in tooltips
            else None,
        ).add_to(m)

    if linestrings:
        linestring_geojson = to_geojson(
            linestrings, "black", 0.3, linestring_width
        )
        folium.GeoJson(
            linestring_geojson,
            style_function=lambda x: {
                "color": x["properties"]["color"],
                "weight": x["properties"]["size"],
                "opacity": x["properties"]["alpha"],
            },
            tooltip=folium.GeoJsonTooltip(
                _get_tooltip_keys(
                    linestring_geojson["features"][0]["properties"]
                )
            )
            if "linestrings" in tooltips
            else None,
        ).add_to(m)

    if points:
        point_geojson = to_geojson(points, "black", 0.3, point_size)
        # Sigh .. have to manually add the circle markers instead of using the
        # geoJson function because geojson function doesn't allow custom
        # markers for points.
        # There's a PR that _should_ fix this:
        # https://github.com/python-visualization/folium/pull/957
        for point_feature in point_geojson["features"]:
            folium.CircleMarker(
                # Needs to be reversed because folium expects lat,lon.
                location=point_feature["geometry"]["coordinates"][::-1],
                # Divide by 2 to match what bokeh does with the size.
                radius=point_feature["properties"]["size"] / 2,
                color=point_feature["properties"]["color"],
                fill_color=point_feature["properties"]["color"],
                opacity=point_feature["properties"]["alpha"],
                tooltip="\n".join(
                    _get_tooltip_values(point_feature["properties"])
                )
                if "points" in tooltips
                else None,
            ).add_to(m)

    return m
