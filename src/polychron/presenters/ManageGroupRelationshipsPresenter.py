from __future__ import annotations

import copy
from typing import Any

import networkx as nx
import numpy as np
from networkx.drawing.nx_pydot import write_dot

from ..interfaces import Mediator
from ..models.Model import Model
from ..util import chrono_edge_add, chrono_edge_remov, node_del_fixed, remove_invalid_attributes_networkx_lt_3_4
from ..views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from .PopupPresenter import PopupPresenter


class ManageGroupRelationshipsPresenter(PopupPresenter[ManageGroupRelationshipsView, Model]):
    """Presenter for managing Residual vs Intrusive contexts"""

    def __init__(self, mediator: Mediator, view: ManageGroupRelationshipsView, model: Model) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        self.prev_dict = {}
        """A dictionary containing the group relationship type between a group and the previous group"""

        self.post_dict = {}
        """A dictionary containing the group relationship type between a group and the next group"""

        self.group_relationship_dict = {}
        """A dictionary of the group relationship type, indexed by `(group, prev_group)`"""

        self.dag = copy.deepcopy(self.model.stratigraphic_dag)
        """The DAG being modified throughout the group management process. Initially a copy of the stratigraphic_dag, which is mutated to become the chronological_dag"""

        self.removed_nodes_tracker = []
        """A list of nodes which have been removed from the copy of the stratigraphic dag due to an absence of node or phase information"""

        # Create a box per group in the model, based on the provided group relationships
        group_labels = self.model.get_unique_groups()
        self.view.create_phase_boxes(group_labels)

        # populate some local members from model inputs.
        # get all the phases for each node
        node_groups = nx.get_node_attributes(self.dag, "Group")
        # get all dates for each notes
        node_determinations = nx.get_node_attributes(self.dag, "Determination")
        # all contexts
        nodes = self.dag.nodes()

        # checks for each context and if there isn't node or phase info, it deletes it
        for i in nodes:
            if node_groups[i] is None:
                self.removed_nodes_tracker.append(i)
            elif node_determinations[i] == [None, None]:
                self.removed_nodes_tracker.append(i)
        for j in self.removed_nodes_tracker:
            self.dag = node_del_fixed(self.dag, j)

        # sets up a context list
        self.context_no_unordered = [
            x for x in list(self.model.stratigraphic_dag.nodes()) if x not in self.removed_nodes_tracker
        ]
        """An unordered list of contexts in the modified stratigraphic dag copy"""

        self.context_types = ["normal" for _ in self.context_no_unordered]
        """The type of each context in the modified dag. normal, residual or intrusive"""

        # checks if contexts are residual or intrusive and if we want to keep them or exclude from modelling
        for i in self.model.residual_contexts:
            if self.model.residual_context_types[i] == "Treat as TPQ":
                self.context_types[np.where(np.array(self.context_no_unordered) == i)[0][0]] = "residual"
            elif self.model.residual_context_types[i] == "Exclude from modelling":
                self.dag = node_del_fixed(self.dag, i)
                self.context_types.pop(np.where(np.array(self.context_no_unordered) == i)[0][0])
                self.context_no_unordered.remove(i)

        for j in self.model.intrusive_contexts:
            if self.model.intrusive_context_types[j] == "Treat as TAQ":
                self.context_types[np.where(np.array(self.context_no_unordered) == j)[0][0]] = "intrusive"
            elif self.model.intrusive_context_types[j] == "Exclude from modelling":
                self.dag = node_del_fixed(self.dag, j)
                self.context_types.pop(np.where(np.array(self.context_no_unordered) == j)[0][0])
                self.context_no_unordered.remove(j)

        # Cleanup the chronological dag removing excess edges
        self.step_1 = chrono_edge_remov(self.dag)

        # Update the table
        self.view.update_relationships_table(self.model.group_relationships_dict())

        # Bind buttons
        self.view.bind_confirm_button(lambda: self.get_coords())
        self.view.bind_render_button(lambda: self.full_chronograph_func())
        self.view.bind_change_button(lambda: self.on_back())

        # Bind canvas events for dragging boxes around
        self.view.bind_phase_box_on_move(self.on_move)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass

    def on_move(self, event: Any) -> None:
        """on move event for dragging boxes around

        Formerly `popupWindow3.on_move`
        """
        component = event.widget
        locx, locy = component.winfo_x(), component.winfo_y()  # top left coords for where the object is
        w, h = self.view.canvas.winfo_width(), self.view.canvas.winfo_height()  # width of master canvas
        mx, my = component.winfo_width(), component.winfo_height()  # width of boxes
        xpos = (locx + event.x) - (15)
        ypos = (locy + event.y) - int(my / 2)
        if (
            xpos >= 0
            and ypos >= 0
            and w - abs(xpos) >= 0
            and xpos <= (w - mx)
            and h - abs(ypos) >= 0
            and ypos <= (h - my)
        ):
            component.place(x=xpos, y=ypos)

    def on_back(self) -> None:
        """Callback for when the back button is pressed (when it exists), which updates the view to show the first phase

        Formerly popupWindow3.back_func"""
        self.view.on_back()
        self.view.update_relationships_table(self.model.group_relationships_dict())

    def get_coords(self) -> None:
        """Triggered when confirming the provided layout of phase relationships.

        Builds prev_dict, post_dict and group_relationship_dict based on the relative positions of the phase boxes before updating the view to the 2nd stage.

        Formerly `popupWindow3.get_coords`

        Todo:
            - How should exactly equal vertical alignment be handled? Should the sort be y and x?

        """
        # Get the coords and dimensions for each group box label
        group_box_xywh = self.view.get_group_box_properties()

        # Reset member variables (i.e. result arrays)
        self.prev_dict = {}
        self.post_dict = {}
        self.group_relationship_dict: dict[tuple[str, str], str] = {}

        # If there is more than one group
        if len(group_box_xywh) > 1:
            # Sort the group box properties by the vertical midpoint
            sorted_group_xywh = sorted(
                group_box_xywh.items(), key=lambda item: item[1][1] + (0.5 * item[1][3]), reverse=True
            )
            # Use the lower-most box as a reference
            ref_group, ref_xywh = sorted_group_xywh[0]
            # ref_w = ref_xywh[2]
            ref_h = ref_xywh[3]
            # Store the reference vertical midpoint
            ref_y = ref_xywh[1] + (0.5 * ref_h)

            # Set some thresholds and offsets
            OVERLAP_PERCENT = 0.25
            ABUTTING_THRESHOLD = 15

            # Prepare a dictionary for the new x y for each box, initialised with the reference box's location
            new_xy = {ref_group: (ref_xywh[0:2])}

            # Iterate the y-sorted groups in pairs, computing the relative relationship between them and building a new set of box xy positions
            for prev_idx, (prev, curr) in enumerate(zip(sorted_group_xywh, sorted_group_xywh[1:])):
                # Unpack the xywh for the prev and current group box
                prev_group, (prev_x, prev_y, prev_w, prev_h) = prev
                curr_group, (curr_x, curr_y, curr_w, curr_h) = curr
                # Get the distance from the right hand edge of the previous box, to the left hand edge of the current box to detect the overlap type
                prev_right = prev_x + prev_w
                curr_left = curr_x
                x_delta = curr_left - prev_right

                # If the difference in x less than the negative threshold, it is an overlap
                if x_delta < -ABUTTING_THRESHOLD:
                    # Compute the new x position for the next node
                    rel = "overlap"
                    new_x = prev_right - (OVERLAP_PERCENT * prev_w)
                    self.prev_dict[curr_group] = rel
                    self.post_dict[prev_group] = rel
                    self.group_relationship_dict[(curr_group, prev_group)] = rel
                # Otherwise, if the difference is greater than the positive threshold, it's a gap
                elif x_delta > +ABUTTING_THRESHOLD:
                    rel = "gap"
                    new_x = prev_right + (OVERLAP_PERCENT * prev_w)
                    self.prev_dict[curr_group] = rel
                    self.post_dict[prev_group] = rel
                    self.group_relationship_dict[(curr_group, prev_group)] = rel
                # Otherwise, it's abutting
                else:
                    rel = "abutting"
                    new_x = prev_right
                    self.prev_dict[curr_group] = rel
                    self.post_dict[prev_group] = rel
                    self.group_relationship_dict[(curr_group, prev_group)] = rel

                # centre of top box + (half and scale factor) times height
                new_y = ref_y - (0.5 + prev_idx + 1) * ref_h
                new_xy[curr_group] = (new_x, new_y)

            # Update the box coordinates
            self.view.update_box_coords(new_xy)

        # Update the view
        self.view.on_confirm()
        self.view.update_relationships_table(self.group_relationship_dict)

    def full_chronograph_func(self) -> None:
        """renders the chronological graph and forms the prev_phase and past_phase vectors

        Formerly `popupWindow3.full_chronograph_func`
        """

        workdir = self.model.get_working_directory()

        prev_group = ["start"]
        post_group = []
        group_list = self.step_1[2]
        if len(self.step_1[0][1][3]) != 0:
            self.dag, phi_ref, self.null_phases = chrono_edge_add(
                self.dag,
                self.step_1[0],
                self.step_1[1],
                self.group_relationship_dict,
                self.model.group_relationships_list(),
                self.post_dict,
                self.prev_dict,
            )
            post_group.append(self.post_dict[phi_ref[0]])
            # adds the phase relationships to prev_group and post_group
            for i in range(1, len(phi_ref) - 1):
                prev_group.append(self.prev_dict[phi_ref[i]])
                post_group.append(self.post_dict[phi_ref[i]])
            prev_group.append(self.prev_dict[phi_ref[len(phi_ref) - 1]])
        else:
            phi_ref = list(self.step_1[0][1][2])
        post_group.append("end")
        del_groups = [i for i in phi_ref if i not in group_list]
        ref_list = []
        for i in del_groups:
            ref = np.where(np.array(phi_ref) == i)[0][0]
            ref_list.append(ref)
        # deletes missing context references from phi_ref
        for index in sorted(ref_list, reverse=True):
            del phi_ref[index]
        # change to new phase rels
        for i in ref_list:
            prev_group[i] = "gap"
            post_group[i] = "gap"
        self.dag.graph["graph"] = {"splines": "ortho"}
        atribs = nx.get_node_attributes(self.dag, "Group")
        nodes = self.dag.nodes()
        edge_add = []
        edge_remove = []
        for i, j in enumerate(self.context_no_unordered):
            ####find paths in that phase

            phase = atribs[j]
            root = [i for i in nodes if f"b_{phase}" in i][0]
            leaf = [i for i in nodes if f"a_{phase}" in i][0]
            all_paths = []
            all_paths.extend(nx.all_simple_paths(self.dag, source=root, target=leaf))

            if self.context_types[i] == "residual":
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.dag.edges():
                    if k[0] == j:
                        edge_remove.append((k[0], k[1]))
            elif self.context_types[i] == "intrusive":
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.dag.edges():
                    if k[1] == j:
                        edge_remove.append((k[0], k[1]))
        for a in edge_add:
            self.dag.add_edge(a[0], a[1], arrowhead="none")
        for b in edge_remove:
            self.dag.remove_edge(b[0], b[1])

        # Ensure the graph is compatible with networkx < 3.4 nx_pydot
        self.dag = remove_invalid_attributes_networkx_lt_3_4(self.dag)

        write_dot(self.dag, workdir / "fi_new_chrono")

        # write output variables into the Model once it is confirmed.
        self.model.context_types = self.context_types
        self.model.prev_group = prev_group
        self.model.post_group = post_group
        self.model.phi_ref = phi_ref
        self.model.context_no_unordered = self.context_no_unordered
        self.model.chronological_dag = self.dag
        self.model.removed_nodes_tracker = self.removed_nodes_tracker
        # Close the popup window
        self.close_window()

    def close_window(self, reason: str | None = None) -> None:
        # Close the view
        self.view.destroy()
