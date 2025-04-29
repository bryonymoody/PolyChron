from sys import stderr
from tkinter import messagebox as messagebox
from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ModelCreateView import ModelCreateView
from .BaseFramePresenter import BaseFramePresenter


class ModelCreatePresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ModelCreateView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind button callbacks to presenter methods
        view.bind_submit_button(lambda: self.on_submit_button())
        view.bind_back_button(lambda: self.on_back_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        pass  # @todo

    def on_submit_button(self) -> None:
        """When the submit button is pressed, update the data model, validate and close the view or present an error"""
        new_model_name: str = self.view.get_name()
        if len(new_model_name) > 0:
            # Validate that the model name is not already in use for the current project.
            # @todo - abstract this check into the appropriate model class.
            # If not a new project, check if the model name is in use
            is_new_project = self.model.new_project is not None and len(self.model.new_project) > 0
            if not is_new_project:
                project = self.model.projects[self.model.selected_project]
                if new_model_name in project.models:
                    # @todo - abstract use of tk.messagebox into the presenter or view base classes?
                    messagebox.showerror(
                        "Tips", "The folder name exists, please change it", parent=self.view
                    )  # @todo better error.

            # On success, update state, report it's ok and close the popup / switch to the model view
            self.model.new_model = new_model_name
            # @todo - shouldn't throw but might. Do better error handling here.
            self.model.create_model_from_self()
            messagebox.showinfo("Tips:", "model created successfully!", parent=self.view)
            # Close the model loading popup.
            self.navigator.close_navigator("new_model")
        else:
            print("Warning: a project name must be provided. @todo GUI error message", file=stderr)

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the previous view

        This behaves differntly than polychron 0.1, by returning to the previous view rather than always new project creation"""
        # Clear any value from the the models new_model property
        self.model.new_model = None
        # If there is a new_project defined, go back to project create
        if self.model.new_project is not None and len(self.model.new_project) > 0:
            self.navigator.switch_presenter("project_create")
        else:
            # Otherwise go back to the model_select view
            self.navigator.switch_presenter("model_select")
