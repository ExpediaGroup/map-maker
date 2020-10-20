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

import json
import pyproj
import numpy as np

from contextlib import redirect_stderr
from collections import Mapping

from toolz import assoc, curry, dissoc, get
from shapely.wkt import loads as wkt_loads
from shapely.errors import WKTReadingError
from shapely.geometry import (
    shape,
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    mapping,
)
from shapely.ops import transform


lla_proj = pyproj.Proj(init="epsg:4326")
merc_proj = pyproj.Proj(init="epsg:3857")
lla_to_merc_proj = curry(pyproj.transform)(lla_proj, merc_proj)
lla_to_merc = curry(transform)(lla_to_merc_proj)


def to_shape(shape_ser):
    """ Deserializes a shape into a Shapely object - can handle WKT, GeoJSON,
        Python dictionaries and Shapely types.
    """
    if isinstance(shape_ser, str):
        try:
            # Redirecting stdout because there's a low level exception that
            # prints.
            with redirect_stderr("/dev/null"):
                shape_obj = wkt_loads(shape_ser)
        except WKTReadingError:
            try:
                shape_obj = shape(json.loads(shape_ser))
            except Exception:
                raise TypeError(
                    "{} is not serializable to a shape.".format(str(shape_ser))
                )
    elif isinstance(shape_ser, Mapping):
        shape_obj = shape(shape_ser)
    elif isinstance(
        shape_ser,
        (
            Point,
            MultiPoint,
            LineString,
            MultiLineString,
            Polygon,
            MultiPolygon,
        ),
    ):
        shape_obj = shape_ser
    else:
        raise TypeError(
            "{} is not serializable to a shape.".format(str(shape_ser))
        )

    return shape_obj


@curry
def _add_shape(sd, shape_obj):
    return assoc(sd, "shape_obj", shape_obj)


def extract_geometries(shape_data, project=True):
    """ Enhances the shape data by adding a 'shape_obj' field with the shapely
        object, and splits data into points and polygons.
    """
    points = []
    linestrings = []
    polygons = []
    for sd in shape_data:
        add_shape = _add_shape(sd)
        # Deserialize the shape.
        shape_obj = to_shape(sd["shape"])
        # Project to web mercator if required.
        if project:
            shape_obj = lla_to_merc(shape_obj)
        if isinstance(shape_obj, Point):
            points.append(add_shape(shape_obj))
        elif isinstance(shape_obj, MultiPoint):
            # Multipoints aren't supported in Bokeh so we have to convert.
            for point in shape_obj:
                points.append(add_shape(point))
        elif isinstance(shape_obj, (Polygon, MultiPolygon)):
            polygons.append(add_shape(shape_obj))
        elif isinstance(shape_obj, (MultiLineString, LineString)):
            linestrings.append(add_shape(shape_obj))

    return points, linestrings, polygons


def get_bounds(shape_data):
    """ Gets the bounds of the shapes. Shapes are shape data dictionaries with
        the actual shape in 'shape_obj'.
    """

    bounds_arr = np.array([sd["shape_obj"].bounds for sd in shape_data])
    minx = bounds_arr[:, 0].min()
    miny = bounds_arr[:, 1].min()
    maxx = bounds_arr[:, 2].max()
    maxy = bounds_arr[:, 3].max()
    return (minx, miny, maxx, maxy)


def to_geojson(shape_data, default_color, default_alpha, default_size):
    """ Turns the provided shape data dictionaries into GeoJSON strings. Adds
        default "color", "alpha", and "size" properties if they aren't present.
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    # These will be overwritten if present in the dict.
                    "color": default_color,
                    # Add a numeric conversion to the special numeric
                    # properties.
                    "alpha": float(get("alpha", sd, default_alpha)),
                    "size": float(get("size", sd, default_size)),
                    # Anything other than the shapes is a propertiy.
                    # Eventually these will turn into tooltips.
                    **dissoc(sd, "shape", "shape_obj", "size", "alpha"),
                },
                "geometry": mapping(sd["shape_obj"]),
            }
            for sd in shape_data
        ],
    }
