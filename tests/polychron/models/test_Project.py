import pathlib
from unittest.mock import patch

import pytest

from polychron.models.Model import Model
from polychron.models.Project import Project


class TestProject:
    """Unit Tests for the `models.Project` class which represents a project directory on disk and the models it contains"""

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
        """Fixture to create a mock projects directory with a single mock project directory inside

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir(exist_ok=True, parents=True)

        # Populate the temp project directory with some fake model directories. This should be enought for Projects.lazy_load etc to allow testing of Project
        # Populate the temp projects directory with a fake project directory and fake models directoeries.
        fake_projects = {"foo": ["bar", "baz"]}
        for project_name, model_names in fake_projects.items():
            project_dir = self.tmp_projects_dir / project_name
            project_dir.mkdir(exist_ok=True)
            for model_name in model_names:
                model_dir = project_dir / model_name
                model_dir.mkdir(exist_ok=True)

        # Create an Model which will raise an Exception during Model.load_from_disk, named `invalid_json` in the `invalid` project directory
        import json
        # Create an invalid json file for the foo/invalid_json model

        # Data to write to json, which should trigger an exception if this Model is loaded from disk
        data = {"invalid": "invalid"}
        json_path = self.tmp_projects_dir / "invalid" / "invalid_json" / "python_only" / "polychron_model.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w") as fp:
            json.dump(data, fp)

        # Yeild control to the tests
        yield

        # post-test cleanup. tmp_path automatically temporary directory/file deletion
        self.tmp_projects_dir = None

    def test_init(self):
        """Test `__init__` behaviour for the dataclass including default and explicit value setting/getting"""
        p = Project("foo", self.tmp_projects_dir / "foo")
        assert p.name == "foo"
        assert p.path == self.tmp_projects_dir / "foo"
        assert isinstance(p.models, dict)
        assert len(p.models) == 0

        # Check excplicit initialisation of models
        models = {
            "bar": Model("bar", self.tmp_projects_dir / "foo" / "bar"),
            "baz": Model("baz", self.tmp_projects_dir / "foo" / "baz"),
        }
        p = Project("foo", self.tmp_projects_dir / "foo", models=models)
        assert p.name == "foo"
        assert p.path == self.tmp_projects_dir / "foo"
        assert isinstance(p.models, dict)
        assert len(p.models) == 2
        for model_name, model in p.models.items():
            assert model.name == model_name
            assert model.path == self.tmp_projects_dir / "foo" / model_name

    def test_create_dir(self, capsys):
        """Test creating the directory for a project, within a temporary projects directory, including if a parent directory is missing (i.e. the projects directory does not yet exist)"""

        # Check creating a project directories for an existing project succeeds
        p = Project("foo", self.tmp_projects_dir / "foo")
        assert p.path.is_dir()
        p.create_dir()
        assert p.path.is_dir()

        # Check creating a project directories which does not yet exist works as intended.
        p = Project("bar", self.tmp_projects_dir / "bar")
        assert not p.path.is_dir()
        p.create_dir()
        assert p.path.is_dir()

        # Test that if an OSError were to occur during directory creation it would be propagated, by patching pathlib.Path.mkdir to always trigger an OSError
        p = Project("baz", self.tmp_projects_dir / "baz")
        with patch("pathlib.Path.mkdir", side_effect=OSError("Mock OSError")):
            with pytest.raises(OSError, match="Mock OSError"):
                p.create_dir()

        # Test that if an NotADirectoryError were to occur during directory creation it would be propagated. This can relaibly be tested without patching/mocking
        not_a_dir_path = self.tmp_projects_dir / "file"
        not_a_dir_path.touch()
        p = Project("baz", not_a_dir_path / "baz")
        with pytest.raises(NotADirectoryError):
            p.create_dir()

    def test_has_model(self):
        """Test `has_model` returns expected values"""
        p = Project(
            "foo", self.tmp_projects_dir / "foo", models={"bar": Model("bar", self.tmp_projects_dir / "foo" / "bar")}
        )

        assert p.has_model("bar")
        assert not p.has_model("baz")
        assert not p.has_model("")

    def test_get_model(self):
        """Test `get_model` returns the appropriate value"""

        # Test getting a model which does not exist behaves
        p = Project("foo", self.tmp_projects_dir / "foo")
        assert p.get_model("bar") is None

        # Test getting a populated model behaves
        p = Project(
            "foo", self.tmp_projects_dir / "foo", models={"bar": Model("bar", self.tmp_projects_dir / "foo" / "bar")}
        )
        assert isinstance(p.get_model("bar"), Model)

        # Test getting a lazy loaded model behaves when the model directory exists but is empty
        # @todo - this should actually return a RuntimeWarning if load_model_from_disk docstring is to be believed
        p = Project("foo", self.tmp_projects_dir / "foo", models={"bar": None})
        assert (self.tmp_projects_dir / "foo" / "bar").is_dir()
        assert isinstance(p.get_model("bar"), Model)
        assert p.models["bar"] is not None

        # Test getting a lazy loaded model behaves when the model directory does not exist.
        p = Project("foo", self.tmp_projects_dir / "foo", models={"not_real": None})
        assert not (self.tmp_projects_dir / "foo" / "not_real").is_dir()
        with pytest.raises(RuntimeWarning):
            p.get_model("not_real")

    def test_create_model(self):
        """Test `create_model` behaves as intended, including expected exceptions when a model name is already taken etc"""
        # Start with a project containing a pre-defined model, which intentionally has a non-default property set and it's directories have been created
        m = Model("bar", self.tmp_projects_dir / "foo" / "bar")
        m.create_dirs()
        m.load_check = True
        p = Project("foo", self.tmp_projects_dir / "foo", models={"bar": m})

        # Assert that creating a new model "baz" retuns a fresh model
        created_model = p.create_model("baz")
        assert isinstance(created_model, Model)
        assert created_model.name == "baz"
        assert not created_model.load_check

        # Assert that creating a new model, with a model to copy from retuns a copied model
        copied_model = p.create_model("bar_copy", m)
        assert isinstance(copied_model, Model)
        assert copied_model.name == "bar_copy"
        assert copied_model.load_check

        # Assert that a RuntimeError is raised if the new model name is already in use for this Project
        with pytest.raises(RuntimeError):
            p.create_model("bar")

        # Assert that a RuntimeError is raised if the new model name is an invalid path, resulting in a mismatch between the path and name
        with pytest.raises(RuntimeError):
            p.create_model(".")

        # Assert that an OSError is raised if create_dirs would raise one, via mocking.
        with patch("pathlib.Path.mkdir", side_effect=OSError("Mock OSError")):
            with pytest.raises(OSError, match="Mock OSError"):
                p.create_model("exception_expected")

        # Test that if an NotADirectoryError were to occur during directory creation it would be propagated. This can relaibly be tested without patching/mocking
        not_a_dir_path = self.tmp_projects_dir / "file"
        not_a_dir_path.touch()
        p = Project("baz", not_a_dir_path / "baz")
        with pytest.raises(NotADirectoryError):
            p.create_model("exception_expected")

    def test_get_or_create_model(self):
        """Test `get_or_create_model` behaves as intended for existing and new models"""
        # Start with a project containing a pre-defined model, which intentionally has a non-default property set
        m = Model("bar", self.tmp_projects_dir / "foo" / "bar")
        m.load_check = True
        p = Project("foo", self.tmp_projects_dir / "foo", models={"bar": m})

        # Assert that getting or creating "bar" returns the mutated model
        loaded_model = p.get_or_create_model("bar")
        assert isinstance(loaded_model, Model)
        assert loaded_model.name == "bar"
        assert loaded_model.load_check
        assert loaded_model == m

        # Assert that getting or creating a new model "baz" retuns a fresh model
        created_model = p.get_or_create_model("baz")
        assert isinstance(created_model, Model)
        assert created_model.name == "baz"
        assert not created_model.load_check

        # Assert that getting or creating a new model, with a model to copy from retuns a copied model
        copied_model = p.get_or_create_model("bar_copy", m)
        assert isinstance(copied_model, Model)
        assert copied_model.name == "bar_copy"
        assert copied_model.load_check

    def test_load_model_from_disk(self, capsys: pytest.CaptureFixture):
        """Test `load_model_from_disk` raises appropraite extensions or calls the appropriate Model method(s) to load a model.

        This does not include testing that loading from disk is actually functional, just that the method eitehr raises an error if the model directory does not exist, or returns a Model instance otherwise.

        Todo:
            Extend test to include a RuntimeError being triggered
        """
        # With a project containing a lazy loaded model bar, which has a directory on disk
        p = Project("foo", self.tmp_projects_dir / "foo", models={"bar": None})
        assert (self.tmp_projects_dir / "foo" / "bar").is_dir()
        # Assert that load_model_from_disk updates the value for "bar" in the models directory is no longer None
        p.load_model_from_disk("bar")
        assert p.models["bar"] is not None
        assert isinstance(p.models["bar"], Model)

        # With a project containing a lazy loaded model "baz", which does not have a directory on disk
        p = Project("foo", self.tmp_projects_dir / "foo", models={"not_real": None})
        assert not (self.tmp_projects_dir / "foo" / "not_real").is_dir()
        # Assert that load_model_from_disk raises an exception.
        captured = capsys.readouterr()
        with pytest.raises(RuntimeWarning):
            p.load_model_from_disk("not_real")
        captured = capsys.readouterr()
        assert len(captured.err) > 0

    def test_lazy_load(self):
        """Test `lazy_load` behaves as intended, populating the models data structure if a model directory exists, but does not check that a saved model is present"""
        # With an empty Projects object pointed at the temporary projects directory, but no Models specified
        p = Project("foo", self.tmp_projects_dir / "foo")

        # Assert there are no models yet
        assert len(p.models) == 0

        # Lazily load the models, which should not throw
        p.lazy_load()

        # Assert that there are now 2 models, both set to None
        assert len(p.models) == 2
        for model_name, model in p.models.items():
            assert model_name in ["bar", "baz"]
            assert model is None

    def test_load(self):
        """Test `load` behaves as intended, iterating a mock models directory calling `load_model_from_disk` for each directory, potentially raising an exception."""
        # With an empty Projects object pointed at the temporary projects directory, but no Models specified
        p = Project("foo", self.tmp_projects_dir / "foo")

        # Assert there are no models yet
        assert len(p.models) == 0

        # Lazily load the models, which should not throw
        p.load()

        # Assert that there are now 2 models, both set to None
        assert len(p.models) == 2
        for model_name, model in p.models.items():
            assert model_name in ["bar", "baz"]
            assert isinstance(model, Model)

        # Assert that if load_model_from_disk were to raise an exception, it would be propagated up. I.e. if the serialised Model json file is invalid.
        p = Project("foo", self.tmp_projects_dir / "invalid")
        # Ensure the fixture worked, creating the invalid json file
        assert (self.tmp_projects_dir / "invalid" / "invalid_json").is_dir()
        assert (self.tmp_projects_dir / "invalid" / "invalid_json" / "python_only" / "polychron_model.json").is_file()
        # Assert that load_model_from_disk raises an exception.
        with pytest.raises(RuntimeError):
            p.load()
