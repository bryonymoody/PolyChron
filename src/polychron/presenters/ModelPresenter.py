from __future__ import annotations

import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askopenfile
from typing import Any, List

import networkx as nx
import numpy as np
import pandas as pd
import pydot

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..presenters.AddContextPresenter import AddContextPresenter
from ..presenters.CalibrateModelSelectPresenter import CalibrateModelSelectPresenter
from ..presenters.DatafilePreviewPresenter import DatafilePreviewPresenter
from ..presenters.MCMCProgressPresenter import MCMCProgressPresenter
from ..presenters.RemoveContextPresenter import RemoveContextPresenter
from ..presenters.RemoveStratigraphicRelationshipPresenter import RemoveStratigraphicRelationshipPresenter
from ..presenters.ResidualOrIntrusivePresenter import ResidualOrIntrusivePresenter
from ..util import edge_label, get_right_click_binding, imagefunc, node_coords_fromjson, node_del_fixed
from ..views.AddContextView import AddContextView
from ..views.CalibrateModelSelectView import CalibrateModelSelectView
from ..views.DatafilePreviewView import DatafilePreviewView
from ..views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from ..views.MCMCProgressView import MCMCProgressView
from ..views.ModelView import ModelView
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.RemoveContextView import RemoveContextView
from ..views.RemoveStratigraphicRelationshipView import RemoveStratigraphicRelationshipView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .FramePresenter import FramePresenter
from .ManageGroupRelationshipsPresenter import ManageGroupRelationshipsPresenter
from .ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter


