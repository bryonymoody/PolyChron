import pathlib

import pytest

from polychron.models.Project import Project
from polychron.models.ProjectsDirectory import ProjectsDirectory


class TestProjectsDirectory:
    """Unit Tests for the model class which represents the projects directory"""

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
        """Fixture to create a mock projects directory

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir(exist_ok=True, parents=True)

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
        """Test the ProjectsDirectory __init__ method"""
        # Test __init__ just the required path
        pd = ProjectsDirectory(self.tmp_projects_dir)
        assert pd.path == self.tmp_projects_dir
        assert isinstance(pd.projects, dict)
        assert len(pd.projects) == 0

        # Check with a path and a dictionary of projects
        projects = {
            "a": Project("a", self.tmp_projects_dir / "a"),
            "b": Project("b", self.tmp_projects_dir / "b"),
        }
        pd = ProjectsDirectory(self.tmp_projects_dir, projects=projects)
        assert pd.path == self.tmp_projects_dir
        assert isinstance(pd.projects, dict)
        assert len(pd.projects) == 2

    def test_lazy_load(self):
        """Test the ProjectsDirectory lazy_load method"""
        pd = ProjectsDirectory(self.tmp_projects_dir)

        # The projects dict should be empty initially
        assert len(pd.projects) == 0

        # Lazily load the mock projects, which should progress without raising any exceptions
        pd.lazy_load()

        # After lazy loading the mock projects directory, there should now be 1 project with 2 models.
        assert len(pd.projects) == 1
        assert len(pd.projects["foo"].models) == 2

    def test_lazy_load_empty_dir(self, tmp_path):
        """Test the ProjectsDirectory lazy_load method for an empty projects directory"""
        pd = ProjectsDirectory(tmp_path / "not_real")

        # The projects dict should be empty initially
        assert len(pd.projects) == 0

        # Lazily load the mock projects, which should progress without raising any exceptions
        pd.lazy_load()

        # After lazy loading the mock projects directory, it shoudl still be empty
        assert len(pd.projects) == 0

    def test_has_project(self):
        """Test the ProjectsDirectory has_project method"""
        # Lazy Load the mock projects directory
        pd = ProjectsDirectory(self.tmp_projects_dir)
        pd.lazy_load()

        # has_project should return true for "foo", but false for anything else.
        assert pd.has_project("foo")
        assert not pd.has_project("bar")
        assert not pd.has_project("baz")
        assert not pd.has_project("")

    def test_get_project(self):
        """Test the ProjectsDirectory get_project method"""
        # Lazy Load the mock projects directory
        pd = ProjectsDirectory(self.tmp_projects_dir)
        pd.lazy_load()

        # get_project should return a Project instance for "foo", and None for invalid projects
        p_foo = pd.get_project("foo")
        assert p_foo is not None
        assert isinstance(p_foo, Project)
        assert pd.get_project("bar") is None
        assert pd.get_project("baz") is None
        assert pd.get_project("") is None

    def test_get_or_create_project(self):
        """Test the ProjectsDirectory get_or_create_project method"""
        # Lazy Load the mock projects directory
        pd = ProjectsDirectory(self.tmp_projects_dir)
        pd.lazy_load()

        # get_or_create_project should return a Project instance for "foo", which has atleast one model (i.e. it's an existing project)
        p_foo = pd.get_or_create_project("foo")
        assert isinstance(p_foo, Project)
        assert len(p_foo.models) > 0

        # get_or_create_project should return a Project instance for new projects such as "bar", but it should not contain any models as it is new.
        p_bar = pd.get_or_create_project("bar")
        assert p_bar is not None
        assert isinstance(p_bar, Project)
        assert len(p_bar.models) == 0
