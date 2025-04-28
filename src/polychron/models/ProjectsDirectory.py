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

    def load(self) -> None:
        """Load the projects for the current path

        @todo - real implementation which loads from disk
        """
        self.projects = self.get_demo_projects()

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
