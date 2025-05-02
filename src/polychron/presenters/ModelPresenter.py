import pathlib
import tempfile
import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askopenfile
from typing import Any, List, Optional

import networkx as nx
import numpy as np
import pandas as pd
import pydot

from ..interfaces import Mediator
from ..models.Model import Model
from ..presenters.AddContextPresenter import AddContextPresenter
from ..presenters.CalibrateModelSelectPresenter import CalibrateModelSelectPresenter
from ..presenters.DatafilePreviewPresenter import DatafilePreviewPresenter
from ..presenters.MCMCProgressPresenter import MCMCProgressPresenter
from ..presenters.RemoveContextPresenter import RemoveContextPresenter
from ..presenters.RemoveStratigraphicRelationshipPresenter import RemoveStratigraphicRelationshipPresenter
from ..presenters.ResidualCheckPopupPresenter import ResidualCheckPopupPresenter
from ..presenters.ResidualOrIntrusivePresenter import ResidualOrIntrusivePresenter
from ..util import imgrender, imgrender_phase, node_coords_fromjson, node_del_fixed
from ..views.AddContextView import AddContextView
from ..views.CalibrateModelSelectView import CalibrateModelSelectView
from ..views.DatafilePreviewView import DatafilePreviewView
from ..views.MCMCProgressView import MCMCProgressView
from ..views.ModelView import ModelView
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.RemoveContextView import RemoveContextView
from ..views.RemoveStratigraphicRelationshipView import RemoveStratigraphicRelationshipView
from ..views.ResidualCheckPopupView import ResidualCheckPopupView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .BaseFramePresenter import BaseFramePresenter
from .ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter


