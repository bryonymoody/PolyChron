from __future__ import annotations

import json
import os
import pathlib
from typing import Type
from unittest.mock import patch

import networkx as nx
import pandas as pd
import pytest
from PIL import Image

from polychron.models.MCMCData import MCMCData
from polychron.models.Model import Model


class TestModel:
    """Unit Tests for the `models.Model` class which represents a polychron Model"""

    def test_init(self, tmp_path: pathlib.Path):
        """Test `__init__` behaviour for the dataclass including default and explicit value setting/getting

        Todo:
            - Test invalid model names and paths (i.e. ".", " ")
            - Test providing optional values to the constructor.
        """
        # Construct an instance, only providing compulsory ctor arguments
        m = Model("foo", tmp_path / "foo")
        assert m.name == "foo"
        assert m.path == tmp_path / "foo"
        assert m.stratigraphic_graphviz_file is None
        assert m.stratigraphic_df is None
        assert m.stratigraphic_dag is None
        assert m.stratigraphic_image is None
        assert m.radiocarbon_df is None
        assert m.context_no_unordered is None
        assert m.group_df is None
        assert m.group_relationship_df is None
        assert m.group_relationships is None
        assert m.context_equality_df is None
        assert not m.load_check
        assert m.chronological_dag is None
        assert m.chronological_image is None
        assert m.mcmc_check is False
        assert m.deleted_nodes == []
        assert m.deleted_edges == []
        assert m.resid_or_intru_dag is None
        assert m.resid_or_intru_image is None
        assert m.intrusive_contexts == []
        assert m.residual_contexts == []
        assert m.intrusive_context_types == {}
        assert m.residual_context_types == {}
        assert not m.grouped_rendering
        assert m.context_types == []
        assert m.prev_group == []
        assert m.post_group == []
        assert m.phi_ref == []
        assert m.removed_nodes_tracker == []
        assert m.mcmc_data == MCMCData()
        assert m.node_coords_and_scale is None
        # Check private members are initialised correctly, although not part of the public interface
        assert m._Model__calibration is None

    def test_get_working_directory(self, tmp_path: pathlib.Path):
        """Test the get_working_directory method returns the expected path

        Todo:
            - Should workdir be a child of python_only?
        """
        m = Model("foo", tmp_path / "foo")
        assert m.get_working_directory() == tmp_path / "foo" / "workdir"

    def test_get_chronological_graph_directory(self, tmp_path: pathlib.Path):
        """Test the get_chronological_graph_directory method returns the expected path"""
        m = Model("foo", tmp_path / "foo")
        assert m.get_chronological_graph_directory() == tmp_path / "foo" / "chronological_graph"

    def test_get_stratigraphic_graph_directory(self, tmp_path: pathlib.Path):
        """Test the get_stratigraphic_graph_directory method returns the expected path"""
        m = Model("foo", tmp_path / "foo")
        assert m.get_stratigraphic_graph_directory() == tmp_path / "foo" / "stratigraphic_graph"

    def test_get_mcmc_results_directory(self, tmp_path: pathlib.Path):
        """Test the get_mcmc_results_directory method returns the expected path"""
        m = Model("foo", tmp_path / "foo")
        assert m.get_mcmc_results_directory() == tmp_path / "foo" / "mcmc_results"

    def test_get_python_only_directory(self, tmp_path: pathlib.Path):
        """Test the get_python_only_directory method returns the expected path"""
        m = Model("foo", tmp_path / "foo")
        assert m.get_python_only_directory() == tmp_path / "foo" / "python_only"

    def test_to_json(self, tmp_path: pathlib.Path):
        """Test the to_json method behaves as expected for a range of Models

        Todo:
            - Expand the tests to check the exported data is correct, rather than just present.
        """
        m = Model("foo", tmp_path / "foo")
        json_str = m.to_json()
        # Assert that a non empty string was returned
        assert len(json_str) > 0
        # Assert that it was a single line, as pretty=False by default
        assert len(json_str.splitlines()) == 1
        # Parse the json string, which should ensure it was valid json
        json_obj = json.loads(json_str)
        # The json should have been mapped back to a dictionary
        assert isinstance(json_obj, dict)
        # The dict should contain a polychron_version element, which is a string and must be 3 versioned segments
        assert "polychron_version" in json_obj
        assert isinstance(json_obj["polychron_version"], str)
        assert len(json_obj["polychron_version"].split(".")) >= 3
        # The dict must also contain a "model" element, which is another dictionary
        assert "model" in json_obj
        assert isinstance(json_obj["model"], dict)
        assert len(json_obj["model"]) > 0
        # This model only has non-default name and path
        assert "name" in json_obj["model"]
        assert json_obj["model"]["name"] == "foo"
        # but the path should not be in the json
        assert "path" not in json_obj["model"]

        # if explicitly called with pretty=False, the json string should be a non empty single line
        json_str = m.to_json(pretty=False)
        assert len(json_str) > 0
        assert len(json_str.splitlines()) == 1

        # if explicitly called with pretty=True, the json string should be a non empty string with more than 1 line (actually >= 4, but should be much higher)
        json_str = m.to_json(pretty=True)
        assert len(json_str) > 0
        assert len(json_str.splitlines()) >= 4

    @pytest.mark.skip(reason="test_save not implemented")
    def test_save(self, tmp_path: pathlib.Path):
        """Test the save method behaves as expected for a range of Models"""
        m = Model("foo", tmp_path / "foo")
        m.save()

    def test_load_from_disk(self, test_data_path: pathlib.Path, capsys: pytest.CaptureFixture):
        """Test the load_from_disk method behaves as expected for a range of json files

        Todo:
            - Add test files with more-complete json files
            - Add a test which includes MCMCData json"""
        test_json_dir = test_data_path / "json"
        # Test that a minimal valid multi-line polychron_model.json is successfully loaded
        m = Model.load_from_disk(test_json_dir / "minimal")
        assert m.name == "foo"
        assert m.path == test_json_dir / "minimal"

        # Test that a minimal valid single-line polychron_model.json is successfully loaded
        m = Model.load_from_disk(test_json_dir / "minimal-single-line")
        assert m.name == "foo"
        assert m.path == test_json_dir / "minimal-single-line"

        # If the directory does not contain a polychron_model.json, return a (almost) default Model
        m = Model.load_from_disk(test_json_dir / "empty")
        assert m.name == "empty"

        # If polychron_model.json is a json object, with required keys but the 'model' does not contain a 'name', the directory name should be used
        m = Model.load_from_disk(test_json_dir / "empty-model")
        assert m.name == "empty-model"

        # if an unknown key is present, in the main json dict object, it should proceed silently
        capsys.readouterr()
        m = Model.load_from_disk(test_json_dir / "unknown-key")
        captured = capsys.readouterr()
        assert len(captured.err) == 0

        # If the model object has unknown keys, a warning should be emitted to stderr
        capsys.readouterr()
        m = Model.load_from_disk(test_json_dir / "unknown-model-member")
        captured = capsys.readouterr()
        assert len(captured.err) > 0

        # --- check a range of model directories which are expected to fail in some way.

        # If polychron_model.json is an empty file, an invalid json file exception should be raised
        with pytest.raises(RuntimeError, match="Invalid JSON file"):
            m = Model.load_from_disk(test_json_dir / "empty-file")

        # If polychron_model.json is an invalid JSON file an invalid json file exception should be raised
        with pytest.raises(RuntimeError, match="Invalid JSON file"):
            m = Model.load_from_disk(test_json_dir / "invalid-json")

        # If polychron_model.json contain an empty dictionary, a missing key exception should be raised
        with pytest.raises(RuntimeError, match="Required key 'polychron_version' missing from"):
            Model.load_from_disk(test_json_dir / "empty-dict")

        # If polychron_model.json is a json object but does not contain the 'polychron_version', a missing key exception should be raised
        with pytest.raises(RuntimeError, match="Required key 'polychron_version' missing from"):
            Model.load_from_disk(test_json_dir / "no-version")

        # If polychron_model.json is a json object but does not contain the 'model', a missing key exception should be raised
        with pytest.raises(RuntimeError, match="Required key 'model' missing from"):
            Model.load_from_disk(test_json_dir / "no-model")

        # If the polychron_version is not a string, an error should be raised
        with pytest.raises(RuntimeError, match="'polychron_version' must be a string"):
            m = Model.load_from_disk(test_json_dir / "invalid-version")

        # If the polychron_version is not a valid version string, an error should be raised
        with pytest.raises(RuntimeError, match="is not a valid version number"):
            m = Model.load_from_disk(test_json_dir / "invalid-version-string")

    def test_create_dirs(self, tmp_path: pathlib.Path):
        """Test the create_dirs method behaves as expected for a range of Models"""
        model_path = tmp_path / "foo"
        m = Model("foo", model_path)
        # Assert that the model dir does not exist right now
        assert not model_path.exists()
        # Call the create directories method
        m.create_dirs()
        # Assert the expected paths now exist
        assert model_path.exists()
        assert model_path.is_dir()
        assert m.get_working_directory().is_dir()
        assert m.get_stratigraphic_graph_directory().is_dir()
        assert m.get_chronological_graph_directory().is_dir()
        assert m.get_mcmc_results_directory().is_dir()
        assert m.get_python_only_directory().is_dir()

        # Assert the current dir has been updated.
        assert pathlib.Path(os.getcwd()) == model_path

        # Assert that calling it again does not error
        m.create_dirs()

        # Check that a model path with a missing parent directory would behave
        model_path = tmp_path / "missing" / "parent" / "dirs" / "foo"
        m = Model("foo", model_path)
        assert not model_path.exists()
        m.create_dirs()
        assert model_path.exists()

        # Tests expected errors would be raised in case of disk errors through mocking
        model_path = tmp_path / "mock_mkdir"
        m = Model("mock_mkdir", model_path)
        with patch("pathlib.Path.mkdir", side_effect=OSError("Mock OSError")):
            with pytest.raises(OSError, match="Mock OSError"):
                m.create_dirs()

        model_path = tmp_path / "mock_chdir"
        m = Model("mock_chdir", model_path)
        with patch("os.chdir", side_effect=OSError("Mock OSError")):
            with pytest.raises(OSError, match="Mock OSError"):
                m.create_dirs()

    def test_save_deleted_contexts(self, tmp_path: pathlib.Path):
        """Test save_deleted_contexts behaves as expected for a range of models, and that it may raise on attempts to write the csv if disk state is invalid"""
        # Test saving a model with no deleted nodes creates a csv with no data rows
        m = Model("foo", tmp_path / "foo")
        expected_csv_path = m.get_working_directory() / "deleted_contexts_meta"
        assert not expected_csv_path.exists()
        m.save_deleted_contexts()
        assert expected_csv_path.is_file()
        df = pd.read_csv(expected_csv_path, dtype=str, keep_default_na=False)
        assert list(df.columns) == ["context", "Reason for deleting"]
        assert len(df) == 0

        # With some deleted contexts, expect the correct data to be included. Includes an edge case with an empry reason.
        deletions = [("foo", "test"), ("bar", "")]
        m.deleted_nodes = deletions
        m.save_deleted_contexts()
        assert expected_csv_path.is_file()
        df = pd.read_csv(expected_csv_path, dtype=str, keep_default_na=False)
        assert list(df.columns) == ["context", "Reason for deleting"]
        assert len(df) == 2
        for idx, (ctx, reason) in enumerate(deletions):
            assert df["context"].iloc[idx] == ctx
            assert df["Reason for deleting"].iloc[idx] == reason

        # Test that reasons containing new line characters are handled by pandas in a way that allows them to be read back in (by quoting the value but including true newline characters).
        deletions = [("foo", "test\nwith\nmultiple\nlines")]
        m.deleted_nodes = deletions
        m.save_deleted_contexts()
        assert expected_csv_path.is_file()
        df = pd.read_csv(expected_csv_path, dtype=str, keep_default_na=False)
        assert list(df.columns) == ["context", "Reason for deleting"]
        assert len(df) == 1
        for idx, (ctx, reason) in enumerate(deletions):
            assert df["context"].iloc[idx] == ctx
            assert df["Reason for deleting"].iloc[idx] == reason

        # Mock an OSError on file opening, which should be propagated up from pandas
        with patch("builtins.open", autospec=True, spec_set=True) as mock_open:
            mock_open.side_effect = OSError(28, "No space left on device")
            with pytest.raises(OSError, match="No space left on device"):
                m.save_deleted_contexts()

    def test_set_stratigraphic_graphviz_file(self, tmp_path: pathlib.Path):
        """Test set_stratigraphic_graphviz_file behaves as intended with different inputs"""
        m = Model("foo", tmp_path / "foo")
        assert m.stratigraphic_graphviz_file is None

        # test with a pathlib object
        m.set_stratigraphic_graphviz_file(tmp_path / "input.gv")
        assert m.stratigraphic_graphviz_file == tmp_path / "input.gv"

        # Test with a string, which should become a pathlib.Path
        m.set_stratigraphic_graphviz_file(str(tmp_path / "input.dot"))
        assert m.stratigraphic_graphviz_file == tmp_path / "input.dot"

    @pytest.mark.parametrize(
        ("data_or_path", "expected_nodes", "expected_edges"),
        [
            # `data/demo/1-strat.csv`` from the data dirctory
            (
                "demo/1-strat.csv",
                ["a", "b", "c", "d", "e", "f", "g"],
                [("a", "b"), ("b", "c"), ("b", "d"), ("b", "e"), ("d", "f"), ("e", "g")],
            ),
            # data/strat-csv/unconnected-context.csv which includes an unconnected context c, so 3 nodes, 1 edge expected
            (
                "strat-csv/unconnected.csv",
                ["a", "b", "c"],
                [("a", "b")],
            ),
            # A custom df which includes an unconnected context c, so 3 nodes, 1 edge expected. This does not currently pass as an emptry string is included as a context
            # (
            #     {"above": ["a", "c"], "below": ["b", ""]},
            #     ["a", "b", "c"],
            #     [("a", "b")],
            # ),
            # A dataframe with expected columns, but no rows of data
            (
                {"above": [], "below": []},
                [],
                [],
            ),
            # An empty dataframe. Currently fails as atleast 2 cols required.
            # (
            #     {},
            #     [],
            #     [],
            # ),
        ],
    )
    def test_set_stratigraphic_df(
        self,
        data_or_path: dict[str, list] | str,
        expected_nodes: list[str],
        expected_edges: list[tuple[str, str]],
        tmp_path: pathlib.Path,
        test_data_path: pathlib.Path,
    ):
        """Test set_stratigraphic_df behaves as expected.

        Todo:
            - Expand the number of input files which are tested, to cover a wider range of edge cases (empty dataframe, invalid context labels, duplicated edges, bi-directional edges, self-edges, alternate column titles, no column titles, reveresd column titles, only one columns / no above below, extra columns)"""

        # Use a dataframe read from disk in the test datasets, which is parsed the same as in ModelPresenter.open_strat_csv_file.
        if isinstance(data_or_path, str):
            input_df = pd.read_csv(test_data_path / data_or_path, dtype=str)
        else:
            input_df = pd.DataFrame(data_or_path, dtype=str)

        # Construct the model instance
        m = Model("foo", tmp_path / "foo")

        # Call the set_stratigraphic_df method
        m.set_stratigraphic_df(input_df)

        # Assert that the stored df is a copy of the provided df
        assert id(m.stratigraphic_df) != id(input_df)
        pd.testing.assert_frame_equal(m.stratigraphic_df, input_df)

        # Assert that a stratigraphic graph has been created, with the expected nodes and edges.
        assert m.stratigraphic_dag is not None
        assert isinstance(m.stratigraphic_dag, nx.DiGraph)
        assert m.stratigraphic_dag.number_of_nodes() == len(expected_nodes)

        # Assert that each expected context exists and is box shaped width an empty determiniation and group
        for node, attribs in m.stratigraphic_dag.nodes(True):
            assert node in expected_nodes
            assert attribs["shape"] == "box"
            assert attribs["Determination"] == [None, None]
            assert attribs["Group"] is None

        # Assert the correct number of edges and correct edges (number of unique rows in the input dataframe with non empty columns 0 and 1)
        assert m.stratigraphic_dag.number_of_edges() == len(expected_edges)
        for u, v, attribs in m.stratigraphic_dag.edges(data=True):
            assert (u, v) in expected_edges
            assert attribs["arrowhead"] == "none"

    @pytest.mark.parametrize(
        ("data_or_path", "num_with_attrib", "exception_t"),
        [
            # Empty dataframe, triggers an exception (missing columns)
            ({}, 0, KeyError),
            # Valid dataframe, with changes
            ("rcd-csv/simple.csv", 4, None),
            # Dataframe with partial information
            ({"context": ["a", "b"], "date": [3400, 3300], "error": [80, 75]}, 2, None),
            # Dataframe with unknown context
            pytest.param(
                {
                    "context": ["a", "b", "c", "d", "e"],
                    "date": [3400, 3300, 3250, 3225, 3333],
                    "error": [80, 75, 80, 75, 50],
                },
                4,
                None,
                marks=pytest.mark.xfail(reason="see https://github.com/bryonymoody/PolyChron/issues/211"),
            ),
        ],
    )
    def test_set_radiocarbon_df(
        self,
        data_or_path: dict[str, list] | str,
        num_with_attrib: int,
        exception_t: Type[Exception] | None,
        tmp_path: pathlib.Path,
        test_data_path: pathlib.Path,
    ):
        """Test set_radiocarbon_df mutates Model instances as expected.

        This is also indirectly covered by TestModelPresenter.test_open_scientific_dating_file

        Todo:
            - Expand the range of inputs covered by this test, including rows which are for contexts not in the strat_df, which should silently pass.
        """
        # Construct the model instance
        m = Model("foo", tmp_path / "foo")

        # Add a simple stratigraphic graph to the model
        strat_df = pd.read_csv(test_data_path / "strat-csv" / "simple.csv", dtype=str)
        m.set_stratigraphic_df(strat_df)

        # Build the parametrised dataframe
        if isinstance(data_or_path, str):
            input_df = pd.read_csv(test_data_path / data_or_path, dtype=str)
        else:
            input_df = pd.DataFrame(data_or_path, dtype=str)

        # call set_radiocarbon_df potentially expecting an exception
        if exception_t is None:
            m.set_radiocarbon_df(input_df)
            # Check how many nodes have a determination attribute set
            determinations = [
                det
                for _, det in m.stratigraphic_dag.nodes("Determination")
                if det[0] is not None and det[1] is not None
            ]
            assert len(determinations) == num_with_attrib
        else:
            with pytest.raises(exception_t, match=None):
                m.set_radiocarbon_df(input_df)

    @pytest.mark.parametrize(
        ("data_or_path", "num_with_attrib", "exception_t"),
        [
            # Empty dataframe, triggers an exception (missing columns)
            ({}, 0, KeyError),
            # Valid dataframe, with changes
            ("context-grouping-csv/simple.csv", 4, None),
            # Dataframe with partial information
            ({"context": ["a", "b"], "Group": [1, 2]}, 2, None),
            # Dataframe with unknown context
            pytest.param(
                {
                    "context": ["a", "b", "c", "d", "e"],
                    "Group": [1, 2, 1, 2, 1],
                },
                4,
                None,
                marks=pytest.mark.xfail(reason="see https://github.com/bryonymoody/PolyChron/issues/211"),
            ),
        ],
    )
    def test_set_group_df(
        self,
        data_or_path: dict[str, list] | str,
        num_with_attrib: int,
        exception_t: Type[Exception] | None,
        tmp_path: pathlib.Path,
        test_data_path: pathlib.Path,
    ):
        """Test set_group_df mutates Model instances as expected.

        This is also indirectly covered by TestModelPresenter.test_open_context_grouping_file

        Todo:
            - Expand the range of inputs covered by this test, including group dataframes which include unknown contexts
        """
        # Construct the model instance
        m = Model("foo", tmp_path / "foo")

        # Add a simple stratigraphic graph to the model
        strat_df = pd.read_csv(test_data_path / "strat-csv" / "simple.csv", dtype=str)
        m.set_stratigraphic_df(strat_df)

        # Build the parametrised dataframe
        if isinstance(data_or_path, str):
            input_df = pd.read_csv(test_data_path / data_or_path, dtype=str)
        else:
            input_df = pd.DataFrame(data_or_path, dtype=str)

        # call set_group_df potentially expecting an exception
        if exception_t is None:
            m.set_group_df(input_df)
            # Check how many nodes have a determination attribute set
            groups = [g for _, g in m.stratigraphic_dag.nodes("Group") if g is not None]
            assert len(groups) == num_with_attrib
        else:
            with pytest.raises(exception_t, match=None):
                m.set_group_df(input_df)

    @pytest.mark.parametrize(
        ("data_or_path", "input_relationships", "exception_t"),
        [
            # Empty dataframe, this silently passes
            ({}, [], None),
            # Valid dataframe, with changes
            ("group-relationships-csv/simple.csv", [("1", "2"), ("2", "3")], None),
            # Dataframe with partial information
            ({"above": ["1"], "below": ["2"]}, [("1", "2")], None),
            # Dataframe with unknown group
            (
                {
                    "above": ["1", "2", "3"],
                    "below": ["2", "3", "4"],
                },
                [("1", "2"), ("2", "3"), ("3", "4")],
                None,
            ),
        ],
    )
    def test_set_group_relationship_df(
        self,
        data_or_path: dict[str, list] | str,
        input_relationships: list[tuple[str, str]],
        exception_t: Type[Exception] | None,
        tmp_path: pathlib.Path,
        test_data_path: pathlib.Path,
    ):
        """Test set_group_relationship_df behaves as expected for a range of inputs.

        This is also indirectly covered by TestModelPresenter.test_open_group_relationship_file

        Todo:
            - Expand the range of inputs covered by this test
            - Ensure the provided dataframe has required columns
            - Ensure the provided list of group relationships matches the values in the csv
        """
        # Construct the model instance
        m = Model("foo", tmp_path / "foo")

        # Add a simple stratigraphic graph to the model
        strat_df = pd.read_csv(test_data_path / "strat-csv" / "simple.csv", dtype=str)
        m.set_stratigraphic_df(strat_df)

        # Build the parametrised dataframe
        if isinstance(data_or_path, str):
            input_df = pd.read_csv(test_data_path / data_or_path, dtype=str)
        else:
            input_df = pd.DataFrame(data_or_path, dtype=str)

        input_relationships = []

        # call set_group_relationship_df potentially expecting an exception
        if exception_t is None:
            m.set_group_relationship_df(input_df, input_relationships)
            # Assert the stored dataframe matches the provided frame
            pd.testing.assert_frame_equal(m.group_relationship_df, input_df)
            # Assert that the stored list is as expected
            assert m.group_relationships == input_relationships
        else:
            with pytest.raises(exception_t, match=None):
                m.set_group_relationship_df(input_df, input_relationships)

    @pytest.mark.parametrize(
        ("data_or_path", "expect_num_nodes", "exception_t"),
        [
            # Empty dataframe, this currently fails with an IndexError.
            ({}, 0, IndexError),
            # Valid dataframe, with changes
            ("context-equality-csv/simple.csv", 3, None),
            # Dataframe with the same pair in both directions. This currently errors
            ("context-equality-csv/reversed.csv", 3, KeyError),
            # Multiple replacements, using the orignal context name. Currently an error, but ideally should work
            pytest.param(
                "context-equality-csv/multiple-combinations-original-name.csv",
                2,
                None,
                marks=pytest.mark.xfail(reason="See https://github.com/bryonymoody/PolyChron/issues/118"),
            ),
            # Multiple replacements, using the new name
            ("context-equality-csv/multiple-combinations-combined-name.csv", 2, None),
        ],
    )
    def test_set_context_equality_df(
        self,
        data_or_path: dict[str, list] | str,
        expect_num_nodes: int,
        exception_t: Type[Exception] | None,
        tmp_path: pathlib.Path,
        test_data_path: pathlib.Path,
    ):
        """Test set_context_equality_df behaves as expected for a range of inputs


        This has some coverage via `TestModelPresenter.test_open_context_equalities_file`

        Todo:
            - Expand the range of inputs this is tested over.
        """
        # Construct the model instance
        m = Model("foo", tmp_path / "foo")

        # Add a simple stratigraphic graph to the model
        strat_df = pd.read_csv(test_data_path / "strat-csv" / "simple.csv", dtype=str)
        m.set_stratigraphic_df(strat_df)

        # Build the parametrised dataframe
        if isinstance(data_or_path, str):
            input_df = pd.read_csv(test_data_path / data_or_path, dtype=str)
        else:
            input_df = pd.DataFrame(data_or_path, dtype=str)

        # call set_context_equality_df potentially expecting an exception
        if exception_t is None:
            m.set_context_equality_df(input_df)
            # Ensure the stored dataframe matches
            pd.testing.assert_frame_equal(m.context_equality_df, input_df)
            # Ensure the number of nodes matches the new expectations
            assert m.stratigraphic_dag.number_of_nodes() == expect_num_nodes

        else:
            with pytest.raises(exception_t, match=None):
                m.set_context_equality_df(input_df)

    def test_render_strat_graph(self, tmp_path: pathlib.Path):
        """Test render_strat_graph calls __render_strat_graph_phase or __render_strat_graph, using mocking/patching to just ensure the correct branch is taken."""
        # Create a model
        m = Model("foo", tmp_path / "foo")
        # The model is not in grouped/phased rendering mode, so render_strat_graph should have been called
        assert not m.grouped_rendering
        with (
            patch("polychron.models.Model.Model._Model__render_strat_graph_phase") as mock_render_phase,
            patch("polychron.models.Model.Model._Model__render_strat_graph") as mock_render,
        ):
            m.render_strat_graph()
            mock_render.assert_called_once()
            mock_render_phase.assert_not_called()

        # Switch to grouped/phased rendering, and the phased version should be called
        m.grouped_rendering = True
        assert m.grouped_rendering
        with (
            patch("polychron.models.Model.Model._Model__render_strat_graph_phase") as mock_render_phase,
            patch("polychron.models.Model.Model._Model__render_strat_graph") as mock_render,
        ):
            m.render_strat_graph()
            mock_render.assert_not_called()
            mock_render_phase.assert_called_once()

    def test_render_resid_or_intru_dag(self, tmp_path: pathlib.Path):
        """Test test_render_resid_or_intru_dag calls __render_resid_or_intru_dag_phase or __render_resid_or_intru_dag, using mocking/patching to just ensure the correct branch is taken."""
        # Create a model
        m = Model("foo", tmp_path / "foo")
        # The model is not in grouped/phased rendering mode, so render_strat_graph should have been called
        assert not m.grouped_rendering
        with (
            patch("polychron.models.Model.Model._Model__render_resid_or_intru_dag_phase") as mock_render_phase,
            patch("polychron.models.Model.Model._Model__render_resid_or_intru_dag") as mock_render,
        ):
            m.render_resid_or_intru_dag()
            mock_render.assert_called_once()
            mock_render_phase.assert_not_called()

        # Switch to grouped/phased rendering, and the phased version should be called
        m.grouped_rendering = True
        assert m.grouped_rendering
        with (
            patch("polychron.models.Model.Model._Model__render_resid_or_intru_dag_phase") as mock_render_phase,
            patch("polychron.models.Model.Model._Model__render_resid_or_intru_dag") as mock_render,
        ):
            m.render_resid_or_intru_dag()
            mock_render.assert_not_called()
            mock_render_phase.assert_called_once()

    @pytest.mark.skip("test___render_strat_graph not implemented")
    def test___render_strat_graph(self, tmp_path: pathlib.Path):
        """Test __render_strat_graph behaves as expected for a range of inputs"""
        # m = Model("foo", tmp_path / "foo")
        pass

    @pytest.mark.skip("test___render_strat_graph_phase not implemented")
    def test___render_strat_graph_phase(self, tmp_path: pathlib.Path):
        """Test __render_strat_graph_phase behaves as expected for a range of inputs"""
        # m = Model("foo", tmp_path / "foo")
        pass

    @pytest.mark.skip("test___render_resid_or_intru_dag not implemented")
    def test___render_resid_or_intru_dag(self, tmp_path: pathlib.Path):
        """Test __render_resid_or_intru_dag behaves as expected for a range of inputs"""
        # m = Model("foo", tmp_path / "foo")
        pass

    @pytest.mark.skip("test___render_resid_or_intru_dag_phase not implemented")
    def test___render_resid_or_intru_dag_phase(self, tmp_path: pathlib.Path):
        """Test __render_resid_or_intru_dag_phase behaves as expected for a range of inputs"""
        # m = Mod
        # passel("foo", tmp_path / "foo")

    @pytest.mark.skip("test_render_chrono_graph not implemented")
    def test_render_chrono_graph(self, tmp_path: pathlib.Path):
        """Test render_chrono_graph behaves as expected for a range of inputs"""
        # m = Model("foo", tmp_path / "foo")
        pass

    def test_reopen_stratigraphic_image(self, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture):
        """Test that reopening the stratigraphic image correctly mutates Model state, without the file existing, with a valid image file at the correct locaiton, and an invalid file (i.e. corrupted)"""
        m = Model("foo", tmp_path / "foo")
        expected_png_path = m.get_working_directory() / "testdag.png"
        assert m.stratigraphic_image is None

        # When the file does not exist in the working directory, the instance value should not be mutated
        assert not expected_png_path.is_file()
        m.reopen_stratigraphic_image()
        assert m.stratigraphic_image is None

        # Create an image at the expected location
        m.create_dirs()
        img = Image.new("RGB", (10, 10), (255, 0, 0))
        img.save(expected_png_path)
        # Test that if a valid png exists at the expected location, an Image instance is stored
        assert expected_png_path.is_file()
        m.reopen_stratigraphic_image()
        assert isinstance(m.stratigraphic_image, Image.Image)
        assert m.stratigraphic_image.size == img.size
        assert m.stratigraphic_image.mode == img.mode
        for x in range(img.width):
            for y in range(img.height):
                assert m.stratigraphic_image.getpixel((x, y)) == img.getpixel((x, y))

        # Reset the image instance to None
        m.stratigraphic_image = None
        # Create a temporary .png file which is not a valid png
        with open(expected_png_path, "w") as fp:
            fp.write("invalid_png")
        assert expected_png_path.is_file()
        # Attempt to reopen the invalid file (simulating a corrupted png on disk). reopen_stratigraphic_image should emit a warning to stderr and set the value to None
        capsys.readouterr()
        m.reopen_stratigraphic_image()
        assert m.stratigraphic_image is None
        captured = capsys.readouterr()
        assert len(captured.out) == 0
        assert len(captured.err) > 0
        assert captured.err.startswith("Warning: unable to open Image")

    def test_reopen_chronological_image(self, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture):
        """Test that reopening the chronological image correctly mutates Model state, without the file existing, with a valid image file at the correct locaiton, and an invalid file (i.e. corrupted)"""
        m = Model("foo", tmp_path / "foo")
        expected_png_path = m.get_working_directory() / "testdag_chrono.png"
        assert m.chronological_image is None

        # When the file does not exist in the working directory, the instance value should not be mutated
        assert not expected_png_path.is_file()
        m.reopen_chronological_image()
        assert m.chronological_image is None

        # Create an image at the expected location
        m.create_dirs()
        img = Image.new("RGB", (10, 10), (255, 0, 0))
        img.save(expected_png_path)
        # Test that if a valid png exists at the expected location, an Image instance is stored
        assert expected_png_path.is_file()
        m.reopen_chronological_image()
        assert isinstance(m.chronological_image, Image.Image)
        assert m.chronological_image.size == img.size
        assert m.chronological_image.mode == img.mode
        for x in range(img.width):
            for y in range(img.height):
                assert m.chronological_image.getpixel((x, y)) == img.getpixel((x, y))

        # Reset the image instance to None
        m.chronological_image = None
        # Create a temporary .png file which is not a valid png
        with open(expected_png_path, "w") as fp:
            fp.write("invalid_png")
        assert expected_png_path.is_file()
        # Attempt to reopen the invalid file (simulating a corrupted png on disk). reopen_chronological_image should emit a warning to stderr and set the value to None
        capsys.readouterr()
        m.reopen_chronological_image()
        assert m.chronological_image is None
        captured = capsys.readouterr()
        assert len(captured.out) == 0
        assert len(captured.err) > 0
        assert captured.err.startswith("Warning: unable to open Image")

    def test_record_deleted_node(self, tmp_path: pathlib.Path):
        """Test that recording deleted nodes correctly mutates the model state"""
        m = Model("foo", tmp_path / "foo")
        # Check that there are no deleted nodes yet
        assert m.deleted_nodes == []

        # Add a deleted node, with a context but no reason.
        m.record_deleted_node("foo")
        assert len(m.deleted_nodes) == 1
        assert m.deleted_nodes[0] == ("foo", None)

        # Add another entry with an empty string for the reason
        m.record_deleted_node("bar", "")
        assert len(m.deleted_nodes) == 2
        assert m.deleted_nodes[1] == ("bar", "")

        # Add another entry with a non empty string
        m.record_deleted_node("baz", "reason")
        assert len(m.deleted_nodes) == 3
        assert m.deleted_nodes[2] == ("baz", "reason")

        # Add another entry for a node which is already present. This is allowed as a node can be created, deleted, then created again.
        m.record_deleted_node("bar", "duplicate")
        assert len(m.deleted_nodes) == 4
        assert m.deleted_nodes[3] == ("bar", "duplicate")

    def test_record_deleted_edge(self, tmp_path: pathlib.Path):
        """Test that recording delted edges correctly mutates the model state"""
        m = Model("foo", tmp_path / "foo")
        # Check that there are no deleted edges yet
        assert m.deleted_edges == []

        # Add a deleted edge, with contexts but no reason.
        m.record_deleted_edge("foo", "bar")
        assert len(m.deleted_edges) == 1
        assert m.deleted_edges[0] == ("foo", "bar", None)

        # Add another entry with an empty string for the reason
        m.record_deleted_edge("foo", "baz", "")
        assert len(m.deleted_edges) == 2
        assert m.deleted_edges[1] == ("foo", "baz", "")

        # Add another entry with a non empty string
        m.record_deleted_edge("bar", "baz", "reason")
        assert len(m.deleted_edges) == 3
        assert m.deleted_edges[2] == ("bar", "baz", "reason")

        # Add another entry for a edge which is already present. This is allowed as a edge can be created, deleted, then created again.
        m.record_deleted_edge("bar", "baz", "duplicate")
        assert len(m.deleted_edges) == 4
        assert m.deleted_edges[3] == ("bar", "baz", "duplicate")

    @pytest.mark.skip("test_MCMC_func not implemented")
    def test_MCMC_func(self, tmp_path: pathlib.Path):
        """Test MCMC_func behaves as expected for a range of inputs / Models"""
        # m = Model("foo", tmp_path / "foo")
        pass
