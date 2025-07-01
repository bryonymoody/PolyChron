from __future__ import annotations

from tkinter import simpledialog
from typing import Any, List

import matplotlib as plt
import networkx as nx
import numpy as np
from matplotlib.figure import Figure

from ..automated_mcmc_ordering_coupling_copy import HPD_interval
from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..util import node_coords_fromjson, phase_length_finder
from ..views.DatingResultsView import DatingResultsView
from .FramePresenter import FramePresenter


class DatingResultsPresenter(FramePresenter[DatingResultsView, ProjectSelection]):
    """Presenter for the Dating Results page/tab."""

    def __init__(self, mediator: Mediator, view: DatingResultsView, model: ProjectSelection):
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        self.results_list: List[str] = []
        """A list of results to be shown in this view?"""

        self.node = "no node"
        """The currenly selected node for right click operations
        """

        self.phase_len_nodes = []
        """Used during testmenu2 (right click menu) operations, seimilar to self.node
        """

        self.fig = None
        """A handle to a matplotlib figure being presented."""

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.mediator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.mediator.switch_presenter("DatingResults"))

        # Bind button callbacks
        self.view.bind_posterior_densities_button(lambda: self.on_button_posterior_densities())
        self.view.bind_hpd_button(lambda: self.on_button_hpd_button())
        self.view.bind_clear_list_button(lambda: self.on_button_clear_list_button())

        # Build file/view/tool menus with callbacks
        self.view.build_file_menu(
            [
                None,
                ("Save project progress", lambda: self.on_file_save()),
            ]
        )

        # Bind the callback for activiting the rightclick / testmenu2
        self.view.bind_testmenu2_commands(lambda event: self.on_testmenu2(event))

        # Bind canvas events
        self.view.bind_littlecanvas2_events(
            lambda event: self.on_canvas_wheel2(event),
            lambda event: self.on_right(event),
            lambda event: self.on_canvas_move_from2(event),
            lambda event: self.on_canvas_move_to2(event),
        )

        # Update the view to reflect the current staet of the model
        self.update_view()

    def update_view(self) -> None:
        # Ensure content is correct when switching tab
        self.chronograph_render_post()

    def get_window_title_suffix(self) -> str | None:
        if self.model.current_project_name and self.model.current_model_name:
            return f"{self.model.current_project_name} - {self.model.current_model_name}"
        else:
            return None

    def on_file_save(self) -> None:
        """Callback for the File > Save project progress menu command

        Formerly a call to startpage::save_state_1
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        model_model.save()

    def on_button_posterior_densities(self) -> None:
        """Callback for when the "Posterior densities" button is pressed

        Formerly startpage::mcmc_output"""
        self.mcmc_output()

    def on_button_hpd_button(self) -> None:
        """Callback for when the "HPD intervals" button is pressed

        Formerly startpage::get_hpd_interval"""
        self.get_hpd_interval()

    def on_button_clear_list_button(self) -> None:
        """Callback for when the "Clear list" button is pressed

        Formerly clear_results_list"""
        self.clear_results_list()

    def pre_click(self, *args) -> None:
        """makes test menu appear and removes any previous test menu

        formerly PageOne.preClick"""
        try:
            self.view.testmenu2.place_forget()
            self.on_right()
        except Exception:
            self.on_right()

    def on_left(self, *args) -> None:
        """hides menu when left clicking

        Formerly PageOne.onLeft"""
        try:
            self.view.testmenu2.place_forget()
        except Exception:
            pass

    def on_right(self, *args) -> None:
        """Makes the test menu appear after right click

        Formerly PageOne.onRight"""
        # Unbind and rebind on_left.
        self.view.unbind_littlecanvas2_callback("<Button-1>")
        self.view.bind_littlecanvas2_callback("<Button-1>", self.on_left)
        # Show the right click menu
        model_model = self.model.current_model
        has_image = model_model is not None and model_model.chronological_image is not None
        # Show the test menu, returning the coords it was place at?
        x_scal, y_scal = self.view.show_testmenu(has_image)
        # If the model has a chronographic image presented, check if a node has been right clicked on and store in a member variable
        # this was part of `PageOne.chrono_nodes``, but standardised to match the other tab a bit more.
        if has_image and x_scal is not None and y_scal is not None:
            self.node = self.nodecheck(x_scal, y_scal)

    def on_canvas_wheel2(self, event: Any) -> None:
        """Zoom with mouse wheel for the chronological image canvas

        Formerly `PageOne.wheel2`
        """
        self.view.wheel2(event)

    def on_canvas_move_from2(self, event: Any) -> None:
        """Remembers previous coordinates for scrolling with the mouse

        Formerly `PageOne.move_from2`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        if model_model.chronological_image is not None:
            self.view.littlecanvas2.scan_mark(event.x, event.y)

    def on_canvas_move_to2(self, event: Any) -> None:
        """Drag (move) canvas to the new position

        Formerly `PageOne.move_to2`
        """
        model_model = self.model.current_model
        if model_model is None:
            return
        if model_model.chronological_image is not None:
            self.view.littlecanvas2.scan_dragto(event.x, event.y, gain=1)
            self.view.show_image2()

    def chronograph_render_post(self) -> None:
        """Formerly `PageOne.chronograph_render_post`"""
        model_model = self.model.current_model
        if model_model is None:
            return

        if model_model.load_check:
            # Render the chronological graph, mutating the model
            model_model.render_chrono_graph()
            # If the render succeeded
            if model_model.chronological_image is not None:
                # Update the view with the image
                self.view.update_littlecanvas2(model_model.chronological_image)

    def nodecheck(self, x_current: int, y_current: int) -> str:
        """Returns the node that corresponds to the mouse coordinates

        Formerly `PageOne.nodecheck`
        """
        node_inside = "no node"

        model_model = self.model.current_model
        if model_model is None:
            return node_inside

        node_df_con = node_coords_fromjson(model_model.chronological_dag)
        node_df = node_df_con[0]
        xmax, ymax = node_df_con[1]
        # forms a dataframe from the dicitonary of coords
        x, y = model_model.chronological_image.size
        cavx = x * self.view.imscale2
        cany = y * self.view.imscale2
        xscale = (x_current) * (xmax) / cavx
        yscale = (cany - y_current) * (ymax) / cany
        outline = nx.get_node_attributes(model_model.chronological_dag, "color")
        for n_ind in range(node_df.shape[0]):
            if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
            ):
                node_inside = node_df.iloc[n_ind].name
                outline[node_inside] = "red"
                nx.set_node_attributes(model_model.chronological_dag, outline, "color")
        return node_inside

    def clear_results_list(self) -> None:
        """clears nodes from results lists

        Formerly `PageOne.clear_results_list`
        """
        self.results_list = []
        # Clear the right canvas
        self.view.clear_littlecanvas3(id=False)
        # Hide any plots
        self.view.hide_canvas_plt()
        # Clear the table.
        self.view.clear_tree_phases()

    def get_hpd_interval(self) -> None:
        """loads hpd intervals into the results page

        Formerly `PageOne.get_hpd_interval`
        """

        model_model = self.model.current_model
        if model_model is None:
            return

        if len(self.results_list) != 0:
            USER_INP = simpledialog.askstring(
                title="HPD interval percentage",
                prompt="Please input HPD interval percentage. Note, 95% is used as standard \n \n Percentage:",
            )

            if model_model.mcmc_check:
                # Compute new data to present
                lim = np.float64(USER_INP) / 100
                intervals = []
                for i, j in enumerate(list(set(self.results_list))):
                    node = str(j)
                    interval = list(
                        HPD_interval(np.array(model_model.mcmc_data.accept_group_limits[j][1000:]), lim=lim)
                    )
                    # define headings
                    hpd_str = ""
                    refs = [k for k in range(len(interval)) if k % 2]
                    for i in refs:
                        hpd_str = hpd_str + str(np.abs(interval[i - 1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                    # add data to the treeview
                    intervals.append((node, hpd_str))

                # Update the view
                self.view.update_hpd_interval(USER_INP, intervals)

    def on_testmenu2(self, currentevent: Any) -> None:
        """finds nodes in the chronodag on results page

        Formerly PageOn.node_finder
        """

        model_model = self.model.current_model
        if model_model is None:
            return

        # Show the testmenu
        self.view.testmenu2.place_forget()

        testmenu2_value = self.view.get_testmenu2_selection()
        if testmenu2_value == "Add to results list":
            self.testmenu_add_to_results_list()

        if len(self.phase_len_nodes) == 1:
            if testmenu2_value == "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context":
                self.testmenu_get_time_elapsed_between()
            self.view.remove_testmenu2_entry(
                "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context"
            )
            self.phase_len_nodes = []

        if testmenu2_value == "Get time elapsed":
            self.testmenu_get_time_elapsed()

        # Update littlecavas3
        self.view.update_littlecanvas3(self.results_list)

        # Reset the right testmenu selected option
        self.view.set_testmenu2_selection("Add to results list")

    def testmenu_add_to_results_list(self) -> None:
        self.view.clear_littlecanvas3(id=True)
        # ref = np.where(np.array(model_model.mcmc_data.contexts) == self.node)[0][0]
        if self.node != "no node":
            self.results_list.append(self.node)

    def testmenu_get_time_elapsed_between(self) -> None:
        model_model = self.model.current_model
        if model_model is None or not model_model.mcmc_check:
            return

        self.phase_len_nodes = np.append(self.phase_len_nodes, self.node)
        if self.view.canvas_plt is not None:
            self.view.canvas_plt.get_tk_widget().pack_forget()
        # font = {'size': 11}
        # using rc function

        self.fig = Figure()
        # self.fig.rc('font', **font)
        LENGTHS = phase_length_finder(
            self.phase_len_nodes[0], self.phase_len_nodes[1], model_model.mcmc_data.all_group_limits
        )
        plot1 = self.fig.add_subplot(111)
        plot1.hist(LENGTHS, bins="auto", color="#0504aa", rwidth=1, density=True)
        # plot1.xlabel('Time elapsed in calibrated years (cal BP)')
        # plot1.ylabel('Probability density')
        plot1.spines["right"].set_visible(False)
        plot1.spines["top"].set_visible(False)
        # plot1.set_ylim([0, 0.05])
        # plot1.set_xlim([0, 400])
        plot1.title.set_text(
            "Time elapsed between " + str(self.phase_len_nodes[0]) + " and " + str(self.phase_len_nodes[1])
        )
        # self.fig.set_tight_layout(True)
        self.view.show_canvas_plot(self.fig)
        # show hpd intervals
        interval = list(HPD_interval(np.array(LENGTHS[1000:])))
        intervals = []
        hpd_str = ""
        refs = [k for k in range(len(interval)) if k % 2]
        for i in refs:
            hpd_str = hpd_str + str(np.abs(interval[i - 1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
        intervals.append((self.phase_len_nodes[0], self.phase_len_nodes[1], hpd_str))
        self.view.update_hpd_interval_3col(intervals)

    def testmenu_get_time_elapsed(self) -> None:
        """When the "get time elasped" option has been selected in the right click menu:
        - Remove any existing elabsed_between options
        - Add a new get time elapsed option.
        """
        if len(self.phase_len_nodes) == 1:
            self.view.remove_testmenu2_entry(
                "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context"
            )
            self.phase_len_nodes = []
        self.phase_len_nodes = np.append(self.phase_len_nodes, self.node)
        self.view.append_testmenu2_entry(
            "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context"
        )

    def mcmc_output(self) -> None:
        """loads posterior density plots into the graph

        Formerly PageOne.mcmc_output"""
        model_model = self.model.current_model
        if model_model is None:
            return

        if model_model.mcmc_check:
            if self.view.canvas_plt is not None:
                self.view.canvas_plt.get_tk_widget().pack_forget()
            if self.view.toolbar is not None:
                self.view.toolbar.destroy()

            fig = Figure(figsize=(8, min(30, len(self.results_list) * 3)), dpi=100)
            for i, j in enumerate(self.results_list):
                # must be single digit number.
                n = min(len(self.results_list), 10)
                plt.rcParams["text.usetex"]

                plot_index = int(str(n) + str(1) + str(i + 1))
                plot1 = fig.add_subplot(plot_index)
                plot1.hist(
                    model_model.mcmc_data.accept_group_limits[j],
                    bins="auto",
                    color="#0504aa",
                    alpha=0.7,
                    rwidth=1,
                    density=True,
                )
                plot1.spines["right"].set_visible(False)
                plot1.spines["top"].set_visible(False)
                fig.gca().invert_xaxis()
                plot1.set_ylim([0, 0.02])
                nodes = list(nx.topological_sort(model_model.chronological_dag))
                uplim = nodes[0]
                lowlim = nodes[-1]
                min_plot = min(model_model.mcmc_data.accept_group_limits[uplim])
                max_plot = max(model_model.mcmc_data.accept_group_limits[lowlim])
                plot1.set_xlim(min_plot, max_plot)
                node = str(j)
                if "a_" in node or "b_" in node:
                    if "a_" in node:
                        node = node.replace("a_", r"\alpha_{")
                    if "b_" in node:
                        node = node.replace("b_", r"\beta_{")
                    if "=" in node:
                        node = node.replace("=", "} = ")
                    plot1.title.set_text(r"Group boundary " + r"$" + node + "}$")
                else:
                    plot1.title.set_text(r"Context " + r"$" + node + "$")  # "}$")

            fig.set_tight_layout(True)
            self.view.show_canvas_plot_with_toolbar(fig)
