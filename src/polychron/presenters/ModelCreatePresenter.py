from sys import stderr
from tkinter import messagebox as messagebox
from typing import Optional

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ModelCreateView import ModelCreateView
from .BaseFramePresenter import BaseFramePresenter


class ModelCreatePresenter(BaseFramePresenter):
    def __init__(self, mediator: Mediator, view: ModelCreateView, model: Optional[ProjectSelection] = None) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

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
            # Set the next model name
            self.model.next_model_name = new_model_name

            # Try and create + switch to the next model
            try:
                print(
                    "@todo switch_to_next here allows loading, not jsut creation. Should call create here, and then switch afterwards / a lighter weight switch?"
                )
                self.model.switch_to_next_project_model(load_ok=False, create_ok=True)
            except RuntimeError as e:
                # Runtime errors currently include existing directories (and missing values)
                # @todo - abstract use of tk.messagebox into the presenter or view base classes
                # @todo - better error message, formerly "The folder name exists, please change it"
                messagebox.showerror("Tips", f"An error occured while creating the model: {e}", parent=self.view)
            except Exception as e:
                # Other exceptions may occur, i.e. permission errors. Forward the message to the user.
                # @todo - abstract use of tk.messagebox into the presenter or view base classes
                # @todo - better error message, formerly "The folder name exists, please change it"
                messagebox.showerror("Tips", f"An error occured while creating the model: {e}", parent=self.view)
            else:
                # If no exceptions occurred, and the model has been created (and it's folders) present a succes message and close the popup.
                # @todo - abstract use of tk.messagebox into the presenter or view base classes
                messagebox.showinfo("Tips:", "model created successfully!", parent=self.view)
                # Close the model loading popup.
                self.mediator.close_window("new_model")
        else:
            print("Warning: a project name must be provided. @todo GUI error message", file=stderr)

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the previous view

        This behaves differntly than polychron 0.1, by returning to the previous view rather than always new project creation"""
        # Clear any value from the the models new_model property
        self.model.next_model_name = None
        # If we came from project_create, return to it. Otherwise return to model_select
        if self.model.using_new_project_process:
            self.mediator.switch_presenter("project_create")
        else:
            # Otherwise go back to the model_select view
            self.mediator.switch_presenter("model_select")
