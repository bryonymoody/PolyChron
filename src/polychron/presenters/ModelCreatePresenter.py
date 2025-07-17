import sys

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ModelCreateView import ModelCreateView
from .FramePresenter import FramePresenter


class ModelCreatePresenter(FramePresenter[ModelCreateView, ProjectSelection]):
    def __init__(self, mediator: Mediator, view: ModelCreateView, model: ProjectSelection) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Bind button callbacks to presenter methods
        view.bind_submit_button(lambda: self.on_submit_button())
        view.bind_back_button(lambda: self.on_back_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update the view with the current project name."""
        if self.model.next_project_name is not None:
            project_name = self.model.next_project_name
            self.view.set_project_name(project_name)
        else:
            self.view.set_project_name("New")

    def on_submit_button(self) -> None:
        """When the submit button is pressed, update the data model, validate and close the view or present an error"""
        new_model_name = self.view.get_name()
        if len(new_model_name) > 0:
            # Set the next model name
            self.model.next_model_name = new_model_name

            # Try and create + switch to the next model
            try:
                self.model.switch_to_next_project_model(load_ok=False, create_ok=True)
            except RuntimeError as e:
                # Runtime errors currently include existing directories (and missing values)
                self.view.messagebox_error("Tips", f"An error occurred while creating the model: {e}")
            except Exception as e:
                # Other exceptions may occur, i.e. permission errors. Forward the message to the user.
                self.view.messagebox_error("Tips", f"An error occurred while creating the model: {e}")
            else:
                # If no exceptions occurred, and the model has been created (and it's folders) present a success message and close the popup.
                self.view.messagebox_info("Tips:", "Model created successfully!")
                # Close the model loading popup.
                self.mediator.close_window("new_model")
        else:
            print("Warning: a project name must be provided.", file=sys.stderr)

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the previous view

        This behaves differently than polychron 0.1, by returning to the previous view rather than always new project creation"""
        # Clear any value from the the models new_model property
        self.model.next_model_name = None
        # If we came from project_create, return to it. Otherwise return to model_select
        if self.model.using_new_project_process:
            self.mediator.switch_presenter("project_create")
        else:
            # Otherwise go back to the model_select view
            self.mediator.switch_presenter("model_select")
