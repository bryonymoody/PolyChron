from __future__ import annotations

import copy
import pathlib
import time
from textwrap import dedent

import networkx as nx
import packaging.version
import pandas as pd
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
                '1" class="node">\n<title>a</title>\n<polygon fill="none" stroke="black" points="54,-180 0,-180 0,-144 54,-144 54,-180"/>\n<text text-anchor="middle" x="27" y="-158.3" font-family="Times,serif" font-size="14.00">a',
                [0.0, 54.0, 144.0, 180.0],
            ),
            (
                '2" class="node">\n<title>b = c</title>\n<polygon fill="none" stroke="black" points="54,-108 0,-108 0,-72 54,-72 54,-108"/>\n<text text-anchor="middle" x="27" y="-86.3" font-family="Times,serif" font-size="14.00">b = c',
                [0.0, 54.0, 72.0, 108.0],
            ),
            (
                '3" class="node">\n<title>d</title>\n<polygon fill="none" stroke="black" points="54,-36 0,-36 0,0 54,0 54,-36"/>\n<text text-anchor="middle" x="27" y="-14.3" font-family="Times,serif" font-size="14.00">d',
                [0.0, 54.0, -0.0, 36.0],
            ),
        ],
    )
    def test_polygonfunc(self, input: str, expected: list[float]):
        """Test polygonfunc behaves as expected for a range of inputs

        Todo:
            - Test invalid inputs (i.e. elipses)
        """
        # Call polygonfunc with the parametrized input,
        retval = util.polygonfunc(input)
        assert retval == pytest.approx(expected)

    @pytest.mark.parametrize(
        ("input", "expected"),
        [
            (
                '1" class="node">\n<title>ellipse</title>\n<ellipse fill="none" stroke="black" cx="33.8" cy="-187.09" rx="33.6" ry="18"/>\n<text text-anchor="middle" x="33.8" y="-183.39" font-family="Times,serif" font-size="14.00">ellipse',
                [0.19999999999999574, 67.4, 169.09, 205.09],
            ),
            (
                '2" class="node">\n<title>oval</title>\n<ellipse fill="none" stroke="black" cx="33.8" cy="-115.09" rx="27" ry="18"/>\n<text text-anchor="middle" x="33.8" y="-111.39" font-family="Times,serif" font-size="14.00">oval',
                [6.799999999999997, 60.8, 97.09, 133.09],
            ),
            (
                '3" class="node">\n<title>circle</title>\n<ellipse fill="none" stroke="black" cx="33.8" cy="-30.55" rx="30.59" ry="30.59"/>\n<text text-anchor="middle" x="33.8" y="-26.85" font-family="Times,serif" font-size="14.00">circle',
                [3.2099999999999973, 64.39, -0.03999999999999915, 61.14],
            ),
        ],
    )
    def test_ellipsefunc(self, input: str, expected: list[float]):
        """Test ellipsefunc behaves as expected for a range of inputs

        Todo:
            - Test invalid inputs (i.e. box/diamonds)
        """
        # Call ellipsefunc with the parametrized input,
        retval = util.ellipsefunc(input)
        assert retval == pytest.approx(expected)

    def test_rank_func(self):
        """Test rank_func behaves as expected for a range of inputs

        Todo:
            - Expand the range of inputs which are tested
        """
        print()
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

    def test_node_coords_fromjson(self):
        """Test node_coords_fromjson behaves as expected for a range of inputs

        Due to non-determinism within graphviz layout generation, we probably cannot rely on exact coordinates for all graphs, but ideally we should be able to for relatively simple graphs.
        The test may need ammending to account for this.

        Todo:
            - Split node_coords_fromjson into a method which takes a graph and returns the coordinates, and an internally used method which takes a string containing an svg. svg extraction can then accurately be tested, while graphviz .svg generation cannot. This also means that we should ensure .png and .svg are regenerated on polychron launch, in case graphviz has changed.
            - rectangular bounding boxes are always used for click detection, even for diamonds and elipses. This may be problematic if graphviz does not ensure that the rectangular bounding box of a diamond/kite is free from other nodes.
            - Consider returning a dict instead of a dataframe.
        """

        # Get the node coordinates and scale for a nx.DiGraph
        g = nx.DiGraph()
        for node in ["a", "b", "c", "d"]:
            g.add_node(node, shape="box")
        for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]:
            g.add_edge(u, v)
        df, scale = util.node_coords_fromjson(g)
        # Assert the types and shape of returned data is as it should be
        assert isinstance(df, pd.DataFrame)
        assert "x_lower" in df.columns
        assert "x_upper" in df.columns
        assert "y_lower" in df.columns
        assert "y_upper" in df.columns
        assert len(df) == 4
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for node in g.nodes():
            assert node in df.index
            assert isinstance(df["x_lower"][node], float)
            assert isinstance(df["x_upper"][node], float)
            assert isinstance(df["y_lower"][node], float)
            assert isinstance(df["y_upper"][node], float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

        # Get the node coordinates and scale for a nx.DiGraph including contraction attribtues, to ensure networkx < 3.4 compatibility (due to use of nx_pydot internally)
        g = nx.DiGraph()
        for node in ["a", "b", "c", "d"]:
            g.add_node(node, shape="box")
        for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]:
            g.add_edge(u, v)
        g = nx.contracted_nodes(g, "b", "c")
        g = nx.relabel_nodes(g, {"b": "b = c"})
        df, scale = util.node_coords_fromjson(g)
        assert isinstance(df, pd.DataFrame)
        assert "x_lower" in df.columns
        assert "x_upper" in df.columns
        assert "y_lower" in df.columns
        assert "y_upper" in df.columns
        assert len(df) == 3
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for node in g.nodes():
            assert node in df.index
            assert isinstance(df["x_lower"][node], float)
            assert isinstance(df["x_upper"][node], float)
            assert isinstance(df["y_lower"][node], float)
            assert isinstance(df["y_upper"][node], float)
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
        df, scale = util.node_coords_fromjson(pydot_g)
        assert isinstance(df, pd.DataFrame)
        assert "x_lower" in df.columns
        assert "x_upper" in df.columns
        assert "y_lower" in df.columns
        assert "y_upper" in df.columns
        assert len(df) == 3
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for node in pydot_g.get_nodes():
            assert node.get_name() in df.index
            assert isinstance(df["x_lower"][node.get_name()], float)
            assert isinstance(df["x_upper"][node.get_name()], float)
            assert isinstance(df["y_lower"][node.get_name()], float)
            assert isinstance(df["y_upper"][node.get_name()], float)
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

        df, scale = util.node_coords_fromjson(g)
        assert isinstance(df, pd.DataFrame)
        assert "x_lower" in df.columns
        assert "x_upper" in df.columns
        assert "y_lower" in df.columns
        assert "y_upper" in df.columns
        assert len(df) == 6
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for node in g.nodes():
            assert node in df.index
            assert isinstance(df["x_lower"][node], float)
            assert isinstance(df["x_upper"][node], float)
            assert isinstance(df["y_lower"][node], float)
            assert isinstance(df["y_upper"][node], float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

        # Test with a graph that includes elipses/ovals/circles
        # polychron currently (0.2.0) only explicitly sets box or diamond, so this is only for .dot inputs which explciitly set custom shapes?
        # Manually build a graph "ellipse" -> "oval" -> "circle"
        g = nx.DiGraph()
        g.add_node("ellipse", shape="ellipse")
        g.add_node("oval", shape="oval")
        g.add_node("circle", shape="circle")
        g.add_edge("ellipse", "oval")
        g.add_edge("oval", "circle")
        df, scale = util.node_coords_fromjson(g)
        # Assert the returned values are the correct types and shape
        assert isinstance(df, pd.DataFrame)
        assert "x_lower" in df.columns
        assert "x_upper" in df.columns
        assert "y_lower" in df.columns
        assert "y_upper" in df.columns
        assert len(df) == 3
        assert isinstance(scale, list)
        assert len(scale) == 2
        # Assert each node is included
        for node in g.nodes():
            assert node in df.index
        # Assert the types of values are correct, as we cannot test the values due to non-deterministic graphviz svg generation
        for node in g.nodes():
            assert node in df.index
            assert isinstance(df["x_lower"][node], float)
            assert isinstance(df["x_upper"][node], float)
            assert isinstance(df["y_lower"][node], float)
            assert isinstance(df["y_upper"][node], float)
        # Assert the scale is the correct shape and types. We cannot test exact values here due to graphviz non-determinism
        assert isinstance(scale, list)
        assert len(scale) == 2
        for value in scale:
            assert isinstance(value, float)

    @pytest.mark.skip(reason="test_phase_info_func not yet implemented")
    def test_phase_info_func(self):
        """Test phase_info_func behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_edge_of_phase not yet implemented")
    def test_edge_of_phase(self):
        """Test edge_of_phase behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_node_del_fixed not yet implemented")
    def test_node_del_fixed(self):
        """Test node_del_fixed behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_all_node_info not yet implemented")
    def test_all_node_info(self):
        """Test all_node_info behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_phase_length_finder not yet implemented")
    def test_phase_length_finder(self):
        """Test phase_length_finder behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_imagefunc not yet implemented")
    def test_imagefunc(self):
        """Test imagefunc behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_phase_relabel not yet implemented")
    def test_phase_relabel(self):
        """Test phase_relabel behaves as expected for a range of inputs"""
        pass

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

    @pytest.mark.skip(reason="test_phase_labels not yet implemented")
    def test_phase_labels(self):
        """Test phase_labels behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_del_empty_phases not yet implemented")
    def test_del_empty_phases(self):
        """Test del_empty_phases behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_group_rels_delete_empty not yet implemented")
    def test_group_rels_delete_empty(self):
        """Test group_rels_delete_empty behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_chrono_edge_add not yet implemented")
    def test_chrono_edge_add(self):
        pass

    @pytest.mark.skip(reason="test_chrono_edge_remov not yet implemented")
    def test_chrono_edge_remov(self):
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
