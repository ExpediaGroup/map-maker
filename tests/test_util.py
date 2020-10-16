import pytest

from shapely.geometry import (
    Point,
    box,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    MultiPoint,
)
from map_maker.util import to_shape, extract_geometries, get_bounds, to_geojson


def test_to_shape_wkt():
    """ Tests that the to_shape function works when the input shape is WKT.
    """
    shape_ser = "POINT( 0.0 0.0 )"
    truth = Point(0.0, 0.0)
    answer = to_shape(shape_ser)

    assert truth == answer


def test_to_shape_geojson():
    """ Tests that the to_shape function works when the input shape is
        GeoJSON.
    """
    shape_ser = """
    {
        "type": "Point",
        "coordinates": [0.0, 0.0]
    }
    """

    truth = Point(0.0, 0.0)
    answer = to_shape(shape_ser)

    assert truth == answer


def test_to_shape_non_serializable_string():
    """ Tests that the to_shape function returns a TypeError when the input
        is a non-geometric string.
    """

    with pytest.raises(TypeError):
        to_shape("POINT ( 0.0")


def test_to_shape_mapping():
    """ Tests that the to_shape function returns the correct value when the
        input is a mapping.
    """
    shape_ser = {"type": "Point", "coordinates": [0.0, 0.0]}
    truth = Point(0.0, 0.0)
    answer = to_shape(shape_ser)

    assert truth == answer


def test_to_shape_shape():
    """ Tests that the to_shape function returns the correct value when the
        input is a shape.
    """
    shape_ser = Point(0.0, 0.0)
    truth = Point(0.0, 0.0)
    answer = to_shape(shape_ser)

    assert truth == answer


def test_to_shape_non_serializable_object():
    """ Tests that the to_shape function raises a TypeError when the input
        is an object that is not serializable to a shape.
    """
    with pytest.raises(TypeError):
        to_shape(3)


def test_extract_geometries():
    """ Tests that the extract_geometries function returns the correct
        value.
    """
    shape_data = [
        {"shape": Point(0.0, 0.0), "color": "black", "x": 1},
        {
            "shape": MultiPoint([Point(1.0, 1.0), Point(2.0, 2.0)]),
            "color": "green",
            "x": 2,
        },
        {
            "shape": LineString([[0.0, 0.0], [1.0, 1.0]]),
            "color": "blue",
            "x": 2,
        },
        {
            "shape": MultiLineString(
                [[[0.0, 0.0], [1.0, 0.0]], [[0.0, 0.0], [0.0, 1.0]]]
            ),
            "color": "gray",
            "x": 3,
        },
        {"shape": box(0.0, 0.0, 1.0, 1.0), "color": "red", "x": 4},
        {
            "shape": MultiPolygon(
                box(0.0, 0.0, 0.5, 0.5), box(0.5, 0.5, 1.0, 1.0)
            ),
            "color": "green",
            "x": 5,
        },
    ]

    points, linestrings, polygons = extract_geometries(shape_data)

    assert len(points) == 3
    assert isinstance(points[0]["shape_obj"], Point)
    assert points[0]["color"] == "black"
    assert points[0]["x"] == 1
    assert isinstance(points[1]["shape_obj"], Point)
    assert points[1]["color"] == "green"
    assert points[1]["x"] == 2
    assert isinstance(points[2]["shape_obj"], Point)
    assert points[2]["color"] == "green"
    assert points[2]["x"] == 2
    assert isinstance(linestrings[0]["shape_obj"], LineString)
    assert linestrings[0]["x"] == 2
    assert isinstance(linestrings[1]["shape_obj"], MultiLineString)
    assert linestrings[1]["x"] == 3
    assert len(polygons) == 2
    assert isinstance(polygons[0]["shape_obj"], Polygon)
    assert polygons[0]["color"] == "red"
    assert polygons[0]["x"] == 4
    assert isinstance(polygons[1]["shape_obj"], MultiPolygon)
    assert polygons[1]["color"] == "green"
    assert polygons[1]["x"] == 5


def test_get_bounds():
    """ Tests that the _get_bounds function returns the correct value.
    """
    shape_data = [{"shape_obj": box(0.0, 0.0, 1.0, 1.0)}]

    truth = (0.0, 0.0, 1.0, 1.0)
    answer = get_bounds(shape_data)

    assert truth == answer


def test_to_geojson():
    """ Tests that the _to_geojson function returns the correct value.
    """
    shape_data = [
        {
            "shape_obj": Point(0.0, 0.0),
            "color": "green",
            "alpha": 0.3,
            "size": 2.0,
            "x": 1,
        }
    ]

    truth = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "color": "green",
                    "alpha": 0.3,
                    "size": 2.0,
                    "x": 1,
                },
                "geometry": {"type": "Point", "coordinates": (0.0, 0.0)},
            }
        ],
    }

    answer = to_geojson(shape_data, "blue", 1.0, 1.0)

    assert truth == answer


def test_to_geojson_default_color_alpha():
    """ Tests that the to_geojson function returns the correct value when
        default color, alpha and size are provided.
    """
    shape_data = [{"shape_obj": Point(0.0, 0.0), "x": 1}]

    truth = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "color": "blue",
                    "alpha": 1.0,
                    "size": 1.0,
                    "x": 1,
                },
                "geometry": {"type": "Point", "coordinates": (0.0, 0.0)},
            }
        ],
    }

    answer = to_geojson(shape_data, "blue", 1.0, 1.0)

    assert truth == answer