class ModelPresenter(BaseFramePresenter):
    """Presenter for the main model tab

    @todo - re-order methods and properties to be logical (rather than in order of porting)
    @todo - reduce duplciation inside methods
    @todo - abstract logic into the Model where possible / appropraite
    @todo - improve view-presenter separation of concerns once behving as intended.
    @todo - split out image canvas areas into their own mini presenters to simplify this file / abstract it away? They could potentially share (most of) an implementation.
    @todo - move imports which are only required in one function into the function to avoid polluting namespaces?
    """

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

        self.node: str = "no node"
        """The currently selected node for right click operations on the stratigraphic graph
        
        @todo - make Optional[str] instead of using "no node"?
        @todo - rename self.selected_node?
        """

        self.edge_nodes: List[Any] = []
        """Used during testmenu (right click menu) options similar to self.node
        
        @todo document it's use, and refactor into a more appropraite name or location"""

        self.comb_nodes: List[Any] = []
        """Used during testmenu (right click menu) options similar to self.node

        Context equality only?
        
        @todo document it's use, and refactor into a more appropraite name or location"""

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
        self.display_data_var = "hidden"  # @todo - this could just be a bool.
        self.view.bind_data_button(lambda: self.on_data_button())

        # Bind the callback for activating the testmenu
        self.view.bind_testmenu_commands(lambda event: self.on_testmenu(event))

        # Bind mouse & keyboard events
        self.view.bind_littlecanvas_callback("<Button-3>", lambda event: self.pre_click(event))
        self.view.bind_littlecanvas_events(
            lambda event: self.on_wheel(event), lambda event: self.move_from(event), lambda event: self.move_to(event)
        )
        self.view.bind_littlecanvas2_events(
            lambda event: self.on_wheel2(event),
            lambda event: self.move_from2(event),
            lambda event: self.move_to2(event),
        )

        # Update the view to reflect the current staet of the model
        self.update_view()

    def update_view(self) -> None:
        """Update the view to reflect the current state of the model

        @todo Ensure that this method updates each UI element for the current model (if there is one). I.e. both graphs, + 3 tables + data loaded drop down + presenter properties like the selected node."""
        # Get the actual model
        # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            # @todo if there is no model, reset everything to empty
            return

        # Update each presenter property
        # @todo - should phase_true be updated?

        # Update the view
        # @todo

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
            # self.bind("<Configure>", self.resize) @todo
            self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
            self.view.bind_littlecanvas_callback("<Button-3>", self.pre_click)

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

        Formerly StartPage.load_mcmc
        """
        # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
        model_model: Model = self.model.get_current_model()
        if model_model is None:  # @todo - should never occur.
            return
        # Create the popup presenter and view
        popup_presenter = MCMCProgressPresenter(self.mediator, MCMCProgressView(self.view), model_model)
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()
        # Run the calibration
        # @todo - gracefully handle errors during calibration
        popup_presenter.run()
        # Close the popup (formerly .cleanup)
        popup_presenter.close_view()
        # Change to the DatingResults tab (assuming the calibration ran successfully @todo)
        self.mediator.switch_presenter("DatingResults")

        # @todo -
        # f = dir(self)
        # self.f_2 = [var for var in f if ("__" or "grid" or "get") not in var]
        # self.newvars = [var for var in self.f_2 if var not in self.f_1]

        # @todo - esnure the presenter is destroyed (for all popup presenters, it should be unless tk is holding references.)

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
        """wraps chronograph render so we can assign a variable when runing the func using a button

        @todo - migrate some of this code into the Model.
        """
        # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
        model_model: Model = self.model.get_current_model()
        if model_model is None:  # @todo - should never occur.
            return

        # @todo - move this condition into a model function.
        if model_model.phase_rels is None or model_model.phase_df is None or model_model.date_df is None:
            # @todo - abstract this into a view
            tk.messagebox.showinfo("Error", "You haven't loaded in all the data required for a chronological graph")
            return
        if model_model.load_check:
            # @todo - abstract this tk call somewhere?
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, are you sure you want to write over it? You can copy this model in the file menu if you want to consider multiple models",
            )
            if answer == "yes":
                print("@todo - finish chronograph_render_wrap")
                self.refresh_4_new_model()  # @todo self.controller, proj_dir, load=False)
                model_model.load_check = False
                # self.littlecanvas2.delete("all")
                model_model.chrono_dag = self.chronograph_render()
                # startpage = self.controller.get_page("StartPage")
                # startpage.CONT_TYPE = self.popup3.CONT_TYPE
                # startpage.prev_phase = self.popup3.prev_phase
                # startpage.post_phase = self.popup3.post_phase
                # startpage.phi_ref = self.popup3.phi_ref
                # startpage.context_no_unordered = self.popup3.context_no_unordered
                # startpage.graphcopy = self.popup3.graphcopy
                # startpage.node_del_tracker = self.popup3.node_del_tracker
            else:
                pass  # @todo - do somethign in this case? Query intended behaviour.
        else:
            print("@todo - finish chronograph_render_wrap")
            # self.littlecanvas2.delete("all")
            model_model.chrono_dag = self.chronograph_render()
            # startpage = self.controller.get_page("StartPage")
            # startpage.CONT_TYPE = self.popup3.CONT_TYPE
            # startpage.prev_phase = self.popup3.prev_phase
            # startpage.post_phase = self.popup3.post_phase
            # startpage.phi_ref = self.popup3.phi_ref
            # startpage.context_no_unordered = self.popup3.context_no_unordered
            # startpage.graphcopy = self.popup3.graphcopy
            # startpage.node_del_tracker = self.popup3.node_del_tracker

    def chronograph_render(self) -> Optional[nx.DiGraph]:
        """initiates residual checking function then renders the graph when thats done

        Returns a copy of the produced chronological graph (if requirements met and no error occurs?).

        @todo - move this into models.Model and make it just self-assign rather than return?

        """

        # @todo - rename model it's confusing + make model_model this presenters' main model object (with some other way to get out of it?)
        model_model: Model = self.model.get_current_model()
        if model_model is None:  # @todo - should never occur.
            return

        # If the chronograph has not already been rendered/loaded for the current state of the model, render it.
        if not model_model.load_check:
            model_model.load_check = True
            # Check for residuals
            self.resid_check()
            # Render the chronological graph
            model_model.chrono_image = model_model.render_chrono_png(
                self.view.littlecanvas2.winfo_width(),
                self.view.littlecanvas2.winfo_height(),
            )  # @todo - get the view width/height cleaner
            # If the render succeeded
            if model_model.chrono_image is not None:
                # Try and update the view
                try:
                    # Update the view including rebinding events which may have been removed
                    self.view.update_littlecanvas2(model_model.chrono_image)
                    self.view.bind_littlecanvas2_callback("<Configure>", self.on_resize_2)
                    self.show_image2()
                except (RuntimeError, TypeError, NameError):
                    # If any error enountered, make sure to mark the graph as not actually rendered.
                    model_model.load_check = False
            else:
                pass  # @todo - should this also set model_model.load_check = False?
        # @todo - return the actual graph produced
        print("@todo - chronograph_render needs to return the actual graph object")
        # return self.popup3.graphcopy @todo
        return None

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
            # self.popup3 = pagetwo.popup4 # @todo - equiv
            # Wait for teh popup to be closed
            self.view.wait_window(popup_presenter.view)  # @todo - abstract this somewhere?
        else:
            # If not, show the residual check presenter, formerly popupWindow3
            # @todo - store a handle to this popup?, formerly self.popup3?
            popup_presenter = ResidualCheckPopupPresenter(self.mediator, ResidualCheckPopupView(self.view), self.model)
            popup_presenter.view.deiconify()
            popup_presenter.view.lift()  # @todo - not sure these are neccesary
            self.view.wait_window(popup_presenter.view)  # @todo - abstract this somewhere?

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
                    # Update the view and any keybindings
                    self.view.update_littlecanvas(model_model.strat_image)
                    # self.bind("<Configure>", self.resize) @todo
                    self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
                    self.view.bind_littlecanvas_callback("<Button-3>", self.pre_click)

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
                # self.bind("<Configure>", self.resize) @todo
                self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
                self.view.bind_littlecanvas_callback("<Button-3>", self.pre_click)
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
        # Store a flag marking this as being enabled. Should this be model data? @todo
        self.phase_true = 1

        # Render the strat graph in pahse mode, if there is one to render, updating the model and view
        model_model: Model = self.model.get_current_model()
        if model_model.strat_graph is not None:
            model_model.strat_image = imgrender_phase(model_model.strat_graph)
            # Update the rendered image in the canvas
            self.view.update_littlecanvas(model_model.strat_image)
            # self.bind("<Configure>", self.resize) @todo
            self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
            self.view.bind_littlecanvas_callback("<Button-3>", self.pre_click)

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

        @todo - rename
        """

        # Hide the right click menu
        self.view.testmenu.place_forget()  # @todo move into a method on the view
        testmenu_value = self.view.get_testmenu_selection()
        # Depending on the option selected from the right click menu, act accordingly.
        if testmenu_value == "Delete context":
            self.testmenu_delete_context()
        elif testmenu_value == "Add new contexts":
            self.testmenu_add_new_contexts()
        # checks if any nodes are in edge node to see if we want to add/delete a context
        elif len(self.edge_nodes) == 1:
            if testmenu_value == "Delete stratigraphic relationship with " + str(self.edge_nodes[0]):
                self.testmenu_delete_strat_with()
            elif testmenu_value == ("Place " + str(self.edge_nodes[0]) + " Above"):
                self.testmenu_place_above()
        elif testmenu_value == "Delete stratigraphic relationship":
            self.testmenu_delete_stratigraphic_prep()
        elif len(self.comb_nodes) == 1 and testmenu_value == "Equate context with " + str(self.comb_nodes[0]):
            self.testmenu_equate_context_with()
        elif testmenu_value == "Equate context with another":
            self.testmenu_equate_context_prep()
        elif testmenu_value == "Supplementary menu":
            self.testmenu_supplementary_menu()
        elif testmenu_value == "Get supplementary data for this context":
            self.testmenu_get_supplementary_for_context()
        elif testmenu_value == "Place above other context":
            self.testmenu_place_above_prep()

        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        # Update the image in the canvas
        # @todo - abstract this into a method to avoid repetition
        if self.phase_true == 1:
            model_model.strat_image = imgrender_phase(model_model.strat_graph)
        else:
            model_model.strat_image = imgrender(
                model_model.strat_graph,
                self.view.littlecanvas.winfo_width(),
                self.view.littlecanvas.winfo_height(),
            )  # @todo - get the view width/height cleaner
        # Should be covered by update_littlecanvas
        self.view.update_littlecanvas(model_model.strat_image)
        self.view.show_image()
        self.view.set_testmenu_selection(
            "Node Action"
        )  # Reset the variable used by the test action. This doesn't appear to actually set the title of the sub-ment
        # Update some bindings.
        self.view.unbind_littlecanvas_callback("<Button-1>")
        self.view.bind_littlecanvas_callback("<Button-1>", self.move_from)  # Shoudl this not be on_left? @todo
        self.view.bind_littlecanvas_callback("<MouseWheel>", self.on_wheel)

    def testmenu_delete_context(self):
        """Callback function from the testmenu for deleting a single context"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        if self.node != "no node":
            if model_model.load_check:
                model_model.load_check = False  # @todo - this should probably be conditional on the askquestion window being closed with yes/no not jsut the window closing
                answer = tk.messagebox.askquestion(
                    "Warning!",
                    "Chronological DAG already loaded, do you want to save this as a new model first? \n\n Click Yes to save as new model and No to overwrite existing model",
                )
                if answer == "yes":
                    self.refresh_4_new_model()  # @todo  self.controller, proj_dir, load=False)
                # self.littlecanvas2.delete("all") # @todo
            model_model.strat_graph = node_del_fixed(model_model.strat_graph, self.node)
            nodedel_reason = self.node_del_popup(self.node)
            model_model.record_deleted_node(self.node, nodedel_reason)
            self.view.append_deleted_node(self.node, nodedel_reason)

    def testmenu_add_new_contexts(self):
        """Callback function from the testmenu for adding contexts"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            if answer == "yes":
                self.refresh_4_new_model()  # @todo self.controller, proj_dir, load=False)
            # self.littlecanvas2.delete("all") # @todo
            model_model.load_check = "not_loaded"

        popup_data = {"value": None}  # @todo - temp. use a proppert object.
        popup_presenter = AddContextPresenter(self.mediator, AddContextView(self.view), popup_data)
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)  # @todo - abstract this somewhere?
        self.node = popup_data["value"]
        model_model.strat_graph.add_node(
            self.node, shape="box", fontsize="30.0", fontname="helvetica", penwidth="1.0"
        )  # @todo - abstract this into the model class

    def edge_render(self) -> str:
        """renders string for deleted edges

        @todo - move this elsewhere / just parametrise it?. Partially refacotred to return rather than set self.temp
        @todo - this does not appear to work as I would have expected. Query intended behaviour. Could likely be much simpler."""
        if len(self.edge_nodes) != 2:
            return  # @todo better error checking
        edges_del = self.edge_nodes
        ednodes = str(edges_del[0]) + " above " + str(edges_del[1])
        temp = []
        temp = str(temp).replace("[", "")
        temp = str(temp).replace("]", "")
        temp = temp + str(ednodes.replace("'", ""))
        return temp

    def testmenu_delete_strat_with(self):
        """Callback function from the testmenu for deleting stratigrahic relationship edges

        @todo - further refactoring?
        @note - order of popup and already loaded check has been changed to match"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        self.edge_nodes = np.append(self.edge_nodes, self.node)
        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            if answer == "yes":
                self.refresh_4_new_model()  # @todo self.controller, proj_dir, load=False)
            # self.littlecanvas2.delete("all") # @todo
            model_model.load_check = False
        # Open a popup to provide a reason for deleting the edge
        # @todo - use the same labelling as provided in edge_render?
        reason = self.edge_del_popup(self.edge_nodes[0], self.edge_nodes[1])

        # Try and remove the edge one way, if it fails try the other. Could be simpler @todo
        # @todo refactor this into a method on the models.Model
        try:
            model_model.strat_graph.remove_edge(self.edge_nodes[0], self.edge_nodes[1])
            model_model.record_deleted_edge(self.edge_nodes[0], self.edge_nodes[1], reason)
            self.view.append_deleted_edge(self.edge_render(), reason)
        except (KeyError, nx.exception.NetworkXError):
            try:
                model_model.strat_graph.remove_edge(self.edge_nodes[1], self.edge_nodes[0])
                model_model.record_deleted_edge(self.edge_nodes[0], self.edge_nodes[1], reason)
                self.view.append_deleted_edge(self.edge_render(), reason)
            except (KeyError, nx.exception.NetworkXError):
                tk.messagebox.showinfo("Error", "An edge doesnt exist between those nodes")

        self.view.remove_testmenu_entry("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
        self.edge_nodes = []

    def testmenu_place_above(self):
        """Callback function from the testmenu for adding stratigrahic relationship"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            if answer == "yes":
                self.refresh_4_new_model()  # @todo self.controller, proj_dir, load=False)
        # self.littlecanvas2.delete("all") @todo
        model_model.load_check = False
        self.edge_nodes = np.append(self.edge_nodes, self.node)
        self.addedge(self.edge_nodes)
        self.view.remove_testmenu_entry("Place " + str(self.edge_nodes[0]) + " Above")
        self.edge_nodes = []

    def testmenu_delete_stratigraphic_prep(self):
        """Callback function from the testmenu for deleting stratigraphic relationships, adding an option to the menu when a node was selected."""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        if len(self.edge_nodes) == 1:
            self.view.remove_testmenu_entry("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
            self.edge_nodes = []
        self.edge_nodes = np.append(self.edge_nodes, self.node)  # @todo shouldn't need to use np.append ever?
        self.view.append_testmenu_entry(
            "Delete stratigraphic relationship with " + str(self.edge_nodes[0])
        )  # @todo use fstrings rather than explicit casting

    def testmenu_equate_context_with(self):
        """Callback function from the testmenu to equate two contexts (when one has already been selected)"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            print(f"@todo - answer ({answer}) not used in this case.")  # @todo
        self.comb_nodes = np.append(self.comb_nodes, self.node)
        strat_graph_temp = nx.contracted_nodes(model_model.strat_graph, self.comb_nodes[0], self.comb_nodes[1])
        x_nod = list(strat_graph_temp)
        newnode = str(self.comb_nodes[0]) + " = " + str(self.comb_nodes[1])
        y_nod = [newnode if i == self.comb_nodes[0] else i for i in x_nod]
        mapping = dict(zip(x_nod, y_nod))
        strat_graph_temp = nx.relabel_nodes(strat_graph_temp, mapping)
        try:
            self.graph_check = nx.transitive_reduction(
                strat_graph_temp
            )  # @todo - this assigns but never uses it. double check
            model_model.strat_graph = strat_graph_temp
        except Exception as e:
            if e.__class__.__name__ == "NetworkXError":  # @todo improve
                tk.messagebox.showinfo("Error!", "This creates a cycle so you cannot equate these contexts")
        self.view.remove_testmenu_entry("Equate context with " + str(self.comb_nodes[0]))
        self.comb_nodes = []

    def testmenu_equate_context_prep(self):
        """Callback function from the testmenu which sets up menu to equate context for when user picks next node"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if len(self.comb_nodes) == 1:
            self.view.remove_testmenu_entry("Equate context with " + str(self.comb_nodes[0]))
        self.comb_nodes = np.append(self.comb_nodes, self.node)
        self.view.append_testmenu_entry("Equate context with " + str(self.comb_nodes[0]))

    def testmenu_supplementary_menu(self):
        """Callback function from the testmenu for users to provide additional supplementary data

        I.e. launches what was formerly popupWindow2

        @todo - implement this (or remove it for now). Non functional in polychron 0.1. https://github.com/bryonymoody/PolyChron/issues/69
        """
        pass

    def testmenu_get_supplementary_for_context(self):
        """Callback function from the testmenu to show supplementary data for the selected context/node"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        stratinfo = self.stratfunc(self.node)
        metadict2 = {}
        metadict = model_model.strat_graph.nodes()[str(self.node)]
        metadict2["Contexts above"] = [stratinfo[0]]
        metadict2["Contexts below"] = [stratinfo[1]]
        meta1 = pd.DataFrame.from_dict(metadict, orient="index")
        meta2 = pd.DataFrame.from_dict(metadict2, orient="index")
        meta = pd.concat([meta1, meta2])
        meta = meta.loc["Determination":"Contexts below"]
        meta.columns = ["Data"]
        if meta.loc["Determination"][0] != "None":
            meta.loc["Determination"][0] = (
                str(meta.loc["Determination"][0][0]) + " +- " + str(meta.loc["Determination"][0][1]) + " Carbon BP"
            )
        self.view.update_supplementary_data_table(self.node, meta)

    def testmenu_place_above_prep(self):
        """Callback function from the testmenu which sets up for placing one context above another"""
        # Get the Model object
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        if len(self.edge_nodes) == 1:
            self.view.remove_testmenu_entry("Place " + str(self.edge_nodes[0]) + " Above")
            self.edge_nodes = []
        self.edge_nodes = np.append(self.edge_nodes, self.node)
        self.view.append_testmenu_entry("Place " + str(self.edge_nodes[0]) + " Above")

    def refresh_4_new_model(self):
        """@todo"""
        print("@todo implement refresh_4_new_model")
        # extra_top = load_Window.new_model(load_Window(MAIN_FRAME), proj_dir, load)
        # self.wait_window(extra_top)
        # # self.save_state_1()

    def pre_click(self, *args):
        """makes test menu appear and removes any previous test menu

        formerly StartMenu.preClick"""
        try:
            self.testmenu.place_forget()
            self.on_right()
        except Exception:
            self.on_right()

    def on_left(self, *args):
        """hides menu when left clicking

        Formerly StartMenu.onLeft"""
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
        x_scal, y_scal = self.view.show_testmenu(has_image)
        # If the model has a stratigraphic image presented, check if a node has been right clicked on and store in a member variable
        if model_model.strat_image is not None and x_scal is not None and y_scal is not None:
            self.node = self.nodecheck(x_scal, y_scal)

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

        self.update_view()

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

        self.update_view()

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

    def on_resize(self, event):
        """resizes image on canvas

        Formerly StartPage.resize

        @todo rename
        @todo - don't re-open from disk, maintain an unzoomed copy in the model?
        """
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return

        # Re-open the image inside the Model
        model_model.reopen_strat_image()
        # Update the image in the view
        if model_model.strat_image is not None:
            self.view.update_littlecanvas_image_only(model_model.strat_image, event)

    def on_resize_2(self, event):
        """resizes image on canvas2

        Formerly StartPage.resize2

        @todo rename
        @todo - don't re-open from disk, maintain an unzoomed copy in the model?
        """
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        # Re-open the image inside the Model
        model_model.reopen_chrono_image()
        if model_model.chrono_image is not None:
            # Update the image in the view
            self.view.update_littlecanvas2_image_only(model_model.chrono_image, event)

    def move_from(self, event):
        """Remembers previous coordinates for scrolling with the mouse

        Formerly StartPage.move_from
        @todo - this is leaking tkinter into the presenter. Abstract this away a little?
        """
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if model_model.strat_image is not None:
            self.view.littlecanvas.scan_mark(event.x, event.y)  # @todo tkinter in presenter

    def move_to(self, event):
        """Drag (move) canvas to the new position

        Formerly StartPage.move_to
        @todo - this is leaking tkinter into the presenter. Abstract this away a little?
        """
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if model_model.strat_image is not None:
            self.view.littlecanvas.scan_dragto(event.x, event.y, gain=1)  # @todo tkinter in presenter
            self.view.show_image()

    def move_from2(self, event):
        """Remembers previous coordinates for scrolling with the mouse

        Formerly StartPage.move_from2
        @todo - this is leaking tkinter into the presenter. Abstract this away a little?
        """
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if model_model.chrono_image is not None:
            self.view.littlecanvas2.scan_mark(event.x, event.y)  # @todo tkinter in presenter

    def move_to2(self, event):
        """Drag (move) canvas to the new position

        Formerly StartPage.move_to2
        @todo - this is leaking tkinter into the presenter. Abstract this away a little?
        """
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if model_model.chrono_image is not None:
            self.view.littlecanvas2.scan_dragto(event.x, event.y, gain=1)  # @todo tkinter in presenter
            self.view.show_image2()

    def on_wheel(self, event):
        """Zoom with mouse wheel for the stratigraphic image canvas

        Formerly StartPage.wheel

        @todo refactor to use view methods rather than directly accessing view members and leaking tkinter"""
        self.view.wheel(event)

    def on_wheel2(self, event):
        """Zoom with mouse wheel for the chronological image canvas

        Formerly StartPage.wheel2

        @todo refactor to use view methods rather than directly accessing view members and leaking tkinter"""
        self.view.wheel2(event)

    def addedge(self, edgevec):
        """adds an edge relationship (edgevec) to graph and rerenders the graph

        Formerly StartPage.addedge
        @todo partially refactor into a method on models.model
        @todo renaming etc"""
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        # global node_df, phase_true
        x_1 = edgevec[0]
        x_2 = edgevec[1]
        model_model.strat_graph.add_edge(x_1, x_2, arrowhead="none")
        strat_graph_check = nx.transitive_reduction(model_model.strat_graph)
        if model_model.strat_graph.edges() != strat_graph_check.edges():
            model_model.strat_graph.remove_edge(x_1, x_2)
            tk.messagebox.showerror(
                "Redundant relationship",
                "That stratigraphic relationship is already implied by other relationships in the graph",
            )
        if self.phase_true == 1:
            model_model.strat_image = imgrender_phase(model_model.strat_graph)
        else:
            model_model.strat_image = imgrender(
                model_model.strat_graph,
                self.view.littlecanvas.winfo_width(),
                self.view.littlecanvas.winfo_height(),
            )  # @todo - get the view width/height cleaner
        self.view.update_littlecanvas(model_model.strat_image)

    def stratfunc(self, node):
        """obtains strat relationships for node

        Formerly StartPage.stratfunc
        @todo partially refactor into a method on models.model
        @todo - using np.append to extend a set?
        @todo renaming etc"""
        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        rellist = list(nx.line_graph(model_model.strat_graph))
        above = ()
        below = ()
        for i in enumerate(rellist):
            if str(node) in rellist[i[0]]:
                if str(node) == rellist[i[0]][0]:
                    below = np.append(below, rellist[i[0]][1])
                elif str(node) == rellist[i[0]][1]:
                    above = np.append(above, rellist[i[0]][0])
        if len(above) == 0:
            str1 = ""
        else:
            str1 = above[0]
            for i in above[1:]:
                str1 = str1 + ", " + i
        if len(below) == 0:
            str2 = ""
        else:
            str2 = below[0]
            for j in below[1:]:
                str2 = str2 + ", " + j
        return [str1, str2]

    def nodecheck(self, x_current, y_current) -> str:
        """returns the node that corresponds to the mouse cooridinates

        Formerly StartPage.nodecheck
        @todo - refactor. This is directly accessing view data (imscale)
        """

        node_inside = "no node"  # @todo use None instead?

        model_model: Model = self.model.get_current_model()
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return node_inside

        workdir = (
            pathlib.Path(tempfile.gettempdir()) / "polychron" / "temp"
        )  # @todo actually do this in the model folder?

        if self.phase_true == 1:
            (graph,) = pydot.graph_from_dot_file(workdir / "fi_new.txt")
            node_df_con = node_coords_fromjson(graph)
        else:
            node_df_con = node_coords_fromjson(model_model.strat_graph)
        node_df = node_df_con[0]

        xmax, ymax = node_df_con[1]
        # forms a dataframe from the dicitonary of coords
        x, y = model_model.strat_image.size
        cavx = x * self.view.imscale
        cany = y * self.view.imscale
        xscale = (x_current) * (xmax) / cavx
        yscale = (cany - y_current) * (ymax) / cany
        for n_ind in range(node_df.shape[0]):
            if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
            ):
                node_inside = node_df.iloc[n_ind].name
                # self.graph[node_inside] @todo - statement does nothing?
        return node_inside

    def node_del_popup(self, context_name: str) -> Optional[str]:
        """Open a popup window for the user to provide input on deleting a node, returning the value

        This blocks users interacting with the main window until the popup is closed

        Formerly StartPage.node_del_popup

        @todo refactor this to just mutate the model directly."""

        # @todo propper model object?
        data = {
            "context": context_name,
            "reason": None,
        }
        # Create the popup window, formerly popupWindow5
        popup_presenter = RemoveContextPresenter(self.mediator, RemoveContextView(self.view), data)
        # self.canvas["state"] = "disabled" # @todo
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)  # @todo - abstract this somewhere?
        # self.canvas["state"] = "normal" # @todo
        return data["reason"]

    def edge_del_popup(self, context_a: str, context_b: str) -> Optional[str]:
        """Open a popup window for the user to provide input on deleting an edge, returning the reason provided

        This blocks users interacting with the main window until the popup is closed

        Formerly StartPage.edge_del_popup

        @todo refactor this to just mutate the model directly."""

        # @todo actual data class / object.
        data = {
            "context_a": context_a,
            "context_b": context_b,
            "reason": None,
        }
        # Create the popup window, formerly popupWindow6
        popup_presenter = RemoveStratigraphicRelationshipPresenter(
            self.mediator, RemoveStratigraphicRelationshipView(self.view), data
        )
        # self.canvas["state"] = "disabled" # @todo
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)  # @todo - abstract this somewhere?
        # self.canvas["state"] = "normal" # @todo
        return data["reason"]
