import pathlib
from typing import Optional

from ..models.Model import Model
from ..models.Project import Project
from ..models.ProjectsDirectory import ProjectsDirectory


class ProjectSelection:
    """A class containing a ProjectsDirectory object, and variables related to the currently selected project/model, and the next project/model to be slelected

    @todo - rename this class.
    @todo - consider making this a data class again? Could take a ProjectsDirectory instance instead of a pathlib?
    """

    def __init__(self, projects_directory_path: pathlib.Path):
        """Initailse an instance of the ProjectSelection class, using a projects direcotry from a specified path."""

        self.__projects_directory: ProjectsDirectory = ProjectsDirectory(projects_directory_path)

        self.__current_project_name: Optional[str] = None
        """The currently selected project within the project directory."""

        self.__current_model_name: Optional[str] = None
        """The currently selected model within the currently selected project for this projects directory.
        """

        self.__next_project_name: Optional[str] = None
        """The name of the next project to be switched to, which may or may not exist
        """

        self.__next_model_name: Optional[str] = None
        """The name of a next model to be switched to, which may or may not exist
        """

        self.__using_save_as: bool = False
        """Boolean indicating if the next model switch should copy the current model or not (if one is set).
        """

        self.__using_new_project_process: bool = False
        """Boolean indicating if the new/create project process is being used, of if project selection is being used. 

        This is to provide correct back button behaviour, without validating the user provided new project name does not already exist. 

        Todo: 
            @todo - Either validate new project names when provide by a user, or if a new project name alrady exists, show the load model view next? 
        """

    @property
    def projects_directiory(self) -> ProjectsDirectory:
        """Get (a ref to) the projects directory object

        No setter is provided.

        returns:
            A reference to the ProjectsDirectory object
        """
        return self.__projects_directory

    @property
    def current_project_name(self) -> Optional[str]:
        """The name of the currently selected project, which may be None"""
        return self.__current_project_name

    @property
    def current_model_name(self) -> Optional[str]:
        """The name of the currently selected model, which may be None"""
        return self.__current_model_name

    @property
    def current_project(self) -> Optional[Project]:
        """Get (a reference) to the currently selected Project object

        Todo:
            @todo - exceptions?"""
        if self.current_project_name is not None:
            return self.__projects_directory.get_project(self.current_project_name)
        else:
            return None

    @property
    def current_model(self) -> Optional[Model]:
        """Get (a reference) to the currently selected model object

        Todo:
            @todo - exceptions? Project.get_model may load from disk, raising various exceptions"""

        if (project := self.current_project) is not None:
            if self.current_model_name is not None:
                return project.get_model(self.current_model_name)
            else:
                return None

    @current_project_name.setter
    def current_project_name(self, name: str) -> None:
        """Set the current project by name

        Todo:
            @todo - should this validate the project name here, raising if it doesn not exist yet?"""
        self.__current_project_name = name

    @current_model_name.setter
    def current_model_name(self, name: str) -> None:
        """Set the current model by name

        Todo:
            @todo - should this raise if ther is no current project yet?
            @todo - should this validate the model name here, raising if it doesn not exist yet? (and if there is not project set)"""
        self.__current_model_name = name

    @property
    def next_project_name(self) -> Optional[str]:
        """Get the name of the next project to be selected/created, which may be None"""
        return self.__next_project_name

    @property
    def next_model_name(self) -> Optional[str]:
        """Get the name of the next model to be selected/created, which may be None"""
        return self.__next_model_name

    @property
    def next_project(self) -> Optional[Project]:
        """Get (a reference) to the "next" Project object, if it already exists

        Todo:
            @todo - exceptions?"""
        if self.next_project_name is not None:
            return self.__projects_directory.get_project(self.next_project_name)
        else:
            return None

    @property
    def next_model(self) -> Optional[Model]:
        """Get (a reference) to the "next" model object, if it already exists within the next project

        Todo:
            @todo - exceptions? Project.get_model may load from disk, raising various exceptions"""

        if (project := self.next_project) is not None:
            if self.next_model_name is not None:
                return project.get_model(self.next_model_name)
            else:
                return None

    @next_project_name.setter
    def next_project_name(self, name: Optional[str]) -> None:
        """Set the current project by name

        This project may or may not exist yet.

        Todo:
            @todo - should this validate the string is a valid project name (i.e. directory name)?
        """
        self.__next_project_name = name

        #
        self.__next_project_name_is_new = False

    @next_model_name.setter
    def next_model_name(self, name: Optional[str]) -> None:
        """Set the current model by name

        This model may or may not exist yet

        Todo:
            @todo - should this validate the string is a valid model name (i.e. directory name)?
            @todo - should this raise if ther is no next project yet?"""
        self.__next_model_name = name

    @property
    def using_save_as(self) -> bool:
        """Flag indicating if the next model shoudl be copied from the current model or not."""
        return self.__using_save_as

    @using_save_as.setter
    def using_save_as(self, value: bool) -> None:
        self.__using_save_as = value

    @property
    def using_new_project_process(self) -> bool:
        """Get if the next project was a user provided new name or not.

        This does not mean the next project name is not already in use, but this is required to provide the correct back functionality during the project/model loading/creation process without validating new project names when provided.
        """
        return self.__using_new_project_process

    @using_new_project_process.setter
    def using_new_project_process(self, value: bool) -> None:
        """Set the flag indicating if the next project is new or not."""
        self.__using_new_project_process = value

    def switch_to_next_project_model(self, load_ok=True, create_ok=True) -> None:
        """Switch to the next project & model, loading a project if it already exists, or creating it if not (unless load_only). potentially copying the current model.

        Parameters:
            load_ok (bool): If loading existing models is allowed
            create_ok (bool): If creating new models is allowed

        Raises:
            @todo - document exceptions, which are raised if loading or creation failed, or if "next" internal state has not yet been setup

        Todo:
            @todo - specialise exception types for better handling downstream
            @todo - should this raise if the current model has not been saved? Or should that be handled elsewhere (probably elsewhere)
        """
        import inspect

        # Ensure that the next project and next model names have been set.
        if self.next_project_name is None or self.next_project_name == "":
            raise RuntimeError("No next project name has been specified (or is empty)")
        if self.next_model_name is None or self.next_model_name == "":
            raise RuntimeError("No next model name has been specified (or is empty)")

        # Get a handle to the current model if we are copying from it.
        copy_from = self.current_model if self.using_save_as else None

        # Get the existing or new project.
        # Any raised exceptions will be allowed to propagate upwards for presentation to the user
        project = self.projects_directiory.get_or_create_project(self.next_project_name)

        # Within that Project, get or create the model.
        # Any raised exceptions will be allowed to propagate upwards for presentation to the user
        # Depedning on function parameters, try to load or create the model
        if load_ok and create_ok:
            project.get_or_create_model(self.next_model_name, copy_from)
        elif load_ok and not create_ok:
            project.get_model(self.next_model_name)
        elif not load_ok and create_ok:
            project.create_model(self.next_model_name, copy_from)
        else:
            # Atleast one of load_ok or create_ok must be truthy
            function_name = inspect.currentframe().f_code.co_name
            raise ValueError(f"{function_name} requires at least one of 'load_ok' and 'create_ok' to be True")

        # Update internal state, setting the current and next project/model variables, if no exceptions occured so far
        self.current_project_name = self.next_project_name
        self.current_model_name = self.next_model_name
        self.next_project_name = None
        self.next_model_name = None
        self.using_save_as = False
