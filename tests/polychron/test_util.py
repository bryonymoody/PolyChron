from __future__ import annotations

import copy
import pathlib
import time
from textwrap import dedent
from typing import Literal
from unittest.mock import patch

import networkx as nx
import packaging.version
import pytest
from networkx.drawing.nx_pydot import write_dot
from PIL import Image, ImageDraw
from pydot import Dot, graph_from_dot_data

from polychron import util


class TestUtil:
    """Unit tests for the util module, which is a collection of utility methods and classes."""

    def test_trim(self):
        """Test the image auto trimming method behaves as intended for several images"""

        # Define a helper function to create an inner rectangle of a nother color
        def create_test_image(
            size: tuple[int, int],
            color: tuple[int, int, int],
            rect: tuple[int, int, int, int] | None,
            rect_color: tuple[int, int, int] | None,
        ) -> Image.Image:
            """Helper fn to create a rectangular image of a specific color, which containse an inner rectangle of another color

            Parameters:
                size: width and height in pixels of the new image
                color: RGB values in the range [0, 255] for the background color
                rect: bbox and  color of the inner rectangle
            """
            img = Image.new("RGB", size, color)
            if rect is not None and rect_color is not None:
                draw = ImageDraw.Draw(img)
                draw.rectangle(rect, fill=rect_color, outline=None, width=1)
            return img

        # Create and trim a solid black image, which should maintain its size when trimmed
        img = create_test_image([100, 100], tuple([255, 255, 255]), None, None)
        trimmed = util.trim(img)
        assert trimmed.size == tuple([100, 100])

        # Create and trim a solid white image, which should maintain its size when trimmed
        img = create_test_image([100, 100], tuple([0, 0, 0]), None, None)
        # Trim the image, assert the new size
        trimmed = util.trim(img)
        assert trimmed.size == tuple([100, 100])

        # Create and trim a 100x100 white image with a 50x50 inner red rectangle, which shoud be 100x100
        img = create_test_image([100, 100], tuple([255, 255, 255]), [25, 25, 74, 74], tuple([255, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([100, 100])

        # Create and trim a 100x100 black image with a 50x50 inner red rectangle, which shoud be trimmed to the 50x50 red recangle
        img = create_test_image([100, 100], tuple([0, 0, 0]), [25, 25, 74, 74], tuple([255, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([50, 50])

        # Create and trim a 100x100 very dark grey image with a 50x50 inner red rectangle, which shoud be trimmed to the 50x50 red recangle
        img = create_test_image([100, 100], tuple([10, 10, 10]), [25, 25, 74, 74], tuple([255, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([50, 50])

        # Create and trim a 100x100 dark grey (100) image with a 50x50 inner red rectangle, which shoud be trimmed to the 50x50 red recangle
        img = create_test_image([100, 100], tuple([100, 100, 100]), [25, 25, 74, 74], tuple([255, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([50, 50])

        # Create and trim a 100x100 dark grey but over the threshold (101) image with a 50x50 inner red rectangle, which shoud be shoud be 100x100
        img = create_test_image([100, 100], tuple([101, 101, 101]), [25, 25, 74, 74], tuple([255, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([100, 100])

        # Check that all channels must be <= 100 for the trim to occur
        img = create_test_image([100, 100], tuple([101, 0, 0]), [25, 25, 74, 74], tuple([255, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([100, 100])
        img = create_test_image([100, 100], tuple([100, 0, 0]), [25, 25, 74, 74], tuple([255, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([50, 50])

        # Check that if the inner rect is also dark, but different to the outer, the crop is not performed.
        img = create_test_image([100, 100], tuple([0, 10, 20]), [25, 25, 74, 74], tuple([100, 0, 0]))
        trimmed = util.trim(img)
        assert trimmed.size == tuple([100, 100])

    @pytest.mark.parametrize(
        ("input", "expected"),
        [
            (
                "54,-180 0,-180 0,-144 54,-144 54,-180",
                [0.0, 54.0, -180.0, -144.0],
            ),
            (
                "54,-108 0,-108 0,-72 54,-72 54,-108",
                [0.0, 54.0, -108.0, -72.0],
            ),
            (
                "54,-36 0,-36 0,0 54,0 54,-36",
                [0.0, 54.0, -36.0, 0.0],
            ),
        ],
    )
    def test_bbox_from_polygon(self, input: str, expected: list[float]):
        """Test bbox_from_polygon behaves as expected for a range of inputs

        Todo:
            - Test other numbers of points.
        """
        # Call bbox_from_polygon with the parametrized input
        retval = util.bbox_from_polygon(input)
        assert retval == pytest.approx(expected)

    @pytest.mark.parametrize(
        ("cx", "cy", "rx", "ry", "expected"),
        [
            (164.75, -187.09, 33.6, 18, [131.15, 198.35, -205.09, -169.09]),
            (164.75, -115.09, 27, 18, [137.75, 191.75, -133.09, -97.09]),
            (164.75, -30.55, 30.59, 30.59, [134.16, 195.34, -61.14, 0.03999999]),
            (33.8, -187.09, 33.6, 18, [0.19999999999999574, 67.4, -205.09, -169.09]),
            (33.8, -115.09, 27, 18, [6.799999999999997, 60.8, -133.09, -97.09]),
            (33.8, -30.55, 30.59, 30.59, [3.2099999999999973, 64.39, -61.14, 0.03999999999999]),
        ],
    )
    def test_bbox_from_ellipse(self, cx: float, cy: float, rx: float, ry: float, expected: list[float]):
        """Test bbox_from_ellipse behaves as expected for a range of ellipse parameters"""
        # Call bbox_from_ellipse with the parametrized input,
        retval = util.bbox_from_ellipse(cx, cy, rx, ry)
        assert retval == pytest.approx(expected)

    def test_rank_func(self):
        """Test rank_func behaves as expected for a range of inputs

        Todo:
            - Expand the range of inputs which are tested
        """
        # Prepare input parameters for rank_func:
        # - A Dict containing the
        # Manually prepare a dictionary which is equivalent to the 0th return value from phase_info_func for the below stratigraphic dag. This is based on an actual value used
        map = {"1": ["c", "d", "e"], "2_below": ["b"]}

        # Manually prepare a dotstring, for a graph with 7 nodes in 2 groups
        dot_string = dedent("""\
        digraph g {
            splines=ortho;
            a [shape="box", Group=2];
            b [shape="box", Group=2];
            c [shape="box", Group=1];
            d [shape="box", Group=1];
            e [shape="box", Group=1];
            f [shape="box", Group=1];
            g [shape="box", Group=1];
            a -> b [arrowhead=none];
            e -> h [arrowhead=none];
            b -> c [arrowhead=none];
            b -> d [arrowhead=none];
            b -> e [arrowhead=none];
            d -> f [arrowhead=none];
        }
        """)

        # Call the fucntion
        mutated_dot_string = util.rank_func(map, dot_string)
        # Compare split lines of the original and mutated dot strings
        split_dot_string = dot_string.splitlines()
        split_mutated_string = mutated_dot_string.splitlines()
        # Other than the final 2 characters of the original string should be the same. This test case ensurese they are on separate lines.
        for mutated_line, original_line in zip(split_mutated_string[:-2], split_dot_string[:-2]):
            assert mutated_line == original_line

        # The second to last line should be a rank statement of the first group in the ordered dict
        assert split_mutated_string[-2] == "{rank = same; c; d; e;}"
        # The final line should be a rank statemnt of the second group in the ordered dict, plus the digraph closing bracet.
        assert split_mutated_string[-1] == "{rank = same; b;}}"

        # With an empty map, the new string should be the same as the old string
        mutated_dot_string = util.rank_func({}, dot_string)
        assert dot_string == mutated_dot_string

    @pytest.mark.parametrize(
        ("test_svg", "expected_coords", "expected_scale", "stderr"),
        [
            # Files using linux line endings, including a strat graph, a chrono graph and a test graph of shapes
            (
                "svg/lf/shapes.svg",
                {
                    "box": [36.75, 90.75, 4.0, 40.0],
                    "diamond": [3.75, 123.74, 76.0, 112.0],
                    "ellipse": [135.15, 202.35, 4.0, 40.0],
                    "oval": [141.75, 195.75, 76.0, 112.0],
                    "circle": [138.16, 199.34, 147.95, 209.13],
                },
                [206.54, 213.09],
                False,
            ),
            (
                "svg/lf/demo_strat.svg",
                {
                    "a": [76.0, 130.0, 4.0, 45.0],
                    "b": [76.0, 130.0, 81.0, 122.0],
                    "e": [4.0, 58.0, 158.0, 199.0],
                    "h": [4.0, 58.0, 235.0, 276.0],
                    "c": [76.0, 130.0, 158.0, 199.0],
                    "d": [148.0, 202.0, 158.0, 199.0],
                    "f": [148.0, 202.0, 235.0, 276.0],
                },
                [206.0, 280.0],
                False,
            ),
            (
                "svg/lf/demo_chrono.svg",
                {
                    "a": [76.0, 130.0, 100.0, 141.0],
                    "b": [76.0, 130.0, 177.0, 218.0],
                    "e": [13.0, 67.0, 350.0, 391.0],
                    "h": [4.0, 58.0, 427.0, 468.0],
                    "a_2 = b_1": [21.0, 185.0, 254.0, 314.0],
                    "a_1": [61.0, 145.0, 504.0, 564.0],
                    "c": [76.0, 130.0, 427.0, 468.0],
                    "d": [131.0, 185.0, 350.0, 391.0],
                    "b_2": [65.0, 141.0, 4.0, 64.0],
                },
                [189.0, 568.0],
                False,
            ),
            # Check windows line endings for a file with one of each shape
            (
                "svg/crlf/shapes.svg",
                {
                    "box": [36.75, 90.75, 4.0, 40.0],
                    "diamond": [3.75, 123.74, 76.0, 112.0],
                    "ellipse": [135.15, 202.35, 4.0, 40.0],
                    "oval": [141.75, 195.75, 76.0, 112.0],
                    "circle": [138.16, 199.34, 147.95, 209.13],
                },
                [206.54, 213.09],
                False,
            ),
            # Check how SVG with no nodes are handled, this should not occur in real usage
            (
                "svg/lf/no_nodes.svg",
                {},
                [206.54, 213.09],
                False,
            ),
            # An unfinished SVG
            (
                "svg/lf/invalid.svg",
                {},
                [],
                True,
            ),
            # An empty svg file
            (
                "svg/lf/empty.svg",
                {},
                [],
                True,
            ),
        ],
    )
    def test_node_coords_from_svg_string(
        self,
        test_svg: str,
        expected_coords: dict[str, list[float]],
        expected_scale: list[float],
        stderr: bool,
        test_data_path: pathlib.Path,
        capsys: pytest.CaptureFixture,
    ):
        """Test extraction of node coordinates from an svg string

        This can be an exact coordinate test, as we can test against stored svg files which were produced by graphviz

        Todo:
            - rectangular bounding boxes are always used for click detection, even for diamonds and ellipses. This may be problematic if graphviz does not ensure that the rectangular bounding box of a diamond/kite is free from other nodes.
            - Consider returning a dict instead of a dataframe.
        """
        # Open the input file in binary mode and cast to a string, so it has the literal characters rather than true line endings, matching usage in node_coords_from_dag
        input_path = test_data_path / test_svg
        with open(input_path, "r") as f:
            svg_string = f.read()
        capsys.readouterr()
        # Call node_coords_from_svg_string
        coords, scale = util.node_coords_from_svg_string(svg_string)
        captured = capsys.readouterr()
        # Check coordinates are as expected, with some float tolerance
        assert list(coords.keys()) == list(expected_coords.keys())
        for key in coords:
            assert list(coords[key]) == pytest.approx(list(expected_coords[key]))
        # Assert the scale is as expected, with some float tolerance
        assert scale == pytest.approx(expected_scale)
        if stderr:
            assert len(captured.err) != 0
        else:
            assert len(captured.err) == 0

    @pytest.mark.parametrize(
        ("test_svg", "type", "expected_coords", "expected_scale", "stderr"),
        [
            # Files using linux line endings, accessed via a string, or a pathlib.Path
            (
                "svg/lf/shapes.svg",
                "str",
                {
                    "box": [36.75, 90.75, 4.0, 40.0],
                    "diamond": [3.75, 123.74, 76.0, 112.0],
                    "ellipse": [135.15, 202.35, 4.0, 40.0],
                    "oval": [141.75, 195.75, 76.0, 112.0],
                    "circle": [138.16, 199.34, 147.95, 209.13],
                },
                [206.54, 213.09],
                False,
            ),
            (
                "svg/lf/shapes.svg",
                "pathlib.Path",
                {
                    "box": [36.75, 90.75, 4.0, 40.0],
                    "diamond": [3.75, 123.74, 76.0, 112.0],
                    "ellipse": [135.15, 202.35, 4.0, 40.0],
                    "oval": [141.75, 195.75, 76.0, 112.0],
                    "circle": [138.16, 199.34, 147.95, 209.13],
                },
                [206.54, 213.09],
                False,
            ),
            (
                "svg/lf/shapes.svg",
                "IO",
                {
                    "box": [36.75, 90.75, 4.0, 40.0],
                    "diamond": [3.75, 123.74, 76.0, 112.0],
                    "ellipse": [135.15, 202.35, 4.0, 40.0],
                    "oval": [141.75, 195.75, 76.0, 112.0],
                    "circle": [138.16, 199.34, 147.95, 209.13],
                },
                [206.54, 213.09],
                False,
            ),
        ],
    )
    def test_node_coords_from_svg(
        self,
        test_svg: str,
        type: Literal["str", "pathlib.Path", "IO"],
        expected_coords: dict[str, list[float]],
        expected_scale: list[float],
        stderr: bool,
        test_data_path: pathlib.Path,
        capsys: pytest.CaptureFixture,
    ):
        """Test extraction of node coordinates from an svg string

        This can be an exact coordinate test, as we can test against stored svg files which were produced by graphviz

        Todo:
            - rectangular bounding boxes are always used for click detection, even for diamonds and ellipses. This may be problematic if graphviz does not ensure that the rectangular bounding box of a diamond/kite is free from other nodes.
            - Consider returning a dict instead of a dataframe.
        """
        # Open the input file in binary mode and cast to a string, so it has the literal characters rather than true line endings, matching usage in node_coords_from_dag
        input_path = test_data_path / test_svg
        capsys.readouterr()
        # Call node_coords_from_svg, using the appropriate type of parameter
        if type == "str":
            coords, scale = util.node_coords_from_svg(str(input_path))
        elif type == "pathlib.Path":
            coords, scale = util.node_coords_from_svg(pathlib.Path(input_path))
        else:  # type == "IO"
            with open(input_path, "r") as f:
                coords, scale = util.node_coords_from_svg(f)
        captured = capsys.readouterr()
        # Check coordinates are as expected, with some float tolerance
        assert list(coords.keys()) == list(expected_coords.keys())
        for key in coords:
            assert list(coords[key]) == pytest.approx(list(expected_coords[key]))
        # Assert the scale is as expected, with some float tolerance
        assert scale == pytest.approx(expected_scale)
        if stderr:
            assert len(captured.err) != 0
        else:
            assert len(captured.err) == 0

    def test_node_coords_from_dag(self):
        """Test node_coords_from_dag behaves as expected for a range of inputs

        Due to non-determinism within graphviz layout generation, we cannot check the exact returned coordinates from the dynamically genrated svg, but that is covered by `test_node_coords_from_svg_string`

        Todo:
            - Call test_node_coords_from_dag less often, storing the coordinates when the png is re-rendered instead. Possibly even remove this method and operate on the svg which is rendered at the same time as the png.
        """

        # Get the node coordinates and scale for a nx.DiGraph
        g = nx.DiGraph()
        for node in ["a", "b", "c", "d"]:
            g.add_node(node, shape="box")
        for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]:
            g.add_edge(u, v)
        coords, scale = util.node_coords_from_dag(g)
        # Assert the types and shape of returned data is as it should be
        assert isinstance(coords, dict)
        assert set(coords.keys()) == set([node for node in g.nodes()])
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for bbox in coords.values():
            assert isinstance(bbox, list)
            assert len(bbox) == 4
            for f in bbox:
                assert isinstance(f, float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

        # Get the node coordinates and scale for a nx.DiGraph including contraction attributes, to ensure networkx < 3.4 compatibility (due to use of nx_pydot internally)
        g = nx.DiGraph()
        for node in ["a", "b", "c", "d"]:
            g.add_node(node, shape="box")
        for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]:
            g.add_edge(u, v)
        g = nx.contracted_nodes(g, "b", "c")
        g = nx.relabel_nodes(g, {"b": "b = c"})
        coords, scale = util.node_coords_from_dag(g)
        # Assert the types and shape of returned data is as it should be
        assert isinstance(coords, dict)
        assert set(coords.keys()) == set([node for node in g.nodes()])
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for bbox in coords.values():
            assert isinstance(bbox, list)
            assert len(bbox) == 4
            for f in bbox:
                assert isinstance(f, float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

        # Test with a pydot version of the graph already (which does not need to go through to_pydot)
        dot_string = dedent("""\
        digraph g {
            a [label="a", shape="box"];
            b [label="b", shape="box"];
            c [label="c", shape="box"];
            a -- b -- c;
        }""")
        pydot_g: Dot = graph_from_dot_data(dot_string)[0]
        coords, scale = util.node_coords_from_dag(pydot_g)
        # Assert the types and shape of returned data is as it should be
        assert isinstance(coords, dict)
        assert set(coords.keys()) == set([node.get_name() for node in pydot_g.get_nodes()])
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for bbox in coords.values():
            assert isinstance(bbox, list)
            assert len(bbox) == 4
            for f in bbox:
                assert isinstance(f, float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

        # Test with a graph that includes kites similar to how they are used in chronological graphs
        g = nx.DiGraph()
        for node in ["a", "b", "c", "d"]:
            g.add_node(node, shape="box")
        for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]:
            g.add_edge(u, v)
        # Add 2 kites/diamonds with edges(though the edges are not required for svg coord extraction, but this better mirrors the real usage)
        g.add_node("a_1", shape="diamond", fontsize="20.0", fontname="helvetica", penwidth="1.0")
        g.add_node("b_1", shape="diamond", fontsize="20.0", fontname="helvetica", penwidth="1.0")
        g.add_edge("a_1", "b_1", arrowhead="none")
        g.add_edge("a_1", "a", arrowhead="none")
        g.add_edge("b", "b_1", arrowhead="none")

        coords, scale = util.node_coords_from_dag(g)
        # Assert the types and shape of returned data is as it should be
        assert isinstance(coords, dict)
        assert set(coords.keys()) == set([node for node in g.nodes()])
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for bbox in coords.values():
            assert isinstance(bbox, list)
            assert len(bbox) == 4
            for f in bbox:
                assert isinstance(f, float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

        # Test with a graph that includes ellipses/ovals/circles
        # polychron currently (0.2.0) only explicitly sets box or diamond, so this is only for .dot inputs which explciitly set custom shapes?
        # Manually build a graph "ellipse" -> "oval" -> "circle"
        g = nx.DiGraph()
        g.add_node("ellipse", shape="ellipse")
        g.add_node("oval", shape="oval")
        g.add_node("circle", shape="circle")
        g.add_edge("ellipse", "oval")
        g.add_edge("oval", "circle")
        coords, scale = util.node_coords_from_dag(g)
        # Assert the types and shape of returned data is as it should be
        assert isinstance(coords, dict)
        assert set(coords.keys()) == set([node for node in g.nodes()])
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for bbox in coords.values():
            assert isinstance(bbox, list)
            assert len(bbox) == 4
            for f in bbox:
                assert isinstance(f, float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

    @pytest.mark.parametrize(
        ("coords", "img_size", "img_scale", "expected_node"),
        [
            # Check coords at expected places. Due to
            ((60, 30), (207, 214), 1.0, "box"),
            ((36.8, 4.1), (207, 214), 1.0, "box"),
            ((36.6, 4.0), (207, 214), 1.0, None),
            ((90.74, 39.9), (207, 214), 1.0, "box"),
            ((90.76, 40.1), (207, 214), 1.0, None),
            ((90, 90), (207, 214), 1.0, "diamond"),
            ((150, 20), (207, 214), 1.0, "ellipse"),
            ((150, 80), (207, 214), 1.0, "oval"),
            ((170, 180), (207, 214), 1.0, "circle"),
        ],
    )
    def test_node_coords_check(
        self, coords: tuple[float, float], img_size: tuple[int, int], img_scale: float, expected_node: str | None
    ):
        """Test the method which returns the node which is at a given set of coordinates, after scaling and zooming may have occurred"""
        # Uses a single set of node_coords / node_coords_scale to avoid excessive duplication in parametrisation
        node_coords = {
            "box": [36.75, 90.75, 4.0, 40.0],
            "diamond": [3.75, 123.74, 76.0, 112.0],
            "ellipse": [135.15, 202.35, 4.0, 40.0],
            "oval": [141.75, 195.75, 76.0, 112.0],
            "circle": [138.16, 199.34, 147.95, 209.13],
        }
        node_coords_scale = [207, 214]
        # Call node_coords_check
        node = util.node_coords_check(coords, img_size, img_scale, node_coords, node_coords_scale)
        # Check the result is as expected
        assert node == expected_node

    @pytest.mark.skip(reason="test_phase_info_func not yet implemented")
    def test_phase_info_func(self):
        """Test phase_info_func behaves as expected for a range of inputs

        Todo:
            - Test with a .gv/.dot provided graph
        """
        pass

    @pytest.mark.skip(reason="test_edge_of_phase not yet implemented")
    def test_edge_of_phase(self):
        """Test edge_of_phase behaves as expected for a range of inputs

        Todo:
            - Test with a .gv/.dot provided graph
        """
        pass

    def test_node_del_fixed(self):
        """Test node_del_fixed behaves as expected for a range of inputs"""
        # Using the graph
        #   a
        #  / \
        # b0  b1
        #  \ /
        #   c
        g_original = nx.DiGraph([("a", "b0"), ("a", "b1"), ("b0", "c"), ("b1", "c")])

        # Test removing a node which only has outgoing edges, i.e. a
        g_in = copy.deepcopy(g_original)
        g_out = util.node_del_fixed(g_in, "a")
        # Assert that a is no longer in the graph
        assert not g_out.has_node("a")
        # Assert that b0 and b1 no longer have any in edges
        assert len(g_out.in_edges("b0")) == 0
        assert len(g_out.in_edges("b1")) == 0

        # phase_relabel currently mutates and returns the provided graph - i.e. they are the same object.
        assert id(g_in) == id(g_out)

        # Test removing a node which only has incoming edges, i.e. c
        g_in = copy.deepcopy(g_original)
        g_out = util.node_del_fixed(g_in, "c")
        # Assert that c is no longer in the graph
        assert not g_out.has_node("c")
        # Assert that b0 and b1 no longer have any out edges
        assert len(g_out.out_edges("b0")) == 0
        assert len(g_out.out_edges("b1")) == 0

        # Test removing a node which has incoming and outgoing edges, while there is another node providing the same implicit relationships i.e. b0. The graph should now be a -> b1 -> c
        g_in = copy.deepcopy(g_original)
        g_out = util.node_del_fixed(g_in, "b0")
        # Assert that b is no longer in the graph
        assert not g_out.has_node("b0")
        # Assert that a has one less out edge
        assert len(g_out.out_edges("a")) == len(g_original.out_edges("a")) - 1
        # Assert that d has one less in edge
        assert len(g_out.in_edges("c")) == len(g_original.in_edges("c")) - 1
        # Assert the original path from a->b1->c remains
        assert g_out.has_edge("a", "b1")
        assert g_out.has_edge("b1", "c")

        # Test removing 2 nodes which have incoming and outgoing edges, that would be replaced by the same edge. This should result in a graph with edge(s) from a->c.
        g_in = copy.deepcopy(g_original)
        g_out = util.node_del_fixed(g_in, "b0")
        g_out = util.node_del_fixed(g_out, "b1")
        # Assert that b0 and b1 are no longer in the graph
        assert not g_out.has_node("b0")
        assert not g_out.has_node("b1")
        # There should now be a path from a->c, with a single edge
        assert len(g_out.edges) == 1
        assert g_out.has_edge("a", "c")

        # Test trying to remove an edge which is not present in the graph
        g_in = copy.deepcopy(g_original)
        assert not g_in.has_node("foo")
        with pytest.raises(nx.NetworkXError):
            g_out = util.node_del_fixed(g_in, "foo")

    @pytest.mark.skip(reason="test_all_node_info not yet implemented, requires .dot input file")
    def test_all_node_info(self):
        """Test all_node_info behaves as expected for a range of inputs"""
        pass

    @pytest.mark.parametrize(
        ("con_1", "con_2", "expected_lengths"),
        [
            # "normal" usage with valid context/group_boundaries
            ("ctx_a", "ctx_b", [500.0, 500.0, 500.0, 500.0]),
            ("ctx_c", "a_1", [2999.5, 2998.5, 2997.5, 2996.5]),
            ("a_1", "ctx_c", [2999.5, 2998.5, 2997.5, 2996.5]),
            ("b_1", "a_1 = b_1", [1000.0, 1002.0, 1004.0, 1006.0]),
            # duration between a context and itself
            ("ctx_a", "ctx_a", [0.0, 0.0, 0.0, 0.0]),
            # invalid context/group_boundary checks
            ("", "ctx_b", []),
            ("ctx_a", "", []),
            ("missing", "other", []),
        ],
    )
    def test_phase_length_finder(self, con_1: str, con_2: str, expected_lengths: list[str]):
        """Test phase_length_finder behaves as expected for a range of inputs"""

        # Prepare a dictionary, mirroring the structure of MCMCData.accept_group_limits / all_group_limits, including negative values
        group_limits = {
            "ctx_a": [3000.0, 3001.0, 3002.0, 3003.0],
            "ctx_b": [2500.0, 2501.0, 2502.0, 2503.0],
            "ctx_c": [1000.5, 1001.5, 1002.5, 1003.5],
            "a_1": [4000.0, 4000.0, 4000.0, 4000.0],
            "b_1": [0000.0, 0001.0, 0002.0, 0003.0],
            "a_1 = b_1": [-1000.0, -1001.0, -1002.0, -1003.0],
        }

        # Check the result when phase_length_finder is provided the parametrised con_1/con_2
        lengths = util.phase_length_finder(con_1, con_2, group_limits)
        assert isinstance(lengths, list)
        assert len(lengths) == len(expected_lengths)
        assert lengths == pytest.approx(expected_lengths)

    def test_phase_length_finder_invalid_group_limits(self):
        """Test that phase_length finder behaves with an invalid group_limits data structure"""
        # Define an invalid group_limits with a mismatching number of entries for 2 contexts

        group_limits = {"ctx_a": [1, 2, 3, 4, 5], "ctx_b": [10, 20]}
        # Assert graceful failure?
        lengths = util.phase_length_finder("ctx_a", "ctx_b", group_limits)
        assert isinstance(lengths, list)
        assert lengths == [9, 18]

    @pytest.mark.skip(reason="test_imagefunc not yet implemented, requires .dot input file")
    def test_imagefunc(self):
        """Test imagefunc behaves as expected for a range of inputs"""
        pass

    def test_phase_relabel(self):
        """Test phase_relabel behaves as expected for a range of inputs"""
        # Test mutating a graph with no alpha or beta nodes (starts with a_ or b_) is not mutated
        g_original = nx.DiGraph([("a", "b"), ("b", "c")])
        g_in = copy.deepcopy(g_original)
        g_out = util.phase_relabel(g_in)
        # phase_relabel currently mutates and returns the provided graph - i.e. they are the same object.
        assert id(g_in) == id(g_out)
        # Assert that the labels are the same
        assert g_out.nodes("label") == g_original.nodes("label")

        # Test mutating a graph with alpha and beta nodes, i.e. node labels which start with a_ and b_.
        g_original = nx.DiGraph([("a_1", "a"), ("a", "b"), ("b", "b_1")])
        g_in = copy.deepcopy(g_original)
        g_out = util.phase_relabel(g_in)
        # Assert that the labels are no longer the same
        assert g_out.nodes("label") != g_original.nodes("label")
        # Assert the labels for a_1 and b_1 are as expected
        node_labels = g_out.nodes("label")
        assert node_labels["a_1"] == "<&alpha;<SUB> 1</SUB>>"
        assert node_labels["b_1"] == "<&beta;<SUB>1</SUB>>"

        # Check an a_1 = b_1 type label.
        g_original = nx.DiGraph([("a_1 = b_1", "a")])
        g_in = copy.deepcopy(g_original)
        g_out = util.phase_relabel(g_in)
        # Assert that the labels are no longer the same
        assert g_out.nodes("label") != g_original.nodes("label")
        # Assert the labels for a_1 = b_1 is as expected
        node_labels = g_out.nodes("label")
        assert node_labels["a_1 = b_1"] == "<&alpha;<SUB>1</SUB> = &beta;<SUB>1</SUB>>"

        # Check nodes which contain a_ or b_, but are not at the start of the node name.
        # Ideally these should not be mutated, but currently are.
        g_original = nx.DiGraph([("foo_a_bar", "foo_b_bar")])
        g_in = copy.deepcopy(g_original)
        g_out = util.phase_relabel(g_in)
        node_labels = g_out.nodes("label")
        # Assert the labels are mutated (current behaviour)
        assert node_labels["foo_a_bar"] == "foo_<&alpha;<SUB> bar</SUB>>"
        assert node_labels["foo_b_bar"] == "foo_<&beta;<SUB>bar</SUB>>"
        # Ideally instead we should Assert the labels were not specified
        # assert "foo_a_bar" not in node_labels
        # assert "foo_b_bar" not in node_labels

        # Check a node which is not a polychron-generate group node, i.e. a user provided context with a_ and/or b_ in the context label.
        # This will be mutates as if it was an alpha/beta node currently, but ideally should not be
        g_original = nx.DiGraph([("a_b_c", "foo")])
        g_in = copy.deepcopy(g_original)
        g_out = util.phase_relabel(g_in)
        # Assert the labels for a_b_c has been changed, although ideally it wouldn't be. This would require a dynamic label prefix, or the method would need to be provided a list of group labels to mutate, rather than checking all nodes for matching patterns.
        node_labels = g_out.nodes("label")
        assert node_labels["a_b_c"] == "<&alpha;<SUB>b_c</SUB>>"
        # ideally this should not be mutated
        # assert "a_b_c" not in node_labels

    def test_alp_beta_node_add(self):
        """Test alp_beta_node_add behaves as expected for a range of inputs"""
        # Start with a graph
        g = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])

        # Test that adding alpha and beta nodes to a copy of the graph behaves as intended.
        g_copy = copy.deepcopy(g)
        util.alp_beta_node_add("1", g_copy)
        # the alpha and beta nodes should not be in g, but should be in g_copy
        assert not g.has_node("a_1")
        assert not g.has_node("b_1")
        assert g_copy.has_node("a_1")
        assert g_copy.has_node("b_1")
        # Assert they are diamond shaped
        assert g_copy.nodes("shape")["a_1"] == "diamond"
        assert g_copy.nodes("shape")["b_1"] == "diamond"

        # Check with another label
        g_copy = copy.deepcopy(g)
        util.alp_beta_node_add("2", g_copy)
        # the alpha and beta nodes should not be in g, but should be in g_copy
        assert not g.has_node("a_2")
        assert not g.has_node("b_2")
        assert g_copy.has_node("a_2")
        assert g_copy.has_node("b_2")
        # Assert they are diamond shaped
        assert g_copy.nodes("shape")["a_2"] == "diamond"
        assert g_copy.nodes("shape")["b_2"] == "diamond"

        # Check adding the same label again, to the same graph. This suceeds because networkx.Graph.add_node can be used to update properties for an existing node
        util.alp_beta_node_add("2", g_copy)
        # the alpha and beta nodes should not be in g, but should be in g_copy
        assert not g.has_node("a_2")
        assert not g.has_node("b_2")
        assert g_copy.has_node("a_2")
        assert g_copy.has_node("b_2")
        # Assert they are diamond shaped
        assert g_copy.nodes("shape")["a_2"] == "diamond"
        assert g_copy.nodes("shape")["b_2"] == "diamond"

    @pytest.mark.parametrize(
        ("phi_ref", "post_group", "phi_accept", "all_samps_phi", "expected"),
        [
            # 2 groups abutting one another. Made up dates (including different lengths of accept)
            (
                ["1", "2"],
                ["abutting", "end"],
                [[5000.0], [4000.0, 4000.0], [3000.0]],
                [[5000.0, 9000.0, 9000.0], [4000.0, 4000.0, 9000.0], [3000.0, 9000.0, 9000.0]],
                (
                    ["a_1", "b_1 = a_2", "b_2"],
                    {"a_1": [5000.0], "a_2 = b_1": [4000.0, 4000.0], "b_2": [3000.0]},
                    {
                        "a_1": [5000.0, 9000.0, 9000.0],
                        "a_2 = b_1": [4000.0, 4000.0, 9000.0],
                        "b_2": [3000.0, 9000.0, 9000.0],
                    },
                ),
            ),
            # 2 groups with a gap one another. Made up dates.
            (
                ["1", "2"],
                ["gap", "end"],
                [[5000.0], [4000.0], [3000.0], [2000.0]],
                [[5000.0, 9000.0], [4000.0, 9000.0], [3000.0, 9000.0], [2000.0, 9000.0]],
                (
                    ["a_1", "b_1", "a_2", "b_2"],
                    {"a_1": [5000.0], "b_1": [4000.0], "a_2": [3000.0], "b_2": [2000.0]},
                    {
                        "a_1": [5000.0, 9000.0],
                        "b_1": [4000.0, 9000.0],
                        "a_2": [3000.0, 9000.0],
                        "b_2": [2000.0, 9000.0],
                    },
                ),
            ),
            # 2 groups with an overlap one another. Made up dates.
            (
                ["1", "2"],
                ["overlap", "end"],
                [[5000.0], [4000.0], [3000.0], [2000.0]],
                [[5000.0, 9000.0], [4000.0, 9000.0], [3000.0, 9000.0], [2000.0, 9000.0]],
                (
                    ["a_1", "a_2", "b_1", "b_2"],
                    {"a_1": [5000.0], "a_2": [4000.0], "b_1": [3000.0], "b_2": [2000.0]},
                    {
                        "a_1": [5000.0, 9000.0],
                        "a_2": [4000.0, 9000.0],
                        "b_1": [3000.0, 9000.0],
                        "b_2": [2000.0, 9000.0],
                    },
                ),
            ),
            # Single group
            (
                ["1"],
                ["end"],
                [[5000.0], [4000.0]],
                [[5000.0, 9000.0], [4000.0, 9000.0]],
                (
                    ["a_1", "b_1"],
                    {"a_1": [5000.0], "b_1": [4000.0]},
                    {"a_1": [5000.0, 9000.0], "b_1": [4000.0, 9000.0]},
                ),
            ),
        ],
    )
    def test_phase_labels(
        self,
        phi_ref: list[str],
        post_group: list[Literal["abutting", "gap", "overlap", "end"]],
        phi_accept: list[list[float]],
        all_samps_phi: list[list[float]],
        expected: tuple[list[str], dict[str, list[float]], dict[str, list[float]]],
    ):
        """Test phase_labels behaves as expected for a range of inputs

        Todo:
            - Test how errors (missing keys etc) are handled.
            - Test with more than 2 groups concurrently
        """
        # call phase_labels with parametrised inputs
        result = util.phase_labels(phi_ref, post_group, phi_accept, all_samps_phi)

        # assert the output is as expected shape / types
        assert isinstance(result, tuple)
        assert len(result) == 3
        labels, accept_group_limits, all_group_limits = result
        assert isinstance(labels, list)
        assert isinstance(accept_group_limits, dict)
        assert isinstance(all_group_limits, dict)

        # Assert the output values match the parametrised expected result
        expected_labels, expected_accept, expected_all = expected
        assert labels == expected_labels
        assert accept_group_limits == expected_accept
        assert all_group_limits == expected_all

    @pytest.mark.parametrize(
        ("phi_ref", "del_phase", "phasedict", "expected"),
        [
            # No groups/phases to remove
            (["1", "2"], set([]), {("2", "1"): "abutting"}, []),
            # Invalid phase in del_phase, nothing to remove
            (["1", "2"], set(["3"]), {("2", "1"): "gap"}, []),
            # Delete the middle group of 3.
            (["1", "2", "3"], set(["2"]), {("2", "1"): "abutting", ("3", "2"): "abutting"}, [["3", "1"]]),
            # Delete the first and last group of 4, no changes (no new gap relationships)
            (
                ["1", "2", "3", "4"],
                set(["1", "4"]),
                {("2", "1"): "abutting", ("3", "2"): "gap", ("4", "3"): "abutting"},
                [],
            ),
            # Delete 2, creating a gap between 1 and 3
            (
                ["1", "2", "3", "4"],
                set(["2"]),
                {("2", "1"): "abutting", ("3", "2"): "gap", ("4", "3"): "abutting"},
                [["3", "1"]],
            ),
            # Delete 3, creating a gap between 2 and 4
            (
                ["1", "2", "3", "4"],
                set(["3"]),
                {("2", "1"): "abutting", ("3", "2"): "gap", ("4", "3"): "abutting"},
                [["4", "2"]],
            ),
            # Delete 2 and 3, creating a gap between 4 and 1. This is included in the list twice
            (
                ["1", "2", "3", "4"],
                set(["2", "3"]),
                {("2", "1"): "abutting", ("3", "2"): "gap", ("4", "3"): "abutting"},
                [["4", "1"], ["4", "1"]],
            ),
            # 5 groups, deleted 2 groups which are not connected to each other
            (
                ["1", "2", "3", "4", "5"],
                set(["2", "4"]),
                {("2", "1"): "abutting", ("3", "2"): "gap", ("4", "3"): "abutting", ("5", "4"): "abutting"},
                [["3", "1"], ["5", "3"]],
            ),
        ],
    )
    def test_del_empty_phases(
        self, phi_ref: list[str], del_phase: set[str], phasedict: dict[tuple[str, str], str], expected: list[list[str]]
    ):
        """Test del_empty_phases behaves as expected for a range of inputs

        Todo:
            - Test with (and handle) missing keys from phasedict. This should not occur in normal polychron usage
        """
        # call del_empty_phases with parametrised inputs
        result = util.del_empty_phases(phi_ref, del_phase, phasedict)
        # assert the output is as expected shape / types
        assert isinstance(result, list)
        # Assert the output values match the parametrised expected result
        assert result == expected

    @pytest.mark.skip(reason="test_group_rels_delete_empty not yet implemented")
    def test_group_rels_delete_empty(self):
        """Test group_rels_delete_empty behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_chrono_edge_add not yet implemented")
    def test_chrono_edge_add(self):
        """Test chrono_edge_add behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_chrono_edge_remov not yet implemented")
    def test_chrono_edge_remov(self):
        """Test chrono_edge_remov behaves as expected for a range of input graphs"""
        pass

    @pytest.mark.parametrize(("src", "dst", "expected"), [("a", "b", "a above b"), ("1", "2", "1 above 2")])
    def test_edge_label(self, src: str, dst: str, expected: str):
        """Test that edge_label returns the expected string for a range of inputs"""
        assert util.edge_label(src, dst) == expected

    def test_remove_invalid_attributes_networkx_lt_3_4(self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
        """Test that removing invalid attributes behaves as expected.

        This method has networkx version-specific behaviour, but we can test both sides throuhg mocking, but actual tests of the networkx call will only be valid for installed verison of networkx

        In networkx < 3.4, the pydot + networkx integration does not correctly escape node and edge attributes which are python dicationaries (i.e. they have `:` in), which are caused throuhg use of nx.contracted_nodes and nx.relabel_nodes.

        The simplest case to reproduce this, is to start with a graph

        ```mermaid
        flowchart TD
            a --> b
            a --> c
            b --> d
            c --> d
        ```

        Then combining nodes b and c into a single node b = c (i.e context equality), via contracted_nodes and relabel_nodes, ending with a graph:

        ```mermaid
        flowchart TD
            a --> b_c["b = c"]
            b_c --> d
        ```
        """
        # Prepare a digraph which will result in contraction attribues on nodes and edges
        g = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
        # Contract b and c, which adds a "contraction" attribute to the node, which is a python dictionary which would trigger the erorr in networkx < 3.4
        g = nx.contracted_nodes(g, "b", "c")
        # Also add a contraction attribute to an edge, through relableing
        g: nx.DiGraph = nx.relabel_nodes(g, {"b": "b = c"})
        # Assert that the node "b = c" exists and has a contraction attribute
        assert "b = c" in g.nodes
        assert "contraction" in g.nodes["b = c"]
        assert isinstance(g.nodes["b = c"]["contraction"], dict)
        # Assert that the edge a -> "b = c" exists and has a contraction attribute
        assert "a", "b = c" in g.edges
        assert "contraction" in g.edges["a", "b = c"]
        assert isinstance(g.edges["a", "b = c"]["contraction"], dict)

        # With this graph known to include attributes we are attempting to trigger, call a pydot method that should fail with networkx, if we have the old version.
        if packaging.version.parse(nx.__version__) < packaging.version.parse("3.4.0"):
            with pytest.raises(ValueError, match='Node names and attributes should not contain ":"'):
                write_dot(g, tmp_path / "file.gv")
        else:
            # Newer verisons should succeed without special handling.
            write_dot(g, tmp_path / "file.gv")

        # Now check that after calling the method we are trying to test, it succeeds regardless of version
        g_copy = util.remove_invalid_attributes_networkx_lt_3_4(g)
        write_dot(g_copy, tmp_path / "file.gv")

        # Now test both sides of the branch in the method being tested
        # Store the real nx_verison
        actual_nx_version = nx.__version__
        # Double check the attributes have not been removed from our input (i.e. not mutated in place)
        assert "contraction" in g.nodes["b = c"]
        assert "contraction" in g.edges["a", "b = c"]
        # monkeypatch out the networkx.__version__ attribute, returning a value ge 3.4.0
        monkeypatch.setattr(nx, "__version__", "3.4.0")
        # Call the method, and assert that the contraction attributes have not been removed.
        g_copy = util.remove_invalid_attributes_networkx_lt_3_4(g)
        assert "contraction" in g_copy.nodes["b = c"]
        assert "contraction" in g_copy.edges["a", "b = c"]

        # monkeypatch out the networkx.__version__ attribute, returning a value lt 3.4.0
        monkeypatch.setattr(nx, "__version__", "3.2.0")
        # Call the method, and assert that the contraction attributes have been removed.
        g_copy = util.remove_invalid_attributes_networkx_lt_3_4(g)
        assert "contraction" not in g_copy.nodes["b = c"]
        assert "contraction" not in g_copy.edges["a", "b = c"]

        # Restore the real nx verison, although this should be implicitly handled by the monkeypatch fixture
        monkeypatch.setattr(nx, "__version__", actual_nx_version)

    class TestMonotonicTimer:
        """Tests for the MonotonicTimer utility class."""

        def test_init(self):
            """Test construction of timers"""
            timer = util.MonotonicTimer()
            # Only sets private members, no public properties
            assert timer._MonotonicTimer__start is None
            assert timer._MonotonicTimer__stop is None

        def test_start(self):
            """Test the start method, which only really sets internal state"""
            timer = util.MonotonicTimer()
            ret = timer.start()
            assert isinstance(timer._MonotonicTimer__start, int)
            assert timer._MonotonicTimer__stop is None
            assert ret == timer

        def test_stop(self):
            """Test the stop method, with and without start having been called"""
            # Call start then stop, which should set both values
            timer = util.MonotonicTimer()
            timer.start()
            ret = timer.stop()
            assert isinstance(timer._MonotonicTimer__start, int)
            assert isinstance(timer._MonotonicTimer__stop, int)
            assert ret == timer

            # Call stop without start, which should raise a Runtime error
            timer = util.MonotonicTimer()
            with pytest.raises(RuntimeError, match="MonotonicTimer.start must be called before MonotonicTimer.stop"):
                timer.stop()

        def test_elapsed_ns(self):
            """Assert that elapsed_ns behaves as expected, raising when needed.

            Some sleeping is used to ensure that a value is provided, although precision is platform/hardware specific
            """
            # No start
            timer = util.MonotonicTimer()
            with pytest.raises(
                RuntimeError, match="MonotonicTimer.start must be called before MonotonicTimer.elapsed_ns"
            ):
                timer.elapsed_ns()
            #  No stop
            timer = util.MonotonicTimer().start()
            with pytest.raises(
                RuntimeError, match="MonotonicTimer.stop must be called before MonotonicTimer.elapsed_ns"
            ):
                timer.elapsed_ns()

            # A valid elapsed call
            timer = util.MonotonicTimer()
            timer.start()
            timer.stop()
            elapsed = timer.elapsed_ns()
            assert isinstance(elapsed, int)
            assert elapsed >= 0

            # A valid elapsed call, with some sleeping
            timer = util.MonotonicTimer()
            timer.start()
            time.sleep(0.1)
            timer.stop()
            elapsed = timer.elapsed_ns()
            assert isinstance(elapsed, int)
            assert elapsed >= 0

        def test_elapsed(self):
            """Assert that elapsed behaves as expected, raising when needed.

            Some sleeping is used to ensure that a value is provided, although precision is platform/hardware specific
            """
            # No start
            timer = util.MonotonicTimer()
            with pytest.raises(RuntimeError, match="MonotonicTimer.start must be called before MonotonicTimer.elapsed"):
                timer.elapsed()
            #  No stop
            timer = util.MonotonicTimer().start()
            with pytest.raises(RuntimeError, match="MonotonicTimer.stop must be called before MonotonicTimer.elapsed"):
                timer.elapsed()

            # A valid elapsed call
            timer = util.MonotonicTimer()
            timer.start()
            timer.stop()
            elapsed = timer.elapsed()
            assert isinstance(elapsed, float)
            assert elapsed >= 0

            # A valid elapsed call, with some sleeping
            timer = util.MonotonicTimer()
            timer.start()
            time.sleep(0.1)
            timer.stop()
            elapsed = timer.elapsed()
            assert isinstance(elapsed, float)
            assert elapsed >= 0

            # Also check that the elapsed seconds is equal to the ns version
            assert timer.elapsed() == pytest.approx(timer.elapsed_ns() / 1e9)

    @pytest.mark.parametrize(
        ("platform_name", "double", "expected"),
        [
            ("Linux", False, "<Button-3>"),
            ("Windows", False, "<Button-3>"),
            ("Darwin", False, "<Button-2>"),
            ("Linux", True, "<Double-Button-3>"),
            ("Windows", True, "<Double-Button-3>"),
            ("Darwin", True, "<Double-Button-2>"),
        ],
    )
    def test_get_right_click_binding(self, platform_name: str, double: bool, expected: str):
        """Ensure that get_right_click_binding returns the correct platform-specific value.

        This patches out platform.system to enable cross-platform testing
        """
        with patch("polychron.util.platform.system", return_value=platform_name):
            assert util.get_right_click_binding(double) == expected
