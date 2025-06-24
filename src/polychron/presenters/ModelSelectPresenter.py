import sys
from tkinter import messagebox as messagebox

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ModelSelectView import ModelSelectView
from .FramePresenter import FramePresenter


class ModelSelectPresenter(FramePresenter[ModelSelectView, ProjectSelection]):
    """Presenter for a frame allowing the user to select a model from a list of models within a project, or a button to create a new one."""

    def __init__(self, mediator: Mediator, view: ModelSelectView, model: ProjectSelection) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Bind button callbacks
        self.view.bind_load_button(lambda: self.on_load_button())
        self.view.bind_back_button(lambda: self.on_back_button())
        self.view.bind_create_model_button(lambda: self.on_create_model_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        # Update the list of models to select from, if a project has been selected
        model_names = list(self.model.next_project.models.keys()) if self.model.next_project is not None else []
        self.view.update_model_list(model_names)

    def on_load_button(self) -> None:
        """When the load button is pressed, update the wider application model data structure and close the popup"""
        selected_model = self.view.get_selected_model()
        if selected_model is not None:
            # Update the data model to include the selected project
            self.model.next_model_name = selected_model
            # Try to switch to the model (load it, and update state)
            try:
                self.model.switch_to_next_project_model(load_ok=True, create_ok=False)
            except RuntimeWarning as e:
                # Runtime errors currently include existing directories (and missing values)
                messagebox.showerror("Tips", f"An error occured while loading the model: {e}", parent=self.view)
            except RuntimeError as e:
                # Runtime errors currently include existing directories (and missing values)
                messagebox.showerror("Tips", f"An error occured while loading the model: {e}", parent=self.view)
            except Exception as e:
                raise e
            else:
                # Close the popup and switch to the ModelPresenter/View if no errors occured during loading
                self.mediator.close_window("load_model")
        else:
            print("Warning: No model selected", file=sys.stderr)

    def on_back_button(self) -> None:
        """When the Back button is pressed, update the previous view and switch to it

        Unlike polychron 0.1 which returned to the project create or load screen, this returns to the project select screen
        """
        # Clear any selected model value, just in case
        self.model.next_model_name = None
        # A previous project should be known, so we can return to it. Fallback to the welcome view
        if self.model.next_project is not None:
            self.mediator.switch_presenter("project_select")
        else:
            self.mediator.switch_presenter("project_welcome")

    def on_create_model_button(self) -> None:
        """When the load button is pressed, update the current modeldata and switch to the model_create view"""
        self.mediator.switch_presenter("model_create")
