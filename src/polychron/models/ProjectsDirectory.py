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

    def lazy_load(self) -> None:
        """Lazily load the projects for the current path

        Todo:
            @todo - this is destructive. I.e. if the ProjectWelcomePresenter is opened, after a model has been changed but not saved, this may overwrite changes back to the state on disk for a currently open project (which may be intended), or clear unsaved state for a "new" project/model
        """
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

    def has_project(self, project_name: str) -> bool:
        """Check if the specified project exists or not"""
        return project_name in self.projects

    def get_project(self, project_name: str) -> Optional[Project]:
        """Fetch a project by it's name

        Paramaters:
            project_name: the name of the project to fetch

        Returns:
            The project if it exists, else None.
        """
        return self.projects.get(project_name, None)

    def get_or_create_project(self, project_name: str) -> Project:
        """Get or create a project within this projects directory.

        Parameters:
            project_name (str): The name of the project to be fetched or created

        Returns:
            The existing or new project with the specified project name

        Raises:
            @todo - document rasised exceptions
        """
        if self.has_project(project_name):
            project = self.get_project(project_name)
            if project is not None:
                return project

        # @todo - this should raise exceptions if the project_name is bad.
        # If no project was returned, create one and return it.
        self.projects[project_name] = Project(name=project_name, path=self.path / project_name)
        return self.projects[project_name]

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
