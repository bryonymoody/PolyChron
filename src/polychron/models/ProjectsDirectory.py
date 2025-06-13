import pathlib
from dataclasses import dataclass, field
from typing import Optional

from ..models.Project import Project


@dataclass
class ProjectsDirectory:
    """MVP Model representing the projects directory"""

    path: pathlib.Path
    """path to the projects direcotry this objet reprsents"""

    projects: dict[str, Project] = field(default_factory=dict)
    """projects within the projects directory"""

    def lazy_load(self) -> None:
        """Lazily load the projects for the current path"""
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

        Parameters:
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

        """
        if self.has_project(project_name):
            project = self.get_project(project_name)
            if project is not None:
                return project

        # If no project was returned, create one and return it.
        self.projects[project_name] = Project(name=project_name, path=self.path / project_name)
        return self.projects[project_name]
