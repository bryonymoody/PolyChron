import pathlib
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

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
        """Load the projects for the current path"""
        # self.projects = self.get_demo_projects()
        # return
        self.projects = {}
        # Iterate the current project directory if it exists, each child directory is a project.
        if self.path.is_dir():
            for item in self.path.iterdir():
                if item.is_dir():
                    # Construct a project instance
                    p = Project(item.name, item, {})
                    # Lazily Load models within the project
                    p.lazy_load()
                    # Store in this instance's dict of projects
                    self.projects[p.name] = p

    def create_model(self, project_name: str, model_name: str) -> None:
        """Create a new model in the named project (which may also be new) and create the required directories

        Parameters:
            project_name: Name of the project to create/use
            model_name: Name of the model to create

        Raises:
            RuntimeError: if the model already exists, or a model name which cannot be converted to a directory name is provided
            OSError: if an exception occurs during direcotry creation.

        @todo input validation here on both parameters
        """
        # Get or create the project
        if project_name not in self.projects:
            self.projects[project_name] = Project(name=project_name, path=self.path / project_name)
        project = self.projects[project_name]
        # Attempt to create the model, which will throw exceptions if errors occur.
        project.new_model(model_name)

    def create_model_from_self(self) -> None:
        """Create a new model, based on the currently selected project if one exists, and update internal state used in the project selection / creation process

        @todo - validation / errors
        @todo - remove this method and just incorparte into create_model with optional params?
        @todo - Migrate the selected/new_project members to it's own model class / part of the presenter's state?
        """
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
            and project.has_model(self.selected_model)
        ):
            m = project.get_model(self.selected_model)
            return m
        else:
            return None

    def get_demo_projects(self) -> dict[str, Project]:
        """Build a dictionary of not-real projects for development / demo purposes

        @todo delete this method
        """

        projects = {
            "demo": Project(
                name="demo",
                path=self.path / "demo",
                models={
                    "demo": Model(name="demo", path=self.path / "demo" / "demo"),
                },
            ),
        }

        # Manually "load" some model data for the demo model, pre serialisation / de-serialisation
        # @todo - this is temporary.
        demo_model = projects["demo"].models["demo"]
        # Ensure directories exist
        demo_model.create_dirs()

        # Strat file from csv
        demo_model.set_strat_df(
            pd.DataFrame(
                [
                    ["a", "b"],
                    ["b", "c"],
                    ["b", "d"],
                    ["b", "e"],
                    ["d", "f"],
                    ["e", "h"],
                ],
                columns=["above", "below"],
            )
        )
        demo_model.set_date_df(
            pd.DataFrame(
                [
                    ["a", "3400", "80"],
                    ["b", "3300", "75"],
                    ["c", "3250", "80"],
                    ["d", "3225", "75"],
                    ["e", "3200", "80"],
                    ["f", "3150", "75"],
                    ["h", "3100", "65"],
                ],
                columns=["context", "date", "error"],
            )
        )
        demo_model.set_phase_df(
            pd.DataFrame(
                [
                    ["a", "2"],
                    ["b", "2"],
                    ["c", "1"],
                    ["d", "1"],
                    ["e", "1"],
                    ["f", "1"],
                    ["h", "1"],
                ],
                columns=["context", "Group"],
            )
        )
        demo_model.set_phase_rel_df(
            pd.DataFrame(
                [
                    ["2", "1"],
                ],
                columns=["above", "below"],
            ),
            phase_rels=[("2", "1")],  # @todo - make this actually dynamic
        )
        # demo_model.set_equal_rel_df(
        #     pd.DataFrame(
        #         [
        #             ["c", "d"],
        #         ],
        #         columns=["left", "right"],
        #     )
        # )
        # @todo - make everytyhign more type safe, so not everything needs to be read in from csv as strings?

        return projects
