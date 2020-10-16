import pytest
import os
import json

from csv import DictReader
from shapely.geometry import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    mapping,
)
from shapely.wkt import loads as wkt_loads
from toolz import assoc

from map_maker.bokeh.map_maker import _get_tooltips, make_map_plot


@pytest.fixture()
def test_data():
    """ Fixture that reads in the test data.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_points = os.path.join(
        current_dir, "test_data/test_data_points.csv"
    )
    test_data_polygons_lines = os.path.join(
        current_dir, "test_data/test_data_polygons_lines.csv"
    )

    dataset = [line for line in DictReader(open(test_data_points, "r"))] + [
        line for line in DictReader(open(test_data_polygons_lines, "r"))
    ]

    return dataset


@pytest.fixture()
def test_data_shape(test_data):
    """ Fixture for the test data that has shape-serialized geometries.
    """
    return [assoc(td, "shape", wkt_loads(td["shape"])) for td in test_data]


@pytest.fixture()
def test_data_dict(test_data_shape):
    """ Fixture for the test data that has dict-serialized geometries.
    """
    return [assoc(td, "shape", mapping(td["shape"])) for td in test_data_shape]


@pytest.fixture()
def test_data_json(test_data_dict):
    """ Fixture for the test data that has json-serialized geometries.
    """
    return [
        assoc(td, "shape", json.dumps(td["shape"])) for td in test_data_dict
    ]


@pytest.fixture()
def test_data_multi(test_data_shape):
    """ Fixture for the test data that has shapes as multi-geometries.
    """
    points = [
        shp["shape"]
        for shp in test_data_shape
        if shp["shape"].geom_type == "Point"
    ]
    linestrings = [
        shp["shape"]
        for shp in test_data_shape
        if shp["shape"].geom_type == "LineString"
    ]
    polygons = [
        shp["shape"]
        for shp in test_data_shape
        if shp["shape"].geom_type == "Polygon"
    ]

    multi_point = MultiPoint(points)
    multi_linestring = MultiLineString(linestrings)
    multi_polygon = MultiPolygon(polygons)

    return [
        {"shape": multi_point, "color": "black", "alpha": 0.3},
        {"shape": multi_linestring, "color": "blue", "alpha": 0.2},
        {"shape": multi_polygon, "color": "red", "alpha": 0.1},
    ]


def test_get_tooltips():
    """ Tests that the _get_tooltips function returns the correct value.
    """
    shape_datum = {
        "shape_obj": Point(0.0, 1.0),
        "shape": "POINT ( 0.0 1.0 )",
        "color": "black",
        "alpha": 0.1,
        "size": 1.0,
        "x": "abc",
        "y": 123,
    }

    truth = [("x", "@x"), ("y", "@y")]
    answer = sorted(_get_tooltips(shape_datum), key=lambda x: x[0])

    assert truth == answer


def test_make_map_plot_wkt(test_data):
    """ Tests that the make_map_plot function can run on sample data in WKT
        format.
    """
    make_map_plot(test_data)


def test_make_map_plot_shape(test_data_shape):
    """ Tests that the make_map_plot function can run on sample data in shape
        format.
    """
    make_map_plot(test_data_shape)


def test_make_map_plot_dict(test_data_dict):
    """ Tests that the make_map_plot function can run on sample data in dict
        format.
    """
    make_map_plot(test_data_dict)


def test_make_map_plot_json(test_data_json):
    """ Tests that the make_map_plot function can run on sample data in json
        format.
    """
    make_map_plot(test_data_json)


def test_make_map_plot_multi(test_data_multi):
    """ Tests that the make_map_plot function can run on sample data that has
        multipolygons and multipoints.
    """
    make_map_plot(test_data_multi)


def test_make_map_plot_no_points(test_data_shape):
    """ Tests that the make_map_plot function can run on data that has no
        points.
    """
    no_points = [
        s for s in test_data_shape if not isinstance(s["shape"], Point)
    ]

    make_map_plot(no_points)


def test_make_map_plot_no_polygons(test_data_shape):
    """ Tests that the make_map_plot function can run on data that has no
        polygons.
    """
    no_polygons = [
        s for s in test_data_shape if not isinstance(s["shape"], Polygon)
    ]

    make_map_plot(no_polygons)


def test_make_map_plot_no_linestrings(test_data_shape):
    """ Tests that the make_map_plot function can run on data that has no
        linestrings.
    """
    no_linestrings = [
        s
        for s in test_data_shape
        if not isinstance(s["shape"], (LineString, MultiLineString))
    ]

    make_map_plot(no_linestrings)
