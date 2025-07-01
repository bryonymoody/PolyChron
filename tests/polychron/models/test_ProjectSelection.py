from __future__ import annotations

import pathlib

import pytest

from polychron.models.Model import Model
from polychron.models.Project import Project
from polychron.models.ProjectsDirectory import ProjectsDirectory
from polychron.models.ProjectSelection import ProjectSelection


class TestProjectSelection:
    """Unit Tests for the model class which handles the selection and switching of projects"""

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
        """Fixture to create a mock projects directory

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir()

        # Populate the temp projects directory with some fake project directories. This should be enought for ProjectsDirectory.lazy_load to allow testing of ProjectSelection

        fake_projects = {"foo": ["bar", "baz"]}
        for project_name, model_names in fake_projects.items():
            project_dir = self.tmp_projects_dir / project_name
            project_dir.mkdir(exist_ok=True)
            for model_name in model_names:
                model_dir = project_dir / model_name
                model_dir.mkdir(exist_ok=True)

        # Yeild control to the tests
        yield

        # post-test cleanup. tmp_path_factory automatically temporary directory/file deletion
        self.tmp_projects_dir = None

    def test_init(self):
        """Test the constructor"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        # This assertion is a bit specialised, but no public project to check
        assert ps.projects_directory.path == self.tmp_projects_dir

    def test_projects_directory(self):
        """Test getting the projects directory object"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        assert ps.projects_directory is not None
        assert isinstance(ps.projects_directory, ProjectsDirectory)
        # Lazy load the projects directory, which *should* be enough for testing purposes.
        ps.projects_directory.lazy_load()

    def test_current_project_name(self):
        """Test getting and setting the current project name"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Check initialsed as None
        assert ps.current_project_name is None
        # Check that setting and getting retuns the new value
        ps.current_project_name = "foo"
        assert ps.current_project_name == "foo"

    def test_current_model_name(self):
        """Test getting and setting the current model name"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        # Check initialsed as None
        assert ps.current_model_name is None
        # Check that setting and getting retuns the new value
        ps.current_model_name = "bar"
        assert ps.current_model_name == "bar"

    def test_current_project(self):
        """Test getting and setting the current project object"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        ps.projects_directory.lazy_load()
        # Should be None when the current project is None
        assert ps.current_project is None
        # Set the currrent project name to an invalid project for the projects directory
        ps.current_project_name = "not_real"
        assert ps.current_project is None
        # After setting, should be a Project instance if it is a valid project for the projects Directory
        ps.current_project_name = "foo"
        assert ps.current_project is not None
        assert isinstance(ps.current_project, Project)

    def test_current_model(self):
        """Test getting and setting the current model object"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        # Should be None when the current project and model are None
        assert ps.current_model is None

        # With a project name but no model, it should still be None
        ps.current_project_name = "foo"
        ps.current_model_name = None
        assert ps.current_model is None

        # With a valid project but an invalid model the current model should be none
        ps.current_project_name = "foo"
        ps.current_model_name = "not_real"
        assert ps.current_model is None

        # With an invalid project but the model should be none
        ps.current_project_name = "not_real"
        ps.current_model_name = "not_real"
        assert ps.current_model is None

        # With a valid project and a valid model within the project, a Model instance should be returned.
        ps.current_project_name = "foo"
        ps.current_model_name = "bar"
        assert ps.current_model is not None
        assert isinstance(ps.current_model, Model)

    def test_next_project_name(self):
        """Test getting and setting the next project name"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Check initialsed as None
        assert ps.next_project_name is None
        # Check that setting and getting retuns the new value
        ps.next_project_name = "foo"
        assert ps.next_project_name == "foo"

    def test_next_model_name(self):
        """Test getting and setting the next model name"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        # Check initialsed as None
        assert ps.next_model_name is None
        # Check that setting and getting retuns the new value
        ps.next_model_name = "bar"
        assert ps.next_model_name == "bar"

    def test_next_project(self):
        """Test getting and setting the next project object"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        ps.projects_directory.lazy_load()
        # Should be None when the next project is None
        assert ps.next_project is None
        # Set the currrent project name to an invalid project for the projects directory
        ps.next_project_name = "not_real"
        assert ps.next_project is None
        # After setting, should be a Project instance if it is a valid project for the projects Directory
        ps.next_project_name = "foo"
        assert ps.next_project is not None
        assert isinstance(ps.next_project, Project)

    def test_next_model(self):
        """Test getting and setting the next model object"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        # Should be None when the next project and model are None
        assert ps.next_model is None

        # With a project name but no model, it should still be None
        ps.next_project_name = "foo"
        ps.next_model_name = None
        assert ps.next_model is None

        # With a valid project but an invalid model the next model should be none
        ps.next_project_name = "foo"
        ps.next_model_name = "not_real"
        assert ps.next_model is None

        # With an invalid project but the model should be none
        ps.next_project_name = "not_real"
        ps.next_model_name = "not_real"
        assert ps.next_model is None

        # With a valid project and a valid model within the project, a Model instance should be returned.
        ps.next_project_name = "foo"
        ps.next_model_name = "bar"
        assert ps.next_model is not None
        assert isinstance(ps.next_model, Model)

    def test_using_save_as(self):
        """Test getting and setting the flag which indicates the save as process is being used"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        # The flag should be false by default
        assert not ps.using_save_as
        # Set the flag to True, check that it has been updated
        ps.using_save_as = True
        assert ps.using_save_as

    def test_using_new_project_process(self):
        """Test getting and setting the flag which indicates the new project process is being used"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()
        # The flag should be false by default
        assert not ps.using_new_project_process
        # Set the flag to True, check that it has been updated
        ps.using_new_project_process = True
        assert ps.using_new_project_process

    def test_switch_to_next_project_model_assertions(self):
        """Test the method for switching to the next project & model, when the values of `next_project_name` or `next_model_name` are invalid, resulting in assertions.

        Todo:
            This should be expanded to include invalid project and model names (i.e. invalid directory names). See https://github.com/bryonymoody/PolyChron/issues/110
        """
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()

        # The next_project_name and next_model_name are None by default, which should trigger a Runtime Error
        with pytest.raises(RuntimeError):
            ps.switch_to_next_project_model()

        # With an empty project name, a Runtime error should also be raised
        ps.next_project_name = ""
        with pytest.raises(RuntimeError):
            ps.switch_to_next_project_model()

        # With an non empty (but valid or invalid) next_project_name, and an empty next_model_name, a RuntimeError should be raised
        ps.next_project_name = "foo"
        ps.next_model_name = ""
        with pytest.raises(RuntimeError):
            ps.switch_to_next_project_model()

    def test_switch_to_next_project_model_True_True(self):
        """Test the method for switching to the next project & model, when load_ok=True and create_ok=True

        This is the default option
        """
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()

        # Switch to an existing project, asserting that the class state has been updated
        ps.next_project_name = "foo"
        ps.next_model_name = "bar"
        ps.switch_to_next_project_model(load_ok=True, create_ok=True)
        assert ps.current_project_name == "foo"
        assert ps.current_model_name == "bar"
        assert ps.next_project_name is None
        assert ps.next_model_name is None
        assert not ps.using_save_as
        assert not ps.using_new_project_process

        # Switch to an new project, asserting that the class state has been updated
        ps.next_project_name = "new_project"
        ps.next_model_name = "new_model"
        ps.switch_to_next_project_model(load_ok=True, create_ok=True)
        assert ps.current_project_name == "new_project"
        assert ps.current_model_name == "new_model"
        assert ps.next_project_name is None
        assert ps.next_model_name is None
        assert not ps.using_save_as
        assert not ps.using_new_project_process

    def test_switch_to_next_project_model_True_False(self):
        """Test the method for switching to the next project & model, when load_ok=True and create_ok=False"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()

        # Switch to an existing project, asserting that the class state has been updated
        ps.next_project_name = "foo"
        ps.next_model_name = "bar"
        ps.switch_to_next_project_model(load_ok=True, create_ok=False)
        assert ps.current_project_name == "foo"
        assert ps.current_model_name == "bar"
        assert ps.next_project_name is None
        assert ps.next_model_name is None
        assert not ps.using_save_as
        assert not ps.using_new_project_process

        # Attempt to switch to an new project, which should fail as load_ok=True but create_ok=False.
        ps.next_project_name = "new_project"
        ps.next_model_name = "new_model"
        with pytest.raises(RuntimeError):
            ps.switch_to_next_project_model(load_ok=True, create_ok=False)
        assert ps.current_project_name != "new_project"
        assert ps.current_model_name != "new_model"
        assert ps.next_project_name == "new_project"
        assert ps.next_model_name == "new_model"

    def test_switch_to_next_project_model_False_True(self):
        """Test the method for switching to the next project & model, when load_ok=False and create_ok=True"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()

        # Attempt to switch to an existing project, which should fail as load_ok=False but create_ok=True.
        ps.next_project_name = "foo"
        ps.next_model_name = "bar"
        with pytest.raises(RuntimeError):
            ps.switch_to_next_project_model(load_ok=False, create_ok=True)
        assert ps.current_project_name != "foo"
        assert ps.current_model_name != "bar"
        assert ps.next_project_name == "foo"
        assert ps.next_model_name == "bar"

        # Switch to a new project, which will succeed
        ps.next_project_name = "new_project"
        ps.next_model_name = "new_model"
        ps.switch_to_next_project_model(load_ok=False, create_ok=True)
        assert ps.current_project_name == "new_project"
        assert ps.current_model_name == "new_model"
        assert ps.next_project_name != "new_project"
        assert ps.next_model_name != "new_model"
        assert not ps.using_save_as
        assert not ps.using_new_project_process

    def test_switch_to_next_project_model_False_False(self):
        """Test the method for switching to the next project & model, when load_ok=False and create_ok=False"""
        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()

        # Attempt to switch to the next model, which should raise a ValueError as one of load_ok or create_ok must be truthy
        ps.next_project_name = "foo"
        ps.next_model_name = "bar"
        with pytest.raises(
            ValueError,
            match="switch_to_next_project_model requires at least one of 'load_ok' and 'create_ok' to be True",
        ):
            ps.switch_to_next_project_model(load_ok=False, create_ok=False)

    def test_switch_to_next_project_model_using_save_as(self):
        """Test the method for switching to the next project & model, when using the save_as process.

        I.e. Ensure that the new Model is a copy of the current model, other than the Name.

        Todo:
            instead of checking that just the single property has been copied, check that all properties other than the name and path have been copied? Or Let this be checked by a Model test
        """

        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()

        # Switch to a valid project
        ps.next_project_name = "foo"
        ps.next_model_name = "bar"
        ps.switch_to_next_project_model()
        assert ps.current_project_name == "foo"
        assert ps.current_model_name == "bar"

        # Set the usign save as flag
        ps.using_save_as = True

        # Set some non-default value on the new Model
        assert not ps.current_model.load_check
        ps.current_model.load_check = True

        # Create the new project, performing the copy
        ps.next_project_name = "new_project"
        ps.next_model_name = "new_model"
        ps.switch_to_next_project_model(load_ok=False)
        # Ensure state is updated
        assert ps.current_project_name == "new_project"
        assert ps.current_model_name == "new_model"
        assert not ps.using_save_as

        # Check that the new model is a copy of the old model, i.e. the non default Model members have been updated.
        assert ps.current_model.load_check

    def test_switch_to(self):
        """Test switch_to behaves as intended, as an overload of switch_to_next_project_model.

        This is less thorough than test_switch_to_next_project_model, as it can rely on those tests"""

        ps = ProjectSelection(self.tmp_projects_dir)
        # Lazy load the mock projects
        ps.projects_directory.lazy_load()

        # Switch to an existing model
        assert ps.current_project_name is None
        assert ps.current_model_name is None
        ps.switch_to("foo", "bar")
        assert ps.current_project_name == "foo"
        assert ps.current_model_name == "bar"
