import pathlib
from dataclasses import dataclass, field
from typing import Optional

from ..models.Model import Model
from ..models.Project import Project

# @todo - when implementing loading of a projects directory, it may be better for projects to be a dict[str, List[str]], i.e. just the folders and no data loading, else there may be a lot of disk io all the time, when only a single model from a single project is actually used.


@dataclass
class ProjectsDirectory:
    """MVP Model representing the projects directory"""

    path: pathlib.Path
    """path to the projects direcotry this objet reprsents"""

    projects: dict[str, Project] = field(default_factory=dict)
    """projects within the projects directory"""

    selected_project: Optional[str] = field(default=None, init=False, repr=False)
    """The currently selected project within this project directory.

    Excluded from the __init__ method (and __repr__)
    
    @todo This is more UI than underlying data, so may need a better home."""

    selected_model: Optional[str] = field(default=None, init=False, repr=False)
    """The currently selected model within the currently selected project for this projects directory.

    Excluded from the __init__ method (and __repr__)
    
    @todo This is more UI than underlying data, so may need a better home."""

    new_project: Optional[str] = field(default=None, init=False, repr=False)
    """The name of a new project to be created.

    Excluded from the __init__ method (and __repr__)
    
    @todo This is more UI state than core ProjectsDirectory data, althoguh should be validated agianst it. 
    @todo Should this be only settable via a method which also does the validation?
    """

    new_model: Optional[str] = field(default=None, init=False, repr=False)
    """The name of a new model to be created.

    Excluded from the __init__ method (and __repr__)
    
    @todo This is more UI state than core ProjectsDirectory data, althoguh should be validated agianst it. 
    @todo Should this be only settable via a method which also does the validation?
    """

    def load(self) -> None:
        """Load the projects for the current path

        @todo - real implementation which loads from disk
        """
        self.projects = self.get_demo_projects()

    def create_model(self, project_name: str, model_name: str) -> None:
        """Create a new model in the named project (which may also be new).

        @todo - this does not actually create anything on disk
        @todo input validation here on both parameters
        """
        if project_name not in self.projects:
            self.projects[project_name] = Project(name=project_name, path=self.path / project_name)
        project = self.projects[project_name]
        if model_name in project.models:
            # @todo - better error handling here.
            raise Exception(f"{model_name} already present in {project_name}")
        else:
            project.models[model_name] = Model(name=model_name, path=project.path / model_name)

    def create_model_from_self(self) -> None:
        # @todo - validation and errors, or remove this method and just incorparte into create_model with optional params.
        project_name = self.new_project or self.selected_project
        self.create_model(project_name, self.new_model)
        # Also make sure the new_x becomes selected_x for subsequent stesp. @todo refactor this out somewhere along the way. This is a bit grim really.
        self.selected_project = project_name
        self.selected_model = self.new_model

    def get_current_project(self) -> Optional[Project]:
        """Get the current project if one is selected

        @todo - feels like this should belong elsewhere (along with select_x and new_x)"""
        if self.selected_project is not None and self.selected_project in self.projects:
            return self.projects[self.selected_project]
        else:
            return None

    def get_current_model(self) -> Optional[Model]:
        """Get the current model if one is selected.

        @todo - feels like this should belong elsewhere (along with select_x and new_x)"""
        if (
            self.selected_model is not None
            and (project := self.get_current_project()) is not None
            and self.selected_model in project.models
        ):
            return project.models[self.selected_model]
        else:
            return None

    def get_demo_projects(self) -> dict[str, Project]:
        """Build a dictionary of not-real projects for development / demo purposes

        @todo delete this method
        """

        projects = {
            "Foo": Project(
                name="Foo",
                path=self.path / "Foo",
                models={
                    "one": Model(name="one", path=self.path / "Foo" / "one"),
                    "two": Model(name="two", path=self.path / "Foo" / "two"),
                },
            ),
            "Bar": Project(
                name="Bar",
                path=self.path / "Bar",
                models={
                    "one": Model(name="one", path=self.path / "Bar" / "one"),
                    "two": Model(name="two", path=self.path / "Bar" / "two"),
                },
            ),
            "Baz": Project(
                name="Baz",
                path=self.path / "Baz",
                models={
                    "one": Model(name="one", path=self.path / "Baz" / "one"),
                    "two": Model(name="two", path=self.path / "Baz" / "two"),
                },
            ),
        }
        return projects
