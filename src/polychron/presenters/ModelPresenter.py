import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askopenfile
from typing import Any, Optional

import pandas as pd

from ..interfaces import Mediator
from ..models.Model import Model
from ..presenters.CalibrateModelSelectPresenter import CalibrateModelSelectPresenter
from ..presenters.DatafilePreviewPresenter import DatafilePreviewPresenter
from ..presenters.MCMCProgressPresenter import MCMCProgressPresenter
from ..presenters.ResidualCheckPopupPresenter import ResidualCheckPopupPresenter
from ..presenters.ResidualOrIntrusivePresenter import ResidualOrIntrusivePresenter
from ..util import imgrender, imgrender_phase
from ..views.CalibrateModelSelectView import CalibrateModelSelectView
from ..views.DatafilePreviewView import DatafilePreviewView
from ..views.MCMCProgressView import MCMCProgressView
from ..views.ModelView import ModelView
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.ResidualCheckPopupView import ResidualCheckPopupView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .BaseFramePresenter import BaseFramePresenter
from .ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter


class ModelPresenter(BaseFramePresenter):
    """Presenter for the main model tab

    @todo - re-order methods and properties to be logical (rather than in order of porting)"""

    def __init__(self, mediator: Mediator, view: ModelView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Properties
        self.strat_check: bool = False
        """If a strat file has been loaded or not
        
        @todo - Should this actually belong to the .model.Model?
        @todo - initalse these variables with values from the model on load?
        """

        self.date_check: bool = False
        """If a data file has been loaded or not
        
        @todo - Should this actually belong to the .model.Model?
        @todo - initalse these variables with values from the model on load?
        """

        self.phase_check: bool = False
        """If a phase file has been loaded or not
        
        @todo - Should this actually belong to the .model.Model?
        @todo - initalse these variables with values from the model on load?
        """

        self.phase_rel_check: bool = False
        """If a phase_rel file has been loaded or not
        
        @todo - Should this actually belong to the .model.Model?
        @todo - initalse these variables with values from the model on load?
        """

        self.phase_true: int = 0
        """If stratigraphic diagram should be rendered in phases or not
        
        @todo - make a bool, rename
        @todo - should this belong to the .model.Model?
        @todo - initalse these variables with values from the model on load?
        """

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.mediator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.mediator.switch_presenter("DatingResults"))

        # Bind menu callbacks
        self.view.bind_file_menu_callbacks(
            {
                "Load stratigraphic diagram file (.dot)": lambda: self.open_strat_dot_file(),
                "Load stratigraphic relationship file (.csv)": lambda: self.open_strat_csv_file(),
                "Load scientific dating file (.csv)": lambda: self.open_scientific_dating_file(),
                "Load context grouping file (.csv)": lambda: self.open_context_grouping_file(),
                "Load group relationship file (.csv)": lambda: self.open_group_relationship_file(),
                "Load context equalities file (.csv)": lambda: self.open_context_equalities_file(),
                "Load new project": lambda: self.load_project(),
                "Load existing model": lambda: self.load_existing_model(),
                "Save changes as current model": lambda: self.save_as_current(),
                "Save changes as new model": lambda: self.save_as_new_model(),
                "Exit": lambda: self.close_application(),
            }
        )
        self.view.bind_view_menu_callbacks(
            {
                "Display Stratigraphic diagram in phases": lambda: self.phasing(),
            }
        )
        self.view.bind_tool_menu_callbacks(
            {
                "Render chronological graph": lambda: self.chronograph_render_wrap(),
                "Calibrate model": lambda: self.popup_calibrate_model(),
                "Calibrate multiple projects from project": lambda: self.popup_calibrate_multiple(),
                "Calibrate node delete variations (alpha)": lambda: self.calibrate_node_delete_variations(),
                "Calibrate important variations (alpha)": lambda: self.calibrate_important_variations(),
            }
        )

        # Bind button clicks
        # Bind the "Data loaded" button callback
        self.display_data_var = "hidden"  # @todo - enum, save this as state?
        self.view.bind_data_button(lambda: self.on_data_button())

        # Bind the callback for activating the testmenu
        self.view.bind_testmenu_commands(lambda event: self.on_testmenu(event))

        # Bind mouse & keyboard events
        self.view.bind_littlecanvas_callback("<Button-3>", lambda event: self.pre_click(event))

        # @todo

        # Update the view to reflect the current staet of the model
        self.update_view()

    def update_view(self) -> None:
        """Update the view to reflect the current state of the model

        @todo expand this"""
        # Get the actual model
        # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        # If the model has an @todo abstrac this to reduce duplication
        if model_model.strat_df is not None:
            if self.phase_true == 1:
                model_model.strat_image = imgrender_phase(model_model.strat_graph)
            else:
                model_model.strat_image = imgrender(
                    model_model.strat_graph,
                    self.view.littlecanvas.winfo_width(),
                    self.view.littlecanvas.winfo_height(),
                )  # @todo - get the view width/height cleaner
            # Update the view
            self.view.update_littlecanvas(model_model.strat_image)

        # Make sure that the check marks are up to date
        if model_model.strat_df is not None:
            self.strat_check = True
        if model_model.date_df is not None:
            self.date_check = True
        if model_model.phase_df is not None:
            self.phase_check = True
        if model_model.phase_rel_df is not None:
            self.phase_rel_check = True
        self.check_list_gen()

    def popup_calibrate_model(self) -> None:
        """Callback function for when Tools -> Calibrate model is selected

        @todo - this allows multiple open project windows to be created, which is not ideal
        """
        # Create the popup presenter and view
        popup_presenter = MCMCProgressPresenter(self.mediator, MCMCProgressView(self.view), self.model)
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()
        # Run the calibration
        # @todo - gracefully handle errors during calibration
        popup_presenter.run()
        # Ensure model data is correct / updated in memory
        # @todo
        # Close the popup
        popup_presenter.close_view()
        # Change to the DatingResults tab (assuming the calibration ran successfully @todo)
        self.mediator.switch_presenter("DatingResults")

        # @todo - esnure the presenter is destroyed

    def popup_calibrate_multiple(self) -> None:
        """Callback function for when Tools -> Calibrate multiple projects from project is selected

        Opens a new popup box allowing the user to select which models from a list to calibrate as a batch.
        On close, depending on if any models were selected or not, the models are subsequently calibrated

        @todo - this allows multiple open project windows to be created, which is not ideal
        """
        popup_presenter = CalibrateModelSelectPresenter(self.mediator, CalibrateModelSelectView(self.view), self.model)
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()

        # Calibrate the selected models
        # see popupwindow8::cleanup
        pass  # @todo

    def chronograph_render_wrap(self):
        """wraps chronograph render so we can assign a variable when runing the func using a button"""

        # @todo Implement this method with the yes/no box depedning on if a chrono dag already exists or not.

        # Render the chronograph temporarily
        self.chronograph_render()

    def chronograph_render(self):
        """initiates residual checking function then renders the graph when thats done

        @todo finish this"""

        # @todo check if loaded

        # Check for residuals
        self.resid_check()

        # @todo rest of the method

    def resid_check(self):
        """Loads a text box to check if the user thinks any samples are residual

        @todo - should the import of tk be moved into a view  / wrap tk.messagebox?
        @todo - is this the most appropraite place for this method? (think so)
        """
        MsgBox = tk.messagebox.askquestion(
            "Residual and Intrusive Contexts",
            "Do you suspect any of your samples are residual or intrusive?",
            icon="warning",
        )
        if MsgBox == "yes":
            # Create and show the residual or intrusive presetner
            popup_presenter = ResidualOrIntrusivePresenter(
                self.mediator, ResidualOrIntrusiveView(self.view), self.model
            )
            popup_presenter.view.deiconify()
            popup_presenter.view.lift()  # @todo - not sure these are neccesary
        else:
            # If not, show the residual check presenter, formerly popupWindow3
            popup_presenter = ResidualCheckPopupPresenter(self.mediator, ResidualCheckPopupView(self.view), self.model)
            popup_presenter.view.deiconify()
            popup_presenter.view.lift()  # @todo - not sure these are neccesary

    def file_popup(self, df: Any) -> str:
        """For a gien dataframe, preview the data to the user. Returns the users decision

        @todo - make this return a bool instead of 'load' or 'cancel'
        """
        # @todo set and get model data appropriately
        temp_model = {"df": df, "result": "cancel"}
        popup_presenter = DatafilePreviewPresenter(self.mediator, DatafilePreviewView(self.view), temp_model)
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()  # @todo - not sure these are neccesary

        # Prevent the view's canvas element from being interacted with?
        self.view.canvas["state"] = "disabled"  # @todo
        self.view.parent.wait_window(popup_presenter.view)  # @todo - view.parent mignt not have wiat_window?
        self.view.canvas["state"] = "normal"  # @todo
        return temp_model["result"]

    def open_strat_dot_file(self) -> None:
        """Callback function when File > Load stratigraphic diagram file (.dot) (.csv) is selected, opening a .dot / graphviz file representing the stratigraphic relationships

        Formerly StartPage.open_file1

        @todo - Implement this, once a "valid" dotfile for this is found.
        @todo - Need to fixup the use of FILE_INPUT in funcs like phase_info_func once this is implemented.
        """
        # @todo
        # global node_df, FILE_INPUT, phase_true
        file = askopenfile(mode="r", filetypes=[("DOT Files", "*.dot"), ("Graphviz Files", "*.gv")])
        self.dot_file = file  # @todo - temp warning suppression
        # FILE_INPUT = file.name
        # self.graph = nx.DiGraph(imagefunc(file.name), graph_attr={'splines':'ortho'})
        # if phase_true == 1:
        #     self.image = imgrender_phase(self.graph)
        # else:
        #     self.image = imgrender(self.graph)
        # self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        # self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw", image=self.littlecanvas.img)

        # self.width, self.height = self.image.size
        # self.imscale = 1.0  # scale for the canvaas image
        # # self.imscale  = min(921/self.image.size[0], 702/self.image.size[1])
        # self.delta = 1.1  # zoom magnitude
        # # Put image into container rectangle and use it to set proper coordinates to the image
        # self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        # self.bind("<Configure>", self.resize)
        # self.littlecanvas.scale('all', 0, 0, self.delta, self.delta)  # rescale all canvas objects
        # self.show_image()
        # self.littlecanvas.bind("<Configure>", self.resize)
        # self.delnodes = []
        # self.delnodes_meta = []
        # self.canvas.delete('all')
        # self.littlecanvas.bind("<Button-3>", self.preClick)

    def open_strat_csv_file(self) -> None:
        """Callback function when File > Load stratigraphic relationship file (.csv) is selected, opening a plain text strat file

        Formerly StartPage.open_file2

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - Column and value validation (within the data model, with exceptions handeled here?)

        @todo - if a new strat file is loaded over the top of an old one, what should happen to the other bits of data?
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])

        if file is not None:
            try:
                # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
                model_model: Model = self.model.get_current_model()
                df = pd.read_csv(file, dtype=str)
                # @todo - Validate the parsed df here, so the errors can be included in the file popup?
                load_it = self.file_popup(df)
                if load_it == "load":
                    # update the model with the dataframe, perofrming post processing, producing the graph
                    model_model.set_strat_df(df)
                    tk.messagebox.showinfo("Success", "Stratigraphic data loaded")
                    # Mark the strat file as loaded @todo this can just be implicit from the model's state
                    self.strat_check = True
                    # Update the check list
                    self.check_list_gen()

                    # Render the image in phases or not
                    if self.phase_true == 1:
                        model_model.strat_image = imgrender_phase(model_model.strat_graph)
                    else:
                        model_model.strat_image = imgrender(
                            model_model.strat_graph,
                            self.view.littlecanvas.winfo_width(),
                            self.view.littlecanvas.winfo_height(),
                        )  # @todo - get the view width/height cleaner
                    # Update the view
                    self.view.update_littlecanvas(model_model.strat_image)

                else:
                    pass  # @todo this case.
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_scientific_dating_file(self) -> None:
        """Callback function when File > Load scientific dating file (.csv) is selected, opening a scientific dating file

        Formerly StartPage.open_file3

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - finish implementing this with the actual model

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])

        if file is not None:
            try:
                # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
                model_model: Model = self.model.get_current_model()
                df = pd.read_csv(file)
                df = df.applymap(str)
                load_it = self.file_popup(df)
                if load_it == "load":
                    model_model.set_date_df(df)
                    self.date_check = True
                    self.check_list_gen()
                    tk.messagebox.showinfo("Success", "Scientific dating data loaded")
                else:
                    pass  # @todo - should this also show an error when the user chooses not to press load?
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_context_grouping_file(self) -> None:
        """Callback function when File > Load context grouping file (.csv) is selected, opening context grouping / phase file

        Formerly StartPage.open_file4

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - Consistent use of terms - phase vs group.

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
                model_model: Model = self.model.get_current_model()
                df = pd.read_csv(file)
                df = df.applymap(str)
                load_it = self.file_popup(df)
                if load_it == "load":
                    model_model.set_phase_df(df)
                    self.phase_check = True
                    self.check_list_gen()
                    tk.messagebox.showinfo("Success", "Grouping data loaded")
                else:
                    pass  # @todo - should this also show an error when the user chooses not to press load?
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_group_relationship_file(self) -> None:
        """Callback function when File > Load group relationship file (.csv) is selected, opening a group relationship / phase relationship file

        Formerly StartPage.open_file5

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - Nothing happens with the result from file_popup here. I.e. pressing load or not doesn't matter.

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
                model_model: Model = self.model.get_current_model()
                df = pd.read_csv(file)
                # @todo - de-duplicate this into the model
                phase_rels = [(str(df["above"][i]), str(df["below"][i])) for i in range(len(df))]
                # @todo - this is not an actual input file preview like the others, but a preview of the reshaped data. i.e. titles don't match.
                load_it = self.file_popup(pd.DataFrame(phase_rels, columns=["Younger group", "Older group"]))
                model_model.set_phase_rel_df(df, phase_rels)
                if load_it:
                    pass  # @todo - 0.1 doesn't check the result / handle the paths differently.
                self.phase_rel_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Group relationships data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_context_equalities_file(self) -> None:
        """Callback function when File > Load context equalities file (.csv) is selected, opening a file providing context equalities (in time)

        Formerly StartPage.open_file6

        @todo - Show a preview of this to the user to match other file loading?

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
                model_model: Model = self.model.get_current_model()
                df = pd.read_csv(file)
                df = df.applymap(str)
                # Update the model & post process, updating the graph
                model_model.set_equal_rel_df(df)
                # @todo - this method did not open a file_preview / popup.

                # Render the image in phases or not @todo - abstract this repeated block
                if self.phase_true == 1:
                    model_model.strat_image = imgrender_phase(model_model.strat_graph)
                else:
                    model_model.strat_image = imgrender(
                        model_model.strat_graph,
                        self.view.littlecanvas.winfo_width(),
                        self.view.littlecanvas.winfo_height(),
                    )  # @todo - get the view width/height cleaner
                # Update the view, showing the new image
                self.view.update_littlecanvas(model_model.strat_image)
                tk.messagebox.showinfo("Success", "Equal contexts data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def close_application(self) -> None:
        """Close polychron gracefully via File > Exit"""
        # @todo - alert on any unsaved changed?
        self.mediator.close_window("exit")

    def phasing(self):
        """Callback function for View > Display Stratigraphic diagram in phases

        Runs image render function with phases on seperate levels

        Formerly StartPage.phasing

        @todo - Make this toggle on and off, rather than just on.

        @todo - need a test case which actually renders differntly when in phasing mode.
        """
        # Store a flag marking this as being enabled
        self.phase_true = 1

        # Render the strat graph in pahse mode, if there is one to render, updating the model and view
        model_model: Model = self.model.get_current_model()
        if model_model.strat_graph is not None:
            model_model.strat_image = imgrender_phase(model_model.strat_graph)
            # Update the rendered image in the canvas
            self.view.update_littlecanvas(model_model.strat_image)

    def calibrate_node_delete_variations(self) -> None:
        """Callback function when Tools > Calibrate node delete variations (alpha)

        Formerly popupWindow9

        @todo - popupWindow9 doesn't / didn't have any of it's own tkinter code, so not yet implemented
        """
        print("@todo - implement calibrate_node_delete_variations/popupWindow9")

    def calibrate_important_variations(self) -> None:
        """Callback function when Tools > Calibrate node delete variations (alpha)

        Formerly popupWindow10

        @todo - popupWindow10 doesn't / didn't have any of it's own tkinter code, so not yet implemented
        """
        print("@todo - implement calibrate_important_variations/popupWindow10")

    def on_data_button(self) -> None:
        """Callback for when the "Data Loaded" button is pressed, which toggles the visibility of which required input files have been parsed or not

        Formerly StartPage.display_data_func

        @todo enum
        """

        if self.display_data_var == "hidden":
            self.view.lift_datacanvas()
            self.display_data_var = "onshow"
        elif self.display_data_var == "onshow":
            self.view.lift_littelcanvas()
            self.display_data_var = "hidden"

    def on_testmenu(self, event) -> None:
        """Callback for when the testmenu is selected (the right option menu when right clicking on the littlecanvas)

        Formerly StartPage.nodes

        @todo - split this into much smaller methods
        """
        print("@todo - on_testmenu()/nodes()") # @todod

    def pre_click(self, *args):
        '''makes test menu appear and removes any previous test menu
        
        formerly StartMenu.preClick'''
        try:
            self.testmenu.place_forget()
            self.on_right()
        except Exception:
            self.on_right()

    def on_left(self, *args):
        '''hides menu when left clicking
        
        Formerly StartMenu.onLeft'''
        try:
            self.testmenu.place_forget()
        except Exception:
            pass

    def on_right(self, *args) -> None:
        """Makes the test menu appear after right click
        
        Formerly StartPage.onRight"""
        # Unbind and rebind on_left. @todo this feels wrong.
        self.view.unbind_littlecanvas_callback("<Button-1>")
        self.view.bind_littlecanvas_callback("<Button-1>", self.on_left)
        # Show the right click menu
        model_model: Model = self.model.get_current_model()
        has_image = model_model.strat_image is not None
        self.view.show_testmenu(has_image)
        # @todo implement node selection int he model-presenter
        # if self.image != "noimage":
        #     x_scal = self.cursorx + self.transx
        #     y_scal = self.cursory + self.transy
        #     self.node = self.nodecheck(x_scal, y_scal)

    def check_list_gen(self) -> None:
        """Update the contents of the datacanvas checklist based on provided model state

        Formerly StartPage.check_list_gen
        """
        self.view.update_datacanvas_checklist(self.strat_check, self.date_check, self.phase_check, self.phase_rel_check)

    def load_project(self) -> None:
        """open a popup dialog to load a model from a different project

        Formerly a call to load_Window(MAIN_FRAME)"""

        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.mediator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()

    def load_existing_model(self) -> None:
        """Open a popup dialog to load an existing model from the current project (althoug possible to go back?)

        Formerly a call to load_Window(MAIN_FRAME, proj_dir)

        @todo - the ProjectSelectProcessPopupPresenter having a separte model object here than the ModelView would be useful, to avoid the back button followed by closing the popup causing issues
        """
        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.mediator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Switch to the model select page, app state should have the correct selected_project still
        popup_presenter.switch_presenter("model_select")
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()

    def save_as_current(self) -> None:
        """Save the current state of the model in-place

        Formerly StartPage.save_state_1"""
        if model := self.model.get_current_model():
            model.save()
        else:
            pass  # @todo handle gracefully, but this should never occur.

    def save_as_new_model(self) -> None:
        """Save the current state of the model, as a new model (with a new name) initially in the same project (although possible to put in a new project)

        @todo - in PolyChron 0.1, save as new model maintains current state in a new project, but does not save the state to disk until save_as_current is called. On load however, this fails to load anything. Query with Bryony the intended behaviour.
        Error: dot: can't open fi_new_chrono

        @todo - in PolyChron 0.1, if the new model name is already taken, the popup is presented but the window closes anyway rather than allowing a new name to be made.

        @todo - in PolyChron 0.1, it's possible to press Back, enter a new project name, and then a new model name. This just creates a blank model in the new project. Decide how this should behave / if the back button should even be there.

        Formerly StartPage.refresh_4_new_model"""
        # Open the project saving dialogue, starting with the new_model view in this current project
        # On close of the popup via the save button, save the model.

        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.mediator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Switch to the model select page, app state should have the correct selected_project still
        popup_presenter.switch_presenter("model_create")
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()

        print("@todo - save_as_new_model partially implemented")
        # @todo - Ensure that data is copied, not replaced.
        # model.save()
