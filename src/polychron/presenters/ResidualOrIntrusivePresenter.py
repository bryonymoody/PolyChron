from __future__ import annotations

import copy
from typing import Any, Literal

import networkx as nx
from PIL import ImageTk

from ..interfaces import Mediator
from ..models.Model import Model
from ..presenters.ManageIntrusiveOrResidualContextsPresenter import ManageIntrusiveOrResidualContextsPresenter
from ..util import node_coords_fromjson
from ..views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .PopupPresenter import PopupPresenter


class ResidualOrIntrusivePresenter(PopupPresenter[ResidualOrIntrusiveView, Model], Mediator):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, the mediator should change to the DatingResults tab
    """

    def __init__(self, mediator: Mediator, view: ResidualOrIntrusiveView, model: Model) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        self.mode: Literal["resid", "intru"] | None = None
        """The currently selected mode, either None, "resid" or "intru"
        
        Formerly PageTwo.modevariable
        """

        # Bind enabling residual mode
        self.view.bind_residual_mode_button(lambda: self.on_resid_button())

        # Bind enabling intrusive
        self.view.bind_intrusive_mode_button(lambda: self.on_intru_button())

        # Bind the proceed button, which should open another popup for the next stage
        self.view.bind_proceed_button(self.on_proceed)

        # Bind canvas/graph interaction
        self.view.bind_graphcanvas_events(self.on_wheel2, self.resid_node_click, self.move_from2, self.move_to2)

        if self.model.stratigraphic_dag is not None:
            self.load_graph()  # this mutates the model
            self.view.imscale2 = min(921 / self.view.image2.size[0], 702 / self.view.image2.size[1])
            self.view.graphcanvas.scale("all", 0, 0, self.view.delta2, self.view.delta2)  # rescale all canvas objects
            self.view.show_image2()
        # Ensure the canvas is up to date
        self.view.graphcanvas.update()

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        """Update the view to reflect the current state of the model/presenter.

        Parts of this formerly in:

        - `StartPage.mode_set`
        - `StartPage.__init__`
        """
        # Update button colours depending ont the mode.
        if self.mode == "resid":
            self.view.set_residual_mode_button_background("orange")
            self.view.set_intrusive_mode_button_background("light gray")
        elif self.mode == "intru":
            self.view.set_residual_mode_button_background("light gray")
            self.view.set_intrusive_mode_button_background("lightblue")
        else:
            self.view.set_residual_mode_button_background("light gray")
            self.view.set_intrusive_mode_button_background("light gray")

        self.view.set_intru_label_text(self.model.intrusive_contexts)
        self.view.set_resid_label_text(self.model.residual_contexts)

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
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)

    def move_from2(self, event: Any) -> None:
        """Remembers previous coordinates for scrolling with the mouse

        Formerly `PageTwo.move_from2`
        """
        if self.model is None:
            return
        if self.view.image2 is not None:
            self.view.graphcanvas.scan_mark(event.x, event.y)

    def move_to2(self, event: Any) -> None:
        """Drag (move) canvas to the new position

        Formerly `PageTwo.move_to2`
        """
        if self.view.image2 is not None:
            self.view.graphcanvas.scan_dragto(event.x, event.y, gain=1)
            self.view.show_image2()

    def on_wheel2(self, event: Any) -> None:
        """Zoom with mouse wheel for the chronological image canvas

        Formerly `PageTwo.wheel2`
        """
        self.view.wheel2(event)

    def resid_node_click(self, event: Any) -> None:
        """Gets node that you're clicking on and sets it as the right colour depending on if it's residual or intrusive

        Formerly `PageTwo.resid_node_click`
        """
        cursorx2 = int(self.view.graphcanvas.winfo_pointerx() - self.view.graphcanvas.winfo_rootx())
        cursory2 = int(self.view.graphcanvas.winfo_pointery() - self.view.graphcanvas.winfo_rooty())
        x_scal = cursorx2 + self.view.transx2
        y_scal = cursory2 + self.view.transy2
        node = self.nodecheck(x_scal, y_scal)
        outline = nx.get_node_attributes(self.model.resid_or_intru_dag, "color")
        # changes colour of the node outline to represent: intrustive (green), residual (orange) or none (black)
        if (node in self.model.residual_contexts) and (self.mode != "intru"):
            self.model.residual_contexts.remove(node)
            outline[node] = "black"
        elif (node in self.model.residual_contexts) and (self.mode == "intru"):
            self.model.residual_contexts.remove(node)
            outline[node] = "blue"
            self.model.intrusive_contexts.append(node)
        elif (node in self.model.intrusive_contexts) and (self.mode != "resid"):
            self.model.intrusive_contexts.remove(node)
            outline[node] = "black"
        elif (node in self.model.intrusive_contexts) and (self.mode == "resid"):
            self.model.intrusive_contexts.remove(node)
            self.model.residual_contexts.append(node)
            outline[node] = "orange"
        elif (self.mode == "resid") and (node not in self.model.residual_contexts):
            self.model.residual_contexts.append(node)
            outline[node] = "orange"
        elif self.mode == "intru" and (node not in self.model.intrusive_contexts):
            self.model.intrusive_contexts.append(node)
            outline[node] = "blue"

        # Update the list of intrusive and residual contexts in-place.
        self.view.set_intru_label_text(self.model.intrusive_contexts)
        self.view.set_resid_label_text(self.model.residual_contexts)

        # updates the node outline colour
        nx.set_node_attributes(self.model.resid_or_intru_dag, outline, "color")

        # re render the stratigraphic graph
        self.model.render_resid_or_intru_dag()

        # Update the image in the view
        if self.model.resid_or_intru_image is not None:
            self.view.update_littlecanvas2_image_only(self.model.resid_or_intru_image)

        # return the node which was clicked on
        return node

    def nodecheck(self, x_current: int, y_current: int) -> str:
        """returns the node that corresponds to the mouse cooridinates

        Formerly `PageTwo.nodecheck`
        """
        node_inside = "no node"

        if self.model is None:
            return node_inside

        if self.model.resid_or_intru_dag is not None:
            # gets node coordinates from the graph
            node_df_con = node_coords_fromjson(self.model.resid_or_intru_dag)
            # forms a dataframe from the dicitonary of coords
            node_df = node_df_con[0]
            xmax, ymax = node_df_con[1]
            # scales the coordinates using the canvas and image size
            x, y = self.view.image2.size
            cavx = x * self.view.imscale2
            cany = y * self.view.imscale2
            xscale = (x_current) * (xmax) / cavx
            yscale = (cany - y_current) * (ymax) / cany
            # gets current node colours
            outline = nx.get_node_attributes(self.model.resid_or_intru_dag, "color")
            for n_ind in range(node_df.shape[0]):
                if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                    node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
                ):
                    node_inside = node_df.iloc[n_ind].name
                    nx.set_node_attributes(self.model.resid_or_intru_dag, outline, "color")
        return node_inside

    def load_graph(self) -> None:
        """Loads graph on results page

        Formerly `PageTwo.load_graph`
        """
        # loads start page so we get get variables from that class
        # startpage = self.controller.get_page('StartPage')
        self.model.resid_or_intru_dag = copy.deepcopy(self.model.stratigraphic_dag)
        datadict = nx.get_node_attributes(self.model.resid_or_intru_dag, "Determination")
        nodes = self.model.resid_or_intru_dag.nodes()
        removed_nodes_tracker = []
        for i in nodes:
            if datadict[i] == [None, None]:
                removed_nodes_tracker.append(i)
        color = nx.get_node_attributes(self.model.resid_or_intru_dag, "color")
        fill = nx.get_node_attributes(self.model.resid_or_intru_dag, "fontcolor")
        for j in removed_nodes_tracker:
            color[j] = "gray"
            fill[j] = "gray"
        nx.set_node_attributes(self.model.resid_or_intru_dag, color, "color")
        nx.set_node_attributes(self.model.resid_or_intru_dag, fill, "fontcolor")

        # render the stratigraphic graph
        self.model.render_resid_or_intru_dag()

        # Update the image in the view
        if self.model.resid_or_intru_image is not None:
            self.view.update_littlecanvas2_image_only(self.model.resid_or_intru_image)

        self.view.icon = ImageTk.PhotoImage(self.view.image2)
        self.view.graphcanvas_img = self.view.graphcanvas.create_image(0, 0, anchor="nw", image=self.view.icon)
        self.view.width2, self.view.height2 = self.view.image2.size
        self.view.imscale2 = 1.0  # scale for the canvaas image
        self.view.delta2 = 1.1  # zoom magnitude
        # .update_idletasks()
        self.view.container = self.view.graphcanvas.create_rectangle(0, 0, self.view.width2, self.view.height2, width=0)
