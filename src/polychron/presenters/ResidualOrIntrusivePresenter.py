import copy
import pathlib
import tempfile
import tkinter as tk  # @todo - refactor into view,  this should not be imported into this file
from tkinter import ttk  # @todo - refactor into view,  this should not be imported into this file
from typing import Any, Literal, Optional

import networkx as nx
from PIL import Image, ImageTk

from ..interfaces import Mediator
from ..models.Model import Model
from ..presenters.ManageIntrusiveOrResidualContextsPresenter import ManageIntrusiveOrResidualContextsPresenter
from ..util import imgrender, imgrender_phase, node_coords_fromjson
from ..views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .BasePopupPresenter import BasePopupPresenter


# @todo - this needs to be closable by child popups, may need Mediator changes (or just in mediater.close call the parents mediator close based on the reason?)
class ResidualOrIntrusivePresenter(BasePopupPresenter, Mediator):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, the mediator should change to the DatingResults tab
    """

    def __init__(self, mediator: Mediator, view: ResidualOrIntrusiveView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        self.mode: Optional[Literal["resid", "intru"]] = None
        """The currently selected mode, either None, "resid" or "intru"
        
        Formerly PageTwo.modevariable

        @todo Enum rather than Literal?"""

        # @todo preesnter variables that might need to move?
        self.intru_list = []
        self.resid_list = []

        # Bind enabling residual mode
        self.view.bind_residual_mode_button(lambda: self.on_resid_button())

        # Bind enabling intrusive
        self.view.bind_intrusive_mode_button(lambda: self.on_intru_button())

        # Bind the proceed button, which should open another popup for the next stage
        self.view.bind_proceed_button(self.on_proceed)

        # Bind canvas/graph interaction. @todo lambdas?
        self.view.bind_graphcanvas_events(self.on_wheel2, self.resid_node_click, self.move_from2, self.move_to2)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        """Update the view to reflect the current state of the model/presenter.

        Parts of this formerly in:

        - StartPage.mode_set
        - StartPage.__init__
        """
        # Update button colours depending ont the mode.
        if self.mode == "resid":
            self.view.set_residual_mode_button_background("orange")
            self.view.set_intrusive_mode_button_background("light gray")
        elif self.mode == "intru":
            self.view.set_residual_mode_button_background("light gray")
            self.view.set_intrusive_mode_button_background("lightgreen")
        else:
            self.view.set_residual_mode_button_background("light gray")
            self.view.set_intrusive_mode_button_background("light gray")

        # @todo - this could belong to a presenter sspecific model?
        # If the model includes a rendered strat graph
        if self.model.strat_graph is not None:
            self.model.resid_or_intru_strat_graph = self.load_graph()
            self.view.imscale2 = min(921 / self.view.image.size[0], 702 / self.view.image.size[1])
            self.view.graphcanvas.scale("all", 0, 0, self.view.delta2, self.view.delta2)  # rescale all canvas objects
            self.view.show_image2()
        # Ensure the canvas is up to date
        self.view.graphcanvas.update()

        # Update lists @todo
        # self.view.set_resid_label_text
        # self.view.set_intru_label_text

    def set_mode(self, mode: Literal["resid", "intru"]) -> None:
        """Set the current mode, and update the view accordingly.

        Formerly part of StartPage.mode_set"""
        self.mode = mode
        self.update_view()

    def on_resid_button(self) -> None:
        """Enable resid mode for user interaction"""
        self.set_mode("resid")
        self.update_view()

    def on_intru_button(self) -> None:
        """Enable intrusive mode for user interaction"""
        self.set_mode("intru")
        self.update_view()

    def on_proceed(self) -> None:
        """When the proceed button is pressed, open the next popup window for managing intrusive or residual contexts

        Formerly PageTwo.popup4_wrapper"""

        popup_presenter = ManageIntrusiveOrResidualContextsPresenter(
            self.mediator, ManageIntrusiveOrResidualContextsView(self.view), self.model
        )
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()  # @todo - not sure these are neccesary
        print("@todo destroy this window?")

    def move_from2(self, event):
        """Remembers previous coordinates for scrolling with the mouse

        Formerly PageTwo.move_from2

        @todo - this is leaking tkinter into the presenter. Abstract this away a little?
        @todo - rename this, doesn't need the 2?
        """
        model_model: Optional[Model] = self.model
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if model_model.strat_image is not None:
            self.view.graphcanvas.scan_mark(event.x, event.y)  # @todo tkinter in presenter

    def move_to2(self, event):
        """Drag (move) canvas to the new position

        Formerly PageTwo.move_to2

        @todo - this is leaking tkinter into the presenter. Abstract this away a little?
        @todo - rename this, doesn't need the 2?
        """
        model_model: Optional[Model] = self.model
        # @todo - this should never occur. Switch to an assert & fix the root cause when switching back from the results tab?
        if model_model is None:
            return
        if model_model.strat_image is not None:
            self.view.graphcanvas.scan_dragto(event.x, event.y, gain=1)  # @todo tkinter in presenter
            self.view.show_image2()

    def on_wheel2(self, event):
        """Zoom with mouse wheel for the chronological image canvas

        Formerly PageTwo.wheel2

        @todo refactor to use view methods rather than directly accessing view members and leaking tkinter
        @todo - rename this, doesn't need the 2?"""
        self.view.wheel2(event)

    def resid_node_click(self, event):
        """Gets node that you're clicking on and sets it as the right colour depending on if it's residual or intrusive

        Formerly PageTwo.resid_node_click

        @todo - rename on_?
        @todo - refactor into a view method + model methods. This is directly accessing view data (imscale)
        @todo - rename some variables.

        """
        if self.model is None:
            return

        # @todo - abstract the bits that require this elsewhere
        workdir = (
            pathlib.Path(tempfile.gettempdir()) / "polychron" / "temp"
        )  # @todo actually do this in the model folder?

        # @todo - is this update idle tasks needed for correct mouse coords?
        # startpage = self.controller.get_page('StartPage')
        # startpage.update_idletasks()
        cursorx2 = int(self.view.graphcanvas.winfo_pointerx() - self.view.graphcanvas.winfo_rootx())
        cursory2 = int(self.view.graphcanvas.winfo_pointery() - self.view.graphcanvas.winfo_rooty())
        x_scal = cursorx2 + self.view.transx2
        y_scal = cursory2 + self.view.transy2
        node = self.nodecheck(x_scal, y_scal)
        outline = nx.get_node_attributes(self.model.resid_or_intru_strat_graph, "color")
        # changes colour of the node outline to represent: intrustive (green), residual (orange) or none (black)
        if (node in self.resid_list) and (self.mode != "intru"):
            self.resid_list.remove(node)
            outline[node] = "black"
        elif (node in self.resid_list) and (self.mode == "intru"):
            self.resid_list.remove(node)
            outline[node] = "green"
            self.intru_list.append(node)
        elif (node in self.intru_list) and (self.mode != "resid"):
            self.intru_list.remove(node)
            outline[node] = "black"
        elif (node in self.intru_list) and (self.mode == "resid"):
            self.intru_list.remove(node)
            self.resid_list.append(node)
            outline[node] = "orange"
        elif (self.mode == "resid") and (node not in self.resid_list):
            self.resid_list.append(node)
            outline[node] = "orange"
        elif self.mode == "intru" and (node not in self.intru_list):
            self.intru_list.append(node)
            outline[node] = "green"
        self.view.resid_label = ttk.Label(self.view.residcanvas, text=str(self.resid_list).replace("'", "")[1:-1])
        self.view.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.view.intru_label = ttk.Label(self.view.intrucanvas, text=str(self.intru_list).replace("'", "")[1:-1])
        self.view.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        # adds scrollbars to the canvas
        scroll_bar1 = ttk.Scrollbar(self.view.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        scroll_bar2 = ttk.Scrollbar(self.view.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        # updates the node outline colour
        nx.set_node_attributes(self.model.resid_or_intru_strat_graph, outline, "color")
        # @todo - abstract this into a models.Model or simialr
        if self.model.phase_true == 1:
            self.view.image = imgrender_phase(self.model.resid_or_intru_strat_graph)
        else:
            self.view.image = imgrender(
                self.model.resid_or_intru_strat_graph,
                self.view.graphcanvas.winfo_width(),
                self.view.graphcanvas.winfo_height(),
            )
        # rerends the image of the strat DAG with right colours
        self.view.image = Image.open(
            workdir / "fi_new.png"
        )  # @todo - make this a resid or intru specific temporary file, to not overwite the actual one?
        width2, height2 = self.view.image.size
        self.view.container = self.view.graphcanvas.create_rectangle(0, 0, width2, height2, width=0)
        self.view.show_image2()
        self.view.graphcanvas.update()

        return node

    def nodecheck(self, x_current, y_current):
        """returns the node that corresponds to the mouse cooridinates

        Formerly PageTwo.nodecheck
        @todo - refactor. This is directly accessing view data (imscale)
        """
        # global node_df
        # @todo - is this needed?
        # startpage = self.controller.get_page('StartPage')
        # updates canvas to get the right coordinates
        # startpage.update_idletasks()

        node_inside = "no node"  # @todo use None instead?

        if self.model is None:
            return node_inside

        if self.model.resid_or_intru_strat_graph is not None:
            # gets node coordinates from the graph
            node_df_con = node_coords_fromjson(self.model.resid_or_intru_strat_graph)
            # forms a dataframe from the dicitonary of coords
            node_df = node_df_con[0]
            xmax, ymax = node_df_con[1]
            # scales the coordinates using the canvas and image size
            x, y = self.view.image.size
            cavx = x * self.view.imscale2
            cany = y * self.view.imscale2
            xscale = (x_current) * (xmax) / cavx
            yscale = (cany - y_current) * (ymax) / cany
            # gets current node colours
            outline = nx.get_node_attributes(self.model.resid_or_intru_strat_graph, "color")
            for n_ind in range(node_df.shape[0]):
                if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                    node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
                ):
                    node_inside = node_df.iloc[n_ind].name
                    nx.set_node_attributes(self.model.resid_or_intru_strat_graph, outline, "color")
        return node_inside

    def load_graph(self):
        """loads graph on results page

        Formerly PageTwo.load_graph
        @todo refactor this method, a lot can go into models.Model or the view.
        @todo - this doesn't need to return and set the model property directly really."""
        # loads start page so we get get variables from that class
        # startpage = self.controller.get_page('StartPage')
        self.model.resid_or_intru_strat_graph = copy.deepcopy(self.model.strat_graph)
        datadict = nx.get_node_attributes(self.model.resid_or_intru_strat_graph, "Determination")
        nodes = self.model.resid_or_intru_strat_graph.nodes()
        node_del_tracker = []
        for i in nodes:
            if datadict[i] == [None, None]:
                node_del_tracker.append(i)
        color = nx.get_node_attributes(self.model.resid_or_intru_strat_graph, "color")
        fill = nx.get_node_attributes(self.model.resid_or_intru_strat_graph, "fontcolor")
        for j in node_del_tracker:
            color[j] = "gray"
            fill[j] = "gray"
        nx.set_node_attributes(self.model.resid_or_intru_strat_graph, color, "color")
        nx.set_node_attributes(self.model.resid_or_intru_strat_graph, fill, "fontcolor")
        if self.model.phase_true == 1:
            self.view.image = imgrender_phase(self.model.resid_or_intru_strat_graph)
        else:
            self.view.image = imgrender(
                self.model.resid_or_intru_strat_graph,
                self.view.graphcanvas.winfo_width(),
                self.view.graphcanvas.winfo_height(),
            )
        # scale_factor = min(self.view.graphcanvas.winfo_width()/self.view.image_ws.size[0], self.view.graphcanvas.winfo_height()/self.view.image_ws.size[1])
        # self.view.image = self.view.image_ws.resize((int(self.view.image_ws.size[0]*scale_factor), int(self.view.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
        self.view.icon = ImageTk.PhotoImage(self.view.image)
        self.view.graphcanvas_img = self.view.graphcanvas.create_image(0, 0, anchor="nw", image=self.view.icon)
        self.view.width2, self.view.height2 = self.view.image.size
        self.view.imscale2 = 1.0  # scale for the canvaas image
        self.view.delta2 = 1.1  # zoom magnitude
        # startpage.update_idletasks()
        self.view.container = self.view.graphcanvas.create_rectangle(0, 0, self.view.width2, self.view.height2, width=0)
        return self.model.resid_or_intru_strat_graph