class ModelPresenter(FramePresenter[ModelView, ProjectSelection]):
    """Presenter for the main model tab"""

    def __init__(self, mediator: Mediator, view: ModelView, model: ProjectSelection) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Properties
        self.strat_check: bool = False
        """If a strat file has been loaded or not"""

        self.date_check: bool = False
        """If a data file has been loaded or not"""

        self.phase_check: bool = False
        """If a phase file has been loaded or not"""

        self.phase_rel_check: bool = False
        """If a phase_rel file has been loaded or not"""

        self.node: str = "no node"
        """The currently selected node for right click operations on the stratigraphic graph"""

        self.edge_nodes: List[Any] = []
        """Used during testmenu (right click menu) options similar to self.node"""

        self.comb_nodes: List[Any] = []
        """Used during testmenu (right click menu) options similar to self.node

        Context equality only?"""

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.mediator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.mediator.switch_presenter("DatingResults"))

        # Build file/view/tool menus with callbacks
        self.view.build_file_menu(
            [
                None,
                ("Load stratigraphic diagram file (.dot)", lambda: self.open_strat_dot_file()),
                ("Load stratigraphic relationship file (.csv)", lambda: self.open_strat_csv_file()),
                ("Load scientific dating file (.csv)", lambda: self.open_scientific_dating_file()),
                ("Load context grouping file (.csv)", lambda: self.open_context_grouping_file()),
                ("Load group relationship file (.csv)", lambda: self.open_group_relationship_file()),
                ("Load context equalities file (.csv)", lambda: self.open_context_equalities_file()),
                ("Load new project", lambda: self.load_project()),
                ("Load existing model", lambda: self.load_existing_model()),
                ("Save changes as current model", lambda: self.save_model()),
                ("Save changes as new model", lambda: self.save_as_new_model()),
                None,
                ("Exit", lambda: self.close_application()),
            ]
        )
        self.view.build_view_menu(
            [
                ("Display Stratigraphic diagram in phases", lambda: self.phasing()),
            ]
        )
        self.view.build_tool_menu(
            [
                ("Render chronological graph", lambda: self.chronograph_render_wrap()),
                ("Calibrate model", lambda: self.popup_calibrate_model()),
                ("Calibrate multiple projects from project", lambda: self.popup_calibrate_multiple()),
                # ("Calibrate node delete variations (alpha)",  lambda: self.calibrate_node_delete_variations()), # see https://github.com/bryonymoody/PolyChron/issues/71
                # ("Calibrate important variations (alpha)",  lambda: self.calibrate_important_variations()), # see https://github.com/bryonymoody/PolyChron/issues/72
            ]
        )

        # Bind button clicks
        # Bind the "Data loaded" button callback
        self.display_data_var = "hidden"
        self.view.bind_data_button(lambda: self.on_data_button())

        # Bind the callback for activating the testmenu
        self.view.bind_testmenu_commands(lambda event: self.on_testmenu(event))

        # Bind mouse & keyboard events
        self.view.bind_littlecanvas_callback(get_right_click_binding(), lambda event: self.pre_click(event))
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
        """Update the view to reflect the current state of the model"""
        # Get the actual model
        model_model = self.model.current_model
        if model_model is None:
            return

        # Render the image if possible
        if model_model.stratigraphic_df is not None:
            model_model.render_strat_graph()
            # Update the view
            self.view.update_littlecanvas(model_model.stratigraphic_image)
            # self.bind("<Configure>", self.resize)
            self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
            self.view.bind_littlecanvas_callback(get_right_click_binding(), self.pre_click)

        # Render the chronological graph if possible
        if model_model.chronological_dag is not None:
            model_model.render_chrono_graph()
            if model_model.chronological_image is not None:
                # Update the view
                self.view.update_littlecanvas2(model_model.chronological_image)
                self.view.bind_littlecanvas2_callback("<Configure>", self.on_resize_2)
                self.view.show_image2()

        # Make sure that the check marks are up to date
        if model_model.stratigraphic_df is not None:
            self.strat_check = True
        if model_model.radiocarbon_df is not None:
            self.date_check = True
        if model_model.group_df is not None:
            self.phase_check = True
        if model_model.group_relationship_df is not None:
            self.phase_rel_check = True
        self.check_list_gen()

        # If there are any deleted nodes, update the table of deleted nodes
        if model_model.deleted_nodes is not None and len(model_model.deleted_nodes):
            self.view.set_deleted_nodes(model_model.deleted_nodes)

        # If there are any deleted edges, update the table of deleted edges
        if model_model.deleted_edges is not None and len(model_model.deleted_edges):
            self.view.set_deleted_edges(
                [tuple([edge_label(ctx_a, ctx_b), meta]) for ctx_a, ctx_b, meta in model_model.deleted_edges]
            )

    def get_window_title_suffix(self) -> str | None:
        return f"{self.model.current_project_name} - {self.model.current_model_name}"

    def popup_calibrate_model(self) -> None:
        """Callback function for when Tools -> Calibrate model is selected

        Formerly `StartPage.load_mcmc`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        # Create the popup presenter and view
        popup_presenter = MCMCProgressPresenter(self.mediator, MCMCProgressView(self.view), model_model)
        # Ensure it is visible and on top
        popup_presenter.view.lift()
        # Run the calibration
        popup_presenter.run()
        # Close the popup (formerly .cleanup)
        popup_presenter.close_view()
        # Change to the DatingResults tab
        self.mediator.switch_presenter("DatingResults")

    def popup_calibrate_multiple(self) -> None:
        """Callback function for when Tools -> Calibrate multiple projects from project is selected

        Opens a new popup box allowing the user to select which models from a list to calibrate as a batch.

        Formerly `popupWindow8`
        """
        popup_presenter = CalibrateModelSelectPresenter(self.mediator, CalibrateModelSelectView(self.view), self.model)
        # Ensure it is visible and on top
        popup_presenter.view.lift()

    def chronograph_render_wrap(self) -> None:
        """wraps chronograph render so we can assign a variable when runing the func using a button"""
        model_model = self.model.current_model
        if model_model is None:
            return

        if (
            model_model.group_relationships is None
            or model_model.group_df is None
            or model_model.radiocarbon_df is None
        ):
            tk.messagebox.showinfo("Error", "You haven't loaded in all the data required for a chronological graph")
            return
        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, are you sure you want to write over it? You can copy this model in the file menu if you want to consider multiple models",
            )
            if answer == "yes":
                self.save_as_new_model()
                model_model.load_check = False
                self.view.clear_littlecanvas2()
                model_model.chronological_dag = self.chronograph_render()
            else:
                pass
        else:
            self.view.clear_littlecanvas2()
            model_model.chronological_dag = self.chronograph_render()

    def chronograph_render(self) -> nx.DiGraph | None:
        """initiates residual checking function then renders the graph when thats done

        Returns a copy of the produced chronological graph (if requirements met and no error occurs?).
        """

        model_model = self.model.current_model
        if model_model is None:
            return

        # If the chronograph has not already been rendered/loaded for the current state of the model, render it.
        if not model_model.load_check:
            model_model.load_check = True
            # Check for residuals & update model state when aproved
            self.resid_check()
            # Render the chronological graph, mutating the model
            model_model.render_chrono_graph()
            # If the render succeeded
            if model_model.chronological_image is not None:
                # Try and update the view
                try:
                    # Update the view including rebinding events which may have been removed
                    self.view.update_littlecanvas2(model_model.chronological_image)
                    self.view.bind_littlecanvas2_callback("<Configure>", self.on_resize_2)
                    self.view.show_image2()
                except (RuntimeError, TypeError, NameError):
                    # If any error enountered, make sure to mark the graph as not actually rendered.
                    model_model.load_check = False
            else:
                pass
        return model_model.chronological_dag  # superfluous?

    def resid_check(self) -> None:
        """Loads a text box to check if the user thinks any samples are residual

        When the popupwindows have been closed (correctly) the model will have been updated accordingly.
        """
        if self.model.current_model is not None:
            MsgBox = tk.messagebox.askquestion(
                "Residual and Intrusive Contexts",
                "Do you suspect any of your samples are residual or intrusive?",
                icon="warning",
            )
            if MsgBox == "yes":
                # Create and show the residual or intrusive presenter
                popup_presenter = ResidualOrIntrusivePresenter(
                    self.mediator, ResidualOrIntrusiveView(self.view), self.model.current_model
                )
                popup_presenter.view.lift()
                # Wait for the popup to be closed
                self.view.wait_window(popup_presenter.view)
            else:
                # If not, show the group relation ship management view/presenter, formerly popupWindow3
                popup_presenter = ManageGroupRelationshipsPresenter(
                    self.mediator, ManageGroupRelationshipsView(self.view), self.model.current_model
                )
                popup_presenter.view.lift()
                self.view.wait_window(popup_presenter.view)

    def file_popup(self, df: Any) -> str:
        """For a gien dataframe, preview the data to the user. Returns the users decision"""
        temp_model = {"df": df, "result": "cancel"}
        popup_presenter = DatafilePreviewPresenter(self.mediator, DatafilePreviewView(self.view), temp_model)
        popup_presenter.view.lift()

        # Prevent the view's canvas element from being interacted with?
        self.view.canvas["state"] = "disabled"
        self.view.parent.wait_window(popup_presenter.view)
        self.view.canvas["state"] = "normal"
        return temp_model["result"]

    def open_strat_dot_file(self) -> None:
        """Callback function when File > Load stratigraphic diagram file (.dot) (.csv) is selected, opening a .dot / graphviz file representing the stratigraphic relationships

        Formerly `StartPage.open_file1`
        """
        raise NotImplementedError(
            "open_strat_dot_file is not implemented due to lack of a compaitble GraphViz input file"
        )
        file = askopenfile(mode="r", filetypes=[("DOT Files", "*.dot"), ("Graphviz Files", "*.gv")])
        if file is not None:
            model_model = self.model.current_model

            # Store the path, marking that the most rencent input was a .dot/gv file
            model_model.set_stratigraphic_graphviz_file(file.name)

            # polychron 0.1 does not mark the strat as loaded in this case
            # self.strat_check = True
            # Update the check list
            # self.check_list_gen()

            model_model.stratigraphic_dag = nx.DiGraph(imagefunc(file.name), graph_attr={"splines": "ortho"})

            # Render the image in phases or not
            model_model.render_strat_graph()

            # Clear the list of deleted nodes.
            model_model.deleted_nodes = []
            model_model.deleted_edges = []

            # Update the view and any keybindings
            self.view.update_littlecanvas(model_model.stratigraphic_image)
            # self.bind("<Configure>", self.resize)
            self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
            self.view.bind_littlecanvas_callback(get_right_click_binding(), self.pre_click)
            self.show_image()

    def open_strat_csv_file(self) -> None:
        """Callback function when File > Load stratigraphic relationship file (.csv) is selected, opening a plain text strat file

        Formerly StartPage.open_file2
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])

        if file is not None:
            try:
                model_model = self.model.current_model
                df = pd.read_csv(file, dtype=str)
                load_it = self.file_popup(df)
                if load_it == "load":
                    # update the model with the dataframe, perofrming post processing, producing the graph
                    model_model.set_stratigraphic_df(df)
                    tk.messagebox.showinfo("Success", "Stratigraphic data loaded")
                    # Mark the strat file as loaded
                    self.strat_check = True
                    # Update the check list
                    self.check_list_gen()

                    # Render the image in phases or not
                    model_model.render_strat_graph()

                    # Clear the list of deleted nodes and edges.
                    model_model.deleted_nodes = []
                    model_model.deleted_edges = []

                    # Update the view and any keybindings
                    self.view.update_littlecanvas(model_model.stratigraphic_image)
                    # self.bind("<Configure>", self.resize)
                    self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
                    self.view.bind_littlecanvas_callback(get_right_click_binding(), self.pre_click)

                else:
                    pass
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_scientific_dating_file(self) -> None:
        """Callback function when File > Load scientific dating file (.csv) is selected, opening a scientific dating file

        Formerly StartPage.open_file3
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])

        if file is not None:
            try:
                model_model = self.model.current_model
                df = pd.read_csv(file)
                df = df.applymap(str)
                load_it = self.file_popup(df)
                if load_it == "load":
                    model_model.set_radiocarbon_df(df)
                    self.date_check = True
                    self.check_list_gen()
                    tk.messagebox.showinfo("Success", "Scientific dating data loaded")
                else:
                    pass
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_context_grouping_file(self) -> None:
        """Callback function when File > Load context grouping file (.csv) is selected, opening context grouping / phase file

        Formerly `StartPage.open_file4`
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                model_model = self.model.current_model
                df = pd.read_csv(file)
                df = df.applymap(str)
                load_it = self.file_popup(df)
                if load_it == "load":
                    model_model.set_group_df(df)
                    self.phase_check = True
                    self.check_list_gen()
                    tk.messagebox.showinfo("Success", "Grouping data loaded")
                else:
                    pass
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_group_relationship_file(self) -> None:
        """Callback function when File > Load group relationship file (.csv) is selected, opening a group relationship / phase relationship file

        Formerly StartPage.open_file5
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                model_model = self.model.current_model
                df = pd.read_csv(file)
                group_rels = [(str(df["above"][i]), str(df["below"][i])) for i in range(len(df))]
                load_it = self.file_popup(pd.DataFrame(group_rels, columns=["Younger group", "Older group"]))
                model_model.set_group_relationship_df(df, group_rels)
                if load_it:
                    pass  # 0.1 doesn't check the result / handle the paths differently.
                self.phase_rel_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Group relationships data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_context_equalities_file(self) -> None:
        """Callback function when File > Load context equalities file (.csv) is selected, opening a file providing context equalities (in time)

        Formerly `StartPage.open_file6`
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                model_model = self.model.current_model
                df = pd.read_csv(file)
                df = df.applymap(str)
                # Update the model & post process, updating the graph
                model_model.set_context_equality_df(df)

                # Render the image in phases or not
                model_model.render_strat_graph()
                # Update the view, showing the new image
                self.view.update_littlecanvas(model_model.stratigraphic_image)
                # self.bind("<Configure>", self.resize)
                self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
                self.view.bind_littlecanvas_callback(get_right_click_binding(), self.pre_click)
                tk.messagebox.showinfo("Success", "Equal contexts data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def close_application(self) -> None:
        """Close polychron gracefully via File > Exit"""
        self.mediator.close_window("exit")

    def phasing(self) -> None:
        """Callback function for View > Display Stratigraphic diagram in phases (groups)

        Runs image render function with phases on seperate levels

        Formerly `StartPage.phasing`
        """

        # Render the strat graph in pahse mode, if there is one to render, updating the model and view
        model_model = self.model.current_model
        if model_model is not None:
            # Store a flag marking this as being enabled. Should this be model data?
            model_model.grouped_rendering = True

            if model_model.stratigraphic_dag is not None:
                model_model.render_strat_graph()
                # Update the rendered image in the canvas
                self.view.update_littlecanvas(model_model.stratigraphic_image)
                # self.bind("<Configure>", self.resize)
                self.view.bind_littlecanvas_callback("<Configure>", self.on_resize)
                self.view.bind_littlecanvas_callback(get_right_click_binding(), self.pre_click)

    def on_data_button(self) -> None:
        """Callback for when the "Data Loaded" button is pressed, which toggles the visibility of which required input files have been parsed or not

        Formerly `StartPage.display_data_func`
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
        """

        # Hide the right click menu
        self.view.testmenu.place_forget()
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
        model_model = self.model.current_model
        if model_model is None:
            return
        # Update the image in the canvas
        model_model.render_strat_graph()
        # Should be covered by update_littlecanvas
        self.view.update_littlecanvas(model_model.stratigraphic_image)
        self.view.show_image()
        # Reset the variable used by the test action. This doesn't appear to actually set the title of the sub-menu
        self.view.set_testmenu_selection("Node Action")
        # Update some bindings.
        self.view.unbind_littlecanvas_callback("<Button-1>")
        self.view.bind_littlecanvas_callback("<Button-1>", self.move_from)
        self.view.bind_littlecanvas_callback("<MouseWheel>", self.on_wheel)

    def testmenu_delete_context(self) -> None:
        """Callback function from the testmenu for deleting a single context"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return

        if self.node != "no node":
            if model_model.load_check:
                model_model.load_check = False
                answer = tk.messagebox.askquestion(
                    "Warning!",
                    "Chronological DAG already loaded, do you want to save this as a new model first? \n\n Click Yes to save as new model and No to overwrite existing model",
                )
                if answer == "yes":
                    self.save_as_new_model()
                # self.littlecanvas2.delete("all")
            nodedel_reason = self.node_del_popup(self.node)
            if nodedel_reason is None:
                return
            
            model_model.stratigraphic_dag = node_del_fixed(model_model.stratigraphic_dag, self.node)
            model_model.record_deleted_node(self.node, nodedel_reason)
            self.view.append_deleted_node(self.node, nodedel_reason)

    def testmenu_add_new_contexts(self) -> None:
        """Callback function from the testmenu for adding contexts"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return
        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            if answer == "yes":
                self.save_as_new_model()
            # self.littlecanvas2.delete("all")
            model_model.load_check = "not_loaded"

        popup_data = {"value": None}
        popup_presenter = AddContextPresenter(self.mediator, AddContextView(self.view), popup_data)
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)
        self.node = popup_data["value"]
        if popup_data["value"] is not None:
            model_model.stratigraphic_dag.add_node(
                self.node, shape="box", fontsize="30.0", fontname="helvetica", penwidth="1.0"
            )

    def testmenu_delete_strat_with(self) -> None:
        """Callback function from the testmenu for deleting stratigrahic relationship edges"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return

        self.edge_nodes = np.append(self.edge_nodes, self.node)
        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            if answer == "yes":
                self.save_as_new_model()
            # self.littlecanvas2.delete("all")
            model_model.load_check = False

        # Find the correct direction of the selected edge to delete, or error if it does not exist. Use a copy so menu deletion can be matinained
        edge_src = self.edge_nodes[0]
        edge_dst = self.edge_nodes[1]
        # Check in the first direction
        if not model_model.stratigraphic_dag.has_edge(edge_src, edge_dst):
            # If the reverse exists, update the src/dst pair
            if model_model.stratigraphic_dag.has_edge(edge_dst, edge_src):
                edge_src, edge_dst = edge_dst, edge_src  # swap the variables via a tuple swap
            else:
                # If the edge does not exist in either direction, report the error and return.
                tk.messagebox.showinfo(
                    "Error", f"An edge doesnt exist between '{self.edge_nodes[0]}' and '{self.edge_nodes[1]}' nodes"
                )
                # Remove the deleted releationshipo with X entry from the right click menu and reset the edges which have been selected so far
                self.view.remove_testmenu_entry("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
                self.edge_nodes = []
                return

        # If the edge does exist, open a popup to provide a reason for deleting the edge
        reason = self.edge_del_popup(edge_src, edge_dst)

        # Remove the edge, updating the model and the view.
        # This no longer needs to be attempted in either direction, or in a try catch really.
        model_model.stratigraphic_dag.remove_edge(edge_src, edge_dst)
        model_model.record_deleted_edge(edge_src, edge_dst, reason)
        self.view.append_deleted_edge(edge_label(edge_src, edge_dst), reason)

        # Remove the deleted releationshipo with X entry from the right click menu and reset the edges which have been selected so far
        self.view.remove_testmenu_entry("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
        self.edge_nodes = []

    def testmenu_place_above(self) -> None:
        """Callback function from the testmenu for adding stratigrahic relationship"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return

        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            if answer == "yes":
                self.save_as_new_model()
        # self.littlecanvas2.delete("all")
        model_model.load_check = False
        self.edge_nodes = np.append(self.edge_nodes, self.node)
        self.addedge(self.edge_nodes)
        self.view.remove_testmenu_entry("Place " + str(self.edge_nodes[0]) + " Above")
        self.edge_nodes = []

    def testmenu_delete_stratigraphic_prep(self) -> None:
        """Callback function from the testmenu for deleting stratigraphic relationships, adding an option to the menu when a node was selected."""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return

        if len(self.edge_nodes) == 1:
            self.view.remove_testmenu_entry("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
            self.edge_nodes = []
        self.edge_nodes = np.append(self.edge_nodes, self.node)
        self.view.append_testmenu_entry("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))

    def testmenu_equate_context_with(self) -> None:
        """Callback function from the testmenu to equate two contexts (when one has already been selected)"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return

        if model_model.load_check:
            answer = tk.messagebox.askquestion(
                "Warning!",
                "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
            )
            if answer == "yes":
                pass
        self.comb_nodes = np.append(self.comb_nodes, self.node)
        strat_graph_temp = nx.contracted_nodes(model_model.stratigraphic_dag, self.comb_nodes[0], self.comb_nodes[1])
        x_nod = list(strat_graph_temp)
        newnode = str(self.comb_nodes[0]) + " = " + str(self.comb_nodes[1])
        y_nod = [newnode if i == self.comb_nodes[0] else i for i in x_nod]
        mapping = dict(zip(x_nod, y_nod))
        strat_graph_temp = nx.relabel_nodes(strat_graph_temp, mapping)
        try:
            # Check for cycles, updating the model if no cycles occur.
            nx.transitive_reduction(strat_graph_temp)
            model_model.stratigraphic_dag = strat_graph_temp
        except nx.NetworkXError:
            tk.messagebox.showinfo("Error!", "This creates a cycle so you cannot equate these contexts")
        except Exception:
            pass
        self.view.remove_testmenu_entry("Equate context with " + str(self.comb_nodes[0]))
        self.comb_nodes = []

    def testmenu_equate_context_prep(self) -> None:
        """Callback function from the testmenu which sets up menu to equate context for when user picks next node"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return
        if len(self.comb_nodes) == 1:
            self.view.remove_testmenu_entry("Equate context with " + str(self.comb_nodes[0]))
        self.comb_nodes = np.append(self.comb_nodes, self.node)
        self.view.append_testmenu_entry("Equate context with " + str(self.comb_nodes[0]))

    def testmenu_supplementary_menu(self) -> None:
        """Callback function from the testmenu for users to provide additional supplementary data

        I.e. launches what was formerly `popupWindow2`

        Note:
            This is not currently implemented. See https://github.com/bryonymoody/PolyChron/issues/69
        """
        raise NotImplementedError(
            "testmenu_supplementary_menu has not been implemented. See https://github.com/bryonymoody/PolyChron/issues/69"
        )

    def testmenu_get_supplementary_for_context(self) -> None:
        """Callback function from the testmenu to show supplementary data for the selected context/node"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return

        # If no node was selected, do nothing.
        if self.node == "no node":
            return

        stratinfo = self.stratfunc(self.node)
        metadict2 = {}
        metadict = model_model.stratigraphic_dag.nodes()[str(self.node)]
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

    def testmenu_place_above_prep(self) -> None:
        """Callback function from the testmenu which sets up for placing one context above another"""
        # Get the Model object
        model_model = self.model.current_model
        if model_model is None:
            return

        if len(self.edge_nodes) == 1:
            self.view.remove_testmenu_entry("Place " + str(self.edge_nodes[0]) + " Above")
            self.edge_nodes = []
        self.edge_nodes = np.append(self.edge_nodes, self.node)
        self.view.append_testmenu_entry("Place " + str(self.edge_nodes[0]) + " Above")

    def pre_click(self, *args) -> None:
        """makes test menu appear and removes any previous test menu

        formerly StartMenu.preClick"""
        try:
            self.view.testmenu.place_forget()
            self.on_right()
        except Exception:
            self.on_right()

    def on_left(self, *args) -> None:
        """hides menu when left clicking

        Formerly StartMenu.onLeft"""
        try:
            self.view.testmenu.place_forget()
        except Exception:
            pass

    def on_right(self, *args) -> None:
        """Makes the test menu appear after right click

        Formerly StartPage.onRight"""
        # Unbind and rebind on_left.
        self.view.unbind_littlecanvas_callback("<Button-1>")
        self.view.bind_littlecanvas_callback("<Button-1>", self.on_left)
        # Show the right click menu
        model_model = self.model.current_model
        has_image = model_model.stratigraphic_image is not None
        x_scal, y_scal = self.view.show_testmenu(has_image)
        # If the model has a stratigraphic image presented, check if a node has been right clicked on and store in a member variable
        if model_model.stratigraphic_image is not None and x_scal is not None and y_scal is not None:
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
        popup_presenter.view.lift()

        # Wait for the popup to be closed
        popup_presenter.view.wait_window()
        # Update the view once the presenter is closed
        self.update_view()

    def load_existing_model(self) -> None:
        """Open a popup dialog to load an existing model from the current project (althoug possible to go back?)

        Formerly a call to load_Window(MAIN_FRAME, proj_dir)
        """
        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.mediator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Set the models' next project to the current project
        self.model.next_project_name = self.model.current_project_name
        # Switch to the model select page
        popup_presenter.switch_presenter("model_select")
        # Ensure it is visible and on top
        popup_presenter.view.lift()
        # Wait for the popup to be closed
        popup_presenter.view.wait_window()
        # Update the view once the presenter is closed
        self.update_view()

    def save_model(self) -> None:
        """Save the current state of the model in-place

        Formerly StartPage.save_state_1"""
        if model := self.model.current_model:
            try:
                model.save()
            except Exception as e:
                tk.messagebox.showerror("Error", f"File not saved: {e}")
            else:
                # State saving success if no exceptions occurred
                tk.messagebox.showinfo("Success", "Your model has been saved")

    def save_as_new_model(self) -> None:
        """Save the current state of the model, as a new model (with a new name) initially in the same project (although possible to put in a new project).
        Switches to the "new" model for any future changes.

        Formerly `StartPage.refresh_4_new_model`
        """

        # Store the old project and model names, to check if the model was changed or not.
        old_project_name = self.model.current_project_name
        old_model_name = self.model.current_model_name

        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.mediator, ProjectSelectProcessPopupView(self.view), self.model
        )

        # Specify the initial project to the current one
        self.model.next_project_name = old_project_name
        # Specify this should be a copy not a fresh model
        self.model.using_save_as = True

        # Switch to the model select page
        popup_presenter.switch_presenter("model_create")
        # Ensure it is visible and on top
        popup_presenter.view.lift()

        # Wait for the popup window to be closed before saving the new model
        self.view.wait_window(popup_presenter.view)

        # Get the new model
        model_model = self.model.current_model
        if model_model is None:
            return

        # If the current project or model name have changed, save the model
        if self.model.current_project_name != old_project_name or self.model.current_model_name is not old_model_name:
            # Save the new model
            model_model.save()
            # Update this view
            self.update_view()

    def on_resize(self, event: Any) -> None:
        """resizes image on canvas

        Formerly `StartPage.resize`
        """
        model_model = self.model.current_model
        if model_model is None:
            return

        # Re-open the image inside the Model
        model_model.reopen_stratigraphic_image()
        # Update the image in the view
        if model_model.stratigraphic_image is not None:
            self.view.update_littlecanvas_image_only(model_model.stratigraphic_image, event)

    def on_resize_2(self, event: Any) -> None:
        """resizes image on canvas2

        Formerly `StartPage.resize2`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        # Re-open the image inside the Model
        model_model.reopen_chronological_image()
        if model_model.chronological_image is not None:
            # Update the image in the view
            self.view.update_littlecanvas2_image_only(model_model.chronological_image, event)

    def move_from(self, event: Any) -> None:
        """Remembers previous coordinates for scrolling with the mouse

        Formerly `StartPage.move_from`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        if model_model.stratigraphic_image is not None:
            self.view.littlecanvas.scan_mark(event.x, event.y)

    def move_to(self, event: Any) -> None:
        """Drag (move) canvas to the new position

        Formerly `StartPage.move_to`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        if model_model.stratigraphic_image is not None:
            self.view.littlecanvas.scan_dragto(event.x, event.y, gain=1)
            self.view.show_image()

    def move_from2(self, event: Any) -> None:
        """Remembers previous coordinates for scrolling with the mouse

        Formerly `StartPage.move_from2`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        if model_model.chronological_image is not None:
            self.view.littlecanvas2.scan_mark(event.x, event.y)

    def move_to2(self, event: Any) -> None:
        """Drag (move) canvas to the new position

        Formerly `StartPage.move_to2`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        if model_model.chronological_image is not None:
            self.view.littlecanvas2.scan_dragto(event.x, event.y, gain=1)
            self.view.show_image2()

    def on_wheel(self, event: Any) -> None:
        """Zoom with mouse wheel for the stratigraphic image canvas

        Formerly `StartPage.wheel`
        """
        self.view.wheel(event)

    def on_wheel2(self, event: Any) -> None:
        """Zoom with mouse wheel for the chronological image canvas

        Formerly `StartPage.wheel2`
        """
        self.view.wheel2(event)

    def addedge(self, edgevec: List[str]) -> None:
        """adds an edge relationship (edgevec) to graph and rerenders the graph

        Formerly `StartPage.addedge`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        x_1 = edgevec[0]
        x_2 = edgevec[1]
        model_model.stratigraphic_dag.add_edge(x_1, x_2, arrowhead="none")
        strat_graph_check = nx.transitive_reduction(model_model.stratigraphic_dag)
        if model_model.stratigraphic_dag.edges() != strat_graph_check.edges():
            model_model.stratigraphic_dag.remove_edge(x_1, x_2)
            tk.messagebox.showerror(
                "Redundant relationship",
                "That stratigraphic relationship is already implied by other relationships in the graph",
            )
        model_model.render_strat_graph()
        self.view.update_littlecanvas(model_model.stratigraphic_image)

    def stratfunc(self, node: str) -> None:
        """obtains strat relationships for node

        Formerly `StartPage.stratfunc`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        rellist = list(nx.line_graph(model_model.stratigraphic_dag))
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

    def nodecheck(self, x_current: int, y_current: int) -> str:
        """returns the node that corresponds to the mouse cooridinates

        Formerly StartPage.nodecheck
        """

        node_inside = "no node"

        model_model = self.model.current_model
        if model_model is None:
            return node_inside

        workdir = model_model.get_working_directory()

        if model_model.grouped_rendering:
            (graph,) = pydot.graph_from_dot_file(workdir / "fi_new.txt")
            node_df_con = node_coords_fromjson(graph)
        else:
            node_df_con = node_coords_fromjson(model_model.stratigraphic_dag)
        node_df = node_df_con[0]

        xmax, ymax = node_df_con[1]
        # forms a dataframe from the dicitonary of coords
        x, y = model_model.stratigraphic_image.size
        cavx = x * self.view.imscale
        cany = y * self.view.imscale
        xscale = (x_current) * (xmax) / cavx
        yscale = (cany - y_current) * (ymax) / cany
        for n_ind in range(node_df.shape[0]):
            if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
            ):
                node_inside = node_df.iloc[n_ind].name
        return node_inside

    def node_del_popup(self, context_name: str) -> str | None:
        """Open a popup window for the user to provide input on deleting a node, returning the value

        This blocks users interacting with the main window until the popup is closed

        Formerly `StartPage.node_del_popup`
        """

        data = {
            "context": context_name,
            "reason": None,
        }
        # Create the popup window, formerly popupWindow5
        popup_presenter = RemoveContextPresenter(self.mediator, RemoveContextView(self.view), data)
        self.view.canvas["state"] = "disabled"
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)
        self.view.canvas["state"] = "normal"
        return data["reason"]

    def edge_del_popup(self, context_a: str, context_b: str) -> str | None:
        """Open a popup window for the user to provide input on deleting an edge, returning the reason provided

        This blocks users interacting with the main window until the popup is closed

        Formerly `StartPage.edge_del_popup`
        """

        data = {
            "context_a": context_a,
            "context_b": context_b,
            "reason": None,
        }
        # Create the popup window, formerly popupWindow6
        popup_presenter = RemoveStratigraphicRelationshipPresenter(
            self.mediator, RemoveStratigraphicRelationshipView(self.view), data
        )
        self.view.canvas["state"] = "disabled"
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)
        self.view.canvas["state"] = "normal"
        return data["reason"]
