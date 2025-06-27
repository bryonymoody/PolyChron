from __future__ import annotations

import pathlib
import time

import networkx as nx
import packaging.version
import pytest
from networkx.drawing.nx_pydot import write_dot
from PIL import Image, ImageDraw

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

    @pytest.mark.skip(reason="test_polygonfunc not yet implemented")
    def test_polygonfunc(self):
        """Test polygonfunc behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_ellipsefunc not yet implemented")
    def test_ellipsefunc(self):
        """Test ellipsefunc behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_rank_func not yet implemented")
    def test_rank_func(self):
        """Test rank_func behaves as expected for a range of inputs"""
        pass

    @pytest.mark.skip(reason="test_node_coords_fromjson not yet implemented")
    def test_node_coords_fromjson(self):
        """Test node_coords_fromjson behaves as expected for a range of inputs"""
        pass

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

    @pytest.mark.skip(reason="test_alp_beta_node_add not yet implemented")
    def test_alp_beta_node_add(self):
        """Test alp_beta_node_add behaves as expected for a range of inputs"""
        pass

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
