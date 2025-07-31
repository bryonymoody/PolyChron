from __future__ import annotations

import copy
import math
from typing import TYPE_CHECKING, Any

import networkx as nx
import numpy as np
import pandas as pd

from ..interfaces import Mediator
from ..models.GroupRelationship import GroupRelationship
from ..models.Model import Model
from ..util import chrono_edge_add, chrono_edge_remov, node_del_fixed
from ..views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from .PopupPresenter import PopupPresenter

if TYPE_CHECKING:
    import tkinter as tk


class ManageGroupRelationshipsPresenter(PopupPresenter[ManageGroupRelationshipsView, Model]):
    """Presenter for managing Residual vs Intrusive contexts"""

    # Set some thresholds and offsets
    INITIAL_OVERLAP_FACTOR = 0.25
    ABUTTING_THRESHOLD = 15
    BOX_MAX_HEIGHT = 48

    def __init__(self, mediator: Mediator, view: ManageGroupRelationshipsView, model: Model) -> None:
        """Construct a presenter for managing group relationships.

        Parameters:
            mediator: The mediator for switching windows etc
            view: the ManageGroupRelationshipsView
            model: The `models.Model` to manipulate groups within

        Raises:
            RuntimeError: if the Model contains an invalid set of defined group relationships. Groups must have 1 incoming relationship, 1 outgoing relationship or 1 relationship in each direction and must not form cycles
        """
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        self.prev_dict = {}
        """A dictionary containing the group relationship type between a group and the previous group"""

        self.post_dict = {}
        """A dictionary containing the group relationship type between a group and the next group"""

        self.group_relationship_dict = copy.deepcopy(self.model.group_relationships_dict())
        """A dictionary of the group relationship type, indexed by `(group, prev_group)`"""

        self.dag = copy.deepcopy(self.model.stratigraphic_dag)
        """The DAG being modified throughout the group management process. Initially a copy of the stratigraphic_dag, which is mutated to become the chronological_dag"""

        self.removed_nodes_tracker = []
        """A list of nodes which have been removed from the copy of the stratigraphic dag due to an absence of node or phase information"""

        # Validate the model's group relationship status, so that assumptions can be made within this class, by building a relationship graph.
        self.__group_relationship_dag = nx.DiGraph([rel for rel in self.group_relationship_dict.keys()])
        """A graph of relationships in the graph"""
        # If the graph of group relationships is not acyclic, raise an error
        if not nx.is_directed_acyclic_graph(self.__group_relationship_dag):
            raise RuntimeError("Groups Relationships must for a directed acyclic graph")
        # If any nodes (groups) in the graph have 0 edges, or more than 1 edge in a direction, raise an error.
        for node in self.__group_relationship_dag.nodes():
            if self.__group_relationship_dag.degree(node) == 0:
                raise RuntimeError(f"Groups must have at least one relationship. {node} does not.")
            elif (indegree := self.__group_relationship_dag.in_degree(node)) > 1:
                raise RuntimeError(
                    f"Groups must only be the 'below' group in at most 1 relationship. {node} is in {indegree}"
                )
            elif (outdegree := self.__group_relationship_dag.out_degree(node)) > 1:
                raise RuntimeError(
                    f"Groups must only be the 'above' group in at most 1 relationship. {node} is in {outdegree}"
                )
        # If any groups are not in the graph, an error should be raised
        missing_groups = set(self.model.get_unique_groups()) - set(self.__group_relationship_dag.nodes())
        if len(missing_groups) > 0:
            raise RuntimeError(f"Groups must have at least one relationship. {', '.join(missing_groups)} do not.")

        self._overlap_factor = self.INITIAL_OVERLAP_FACTOR
        """The overlap to use when calculating box widths and post-confirmation placement. Ideally a relative proportion of box widths, but clamped to above the ABUTTING_THRESHOLD"""

        # Create a box per group in the model, based on the provided group relationships
        boxes_to_create = self.compute_box_placement()
        self.view.create_group_boxes(boxes_to_create)

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
        self.view.bind_group_box_mouse_events(
            self.on_box_mouse_press, self.on_box_mouse_move, self.on_box_mouse_release, "fleur"
        )

        self.__group_box_drag_x: float | None = None
        """x coordinate for the start of the current dragging event, in canvas coordinate space?"""

        self.__group_box_drag_y: float | None = None
        """y coordinate for the start of the current dragging event, in canvas coordinate space?"""

        self.__group_box_widget: Any | None = None
        """The tkinter label being dragged.
        Todo: 
            This is a tkinter leak into the presenter, but that's required if the presenter is handling mouse events...
        """

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass

    def compute_box_placement(self) -> dict[str, tuple[float, float, float, float]]:
        """Compute the (initial) location of group boxes for the current model

        Returns:
            A tuple dictionary of tuples (x, y, w, h), keyed by the label.
        """
        relationships = self.group_relationship_dict
        num_groups = len(self.model.get_unique_groups())

        # Get the size of the canvas area
        canvas_width, canvas_height = self.view.get_group_canvas_dimensions()

        # Compute the width for each box, based on the number of boxes, the total width available, and enough room for the gaps to be rendered.
        # As there is an absolute threshold for abutting detection, the actual overlap must be at least the threshold.
        space_per_group = math.floor(canvas_width / num_groups)
        if math.ceil(space_per_group * self._overlap_factor) <= self.ABUTTING_THRESHOLD:
            max_box_width = math.floor(space_per_group - (self.ABUTTING_THRESHOLD + 1))
            self._overlap_factor = ((self.ABUTTING_THRESHOLD + 1) / max_box_width) + 0.01
        box_width = space_per_group / (1 + self._overlap_factor)

        # Compute the height for each box, based on the number of boxes, total height available, and some margin, with an upper limit.
        box_height = (canvas_height - (self.BOX_MAX_HEIGHT)) / num_groups
        box_height = min(self.BOX_MAX_HEIGHT, box_height)

        # Topologically sort the nodes (requires an acyclic graph)
        topo_sorted_groups = list(nx.topological_sort(self.__group_relationship_dag))

        # Sort the dictionary of relationships in order of the topological nodes
        mapping = {element: index for index, element in enumerate(topo_sorted_groups)}
        sorted_relationships = sorted(
            relationships.items(),
            key=lambda item: (mapping.get(item[0][0], float("inf")), mapping.get(item[0][1], float("inf"))),
        )

        # Calculate the coordinates and dimension for each box within the available space, starting with the oldest group at the bottom left, working through the known before-after relationships.
        xywh_per_group = {}

        # Place the oldest group at the bottom left (excluding margin)
        xywh_per_group[topo_sorted_groups[-1]] = (0.0, canvas_height - box_height, box_width, box_height)

        # Iterate the sorted relationships in reverse order, adding a box for each newly encountered group. Groups must only have at most one incoming and at most one outgoing relationship, so this should be fine.
        for (younger, older), relationship in reversed(sorted_relationships):
            # Get the position of the older group which should be known
            older_x, older_y, older_w, _ = xywh_per_group[older]
            older_right_edge = older_x + older_w
            # Calculate the box placement for the current group based on the placement of the the older box and the type of relationship (if known).
            # This will not handle having relationships with multiple groups well.
            if relationship == GroupRelationship.OVERLAP:
                x = older_right_edge - (self._overlap_factor * older_w)
            elif relationship == GroupRelationship.GAP:
                x = older_right_edge + (self._overlap_factor * older_w)
            elif relationship == GroupRelationship.ABUTTING:
                x = older_right_edge
            else:  # None / unknown
                # When relationships are not known, leave enough room for the rendered gap amount (_overlap_factor)
                x = older_right_edge + (self._overlap_factor * older_w)
            # The box should be on the net vertical height compared to the prior group
            y = older_y - box_height
            # Store the x, y, width and height for the box
            xywh_per_group[younger] = x, y, box_width, box_height

        # Adjust placement to be horizontally and vertically centred by adding a margin to each box. This is done in a separate pass to account for overlap, gap,and abutting boxes.

        min_x, max_x = canvas_width, 0
        min_y, max_y = canvas_height, 0
        for x, y, w, h in xywh_per_group.values():
            min_x = min(min_x, x)
            max_x = max(max_x, x + w)
            min_y = min(min_y, y)
            max_y = max(max_y, y + h)

        x_range = max_x - min_x
        y_range = max_y - min_y
        x_margin = (canvas_width - x_range) / 2.0
        y_margin = (canvas_height - y_range) / 2.0

        # Add a margin (subtract in y, as placement started at the bottom but origin is top left) to each box to place in the centre of the area
        for group, (x, y, w, h) in xywh_per_group.items():
            xywh_per_group[group] = (x + x_margin, y - y_margin, w, h)

        # Return the initial locations of the boxes
        return xywh_per_group

    def on_box_mouse_press(self, event: "tk.Event") -> None:
        self.__group_box_drag_x = event.x
        self.__group_box_drag_y = event.y
        self.__group_box_widget = event.widget

    def on_box_mouse_move(self, event: "tk.Event") -> None:
        new_x = self.__group_box_widget.winfo_x() + (event.x - self.__group_box_drag_x)
        new_y = self.__group_box_widget.winfo_y() + (event.y - self.__group_box_drag_y)

        # Do not allow the new x / y to be outside the canvas
        canvas_w, canvas_h = self.view.get_group_canvas_dimensions()

        new_x = max(0, min(new_x, canvas_w - self.__group_box_widget.winfo_width()))
        new_y = max(0, min(new_y, canvas_h - self.__group_box_widget.winfo_height()))

        self.__group_box_widget.place(x=new_x, y=new_y)

    def on_box_mouse_release(self, event: "tk.Event") -> None:
        self.__group_box_drag_x = None
        self.__group_box_drag_y = None
        self.__group_box_widget = None

    def on_back(self) -> None:
        """Callback for when the back button is pressed (when it exists), which updates the view to show the first phase

        Formerly popupWindow3.back_func"""
        self.view.update_relationships_table(self.group_relationship_dict)
        self.view.layout_step_one()
        self.view.bind_group_box_mouse_events(
            self.on_box_mouse_press, self.on_box_mouse_move, self.on_box_mouse_release, "fleur"
        )

    def get_coords(self) -> None:
        """Triggered when confirming the provided layout of phase relationships.

        Builds prev_dict, post_dict and group_relationship_dict based on the relative positions of the phase boxes before updating the view to the 2nd stage.


        Formerly `popupWindow3.get_coords`
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
            ref_y = ref_xywh[1]
            ref_h = ref_xywh[3]

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

                new_prev_right = new_xy[prev_group][0] + prev_w
                # If the difference in x less than the negative threshold, it is an overlap
                if x_delta < -self.ABUTTING_THRESHOLD:
                    # Compute the new x position for the next node
                    rel = GroupRelationship.OVERLAP
                    new_x = new_prev_right - (self._overlap_factor * prev_w)
                    self.prev_dict[curr_group] = rel
                    self.post_dict[prev_group] = rel
                    self.group_relationship_dict[(curr_group, prev_group)] = rel
                # Otherwise, if the difference is greater than the positive threshold, it's a gap
                elif x_delta > +self.ABUTTING_THRESHOLD:
                    rel = GroupRelationship.GAP
                    new_x = new_prev_right + (self._overlap_factor * prev_w)
                    self.prev_dict[curr_group] = rel
                    self.post_dict[prev_group] = rel
                    self.group_relationship_dict[(curr_group, prev_group)] = rel
                # Otherwise, it's abutting
                else:
                    rel = GroupRelationship.ABUTTING
                    new_x = new_prev_right
                    self.prev_dict[curr_group] = rel
                    self.post_dict[prev_group] = rel
                    self.group_relationship_dict[(curr_group, prev_group)] = rel

                # New y value is based on the top edge of the bottom-most box, with the correct number of box heights removed
                new_y = ref_y - ((prev_idx + 1) * ref_h)
                new_xy[curr_group] = (new_x, new_y)

            # Update the box coordinates
            self.view.update_box_coords(new_xy)

        # Disable mouse-interaction with boxes
        self.view.bind_group_box_mouse_events(lambda _: None, lambda _: None, lambda _: None, "")

        # Reverse the order of the group relationship dictionary, so the 0th row of the table matches the top-most relationship
        self.group_relationship_dict = dict(reversed(self.group_relationship_dict.items()))

        # Update the view
        self.view.update_relationships_table(self.group_relationship_dict)
        self.view.layout_step_two()

    def full_chronograph_func(self) -> None:
        """renders the chronological graph and forms the prev_phase and past_phase vectors

        Formerly `popupWindow3.full_chronograph_func`
        """

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
            prev_group[i] = GroupRelationship.GAP
            post_group[i] = GroupRelationship.GAP
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

        # Store the chronological dag
        self.model.chronological_dag = self.dag

        # Update the dataframe of group relationships to match the version from chrono rendering rather than the version from disk
        self.model.group_relationship_df = pd.DataFrame(
            [[above, below, relationship] for (above, below), relationship in self.group_relationship_dict.items()],
            columns=["above", "below", "relationship"],
        )

        # Update other model properties
        self.model.context_types = self.context_types
        self.model.prev_group = prev_group
        self.model.post_group = post_group
        self.model.phi_ref = phi_ref
        self.model.context_no_unordered = self.context_no_unordered
        self.model.removed_nodes_tracker = self.removed_nodes_tracker

        # set the load_check flag indicating the chorological_dag has been rendered
        self.model.load_check = True

        # Close the popup window
        self.close_window()

    def close_window(self, reason: str | None = None) -> None:
        # Close the view
        self.view.destroy()
