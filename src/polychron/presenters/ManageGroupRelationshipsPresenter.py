import copy
from typing import Any, Optional

import networkx as nx
import numpy as np
import packaging.version
from networkx.drawing.nx_pydot import write_dot

from ..interfaces import Mediator
from ..models.Model import Model
from ..util import chrono_edge_add, chrono_edge_remov, node_del_fixed
from ..views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from .PopupPresenter import PopupPresenter


class ManageGroupRelationshipsPresenter(PopupPresenter[Model]):
    """Presenter for managing Residual vs Intrusive contexsts

    @todo - createa a popup for this and the confirmation version
    """

    def __init__(self, mediator: Mediator, view: ManageGroupRelationshipsView, model: Model) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Create a box per phase in the model, based on the models phase releationships
        # @todo - move some of this into Model or similar.
        phases = []
        for i in self.model.group_relationships:
            phases.append(i[0])
            phases.append(i[1])
        phase_labels = list(set(phases))
        self.view.create_phase_boxes(phase_labels)

        # @todo - these 3 might belong in model? and need better names
        self.prev_dict = {}
        self.post_dict = {}
        self.menudict = {}  # aka phasedict?

        self.graphcopy = copy.deepcopy(self.model.stratigraphic_dag)
        """A copt of the model's stratigraphic graph for mutation in this process. @todo make it another Model member?"""

        # @todo - these probably all bellong in Model? or atleast a copy needs to go into the Model eventually.
        # @todo - need to thinkabotu cases where go back should restore the state of Model in general?
        # self.CONT_TYPE = None
        self.prev_phase = []
        self.post_phase = []
        self.phi_ref = []
        self.context_no_unordered = []

        # populate some local members from model inputs.
        # get all the phases for each node
        phasedict = nx.get_node_attributes(self.graphcopy, "Group")
        # get all dates for each notes
        datadict = nx.get_node_attributes(self.graphcopy, "Determination")
        # all contexts
        nodes = self.graphcopy.nodes()

        # empty node tracker
        self.node_del_tracker = []

        # checks for each context and if there isn't node or phase info, it deletes it
        for i in nodes:
            if phasedict[i] is None:
                self.node_del_tracker.append(i)
            elif datadict[i] == [None, None]:
                self.node_del_tracker.append(i)
        for j in self.node_del_tracker:
            self.graphcopy = node_del_fixed(self.graphcopy, j)

        # sets up a context list
        self.context_no_unordered = [
            x for x in list(self.model.stratigraphic_dag.nodes()) if x not in self.node_del_tracker
        ]
        # set up context types
        self.CONT_TYPE = ["normal" for _ in self.context_no_unordered]

        # checks if contexts are residual or intrusive and if we want to keep them or exclude from modelling
        for i in self.model.resid_list:
            if self.model.resid_dropdowns[i] == "Treat as TPQ":
                self.CONT_TYPE[np.where(np.array(self.context_no_unordered) == i)[0][0]] = "residual"
            elif self.model.resid_dropdowns[i] == "Exclude from modelling":
                self.graphcopy = node_del_fixed(self.graphcopy, i)
                self.CONT_TYPE.pop(np.where(np.array(self.context_no_unordered) == i)[0][0])
                self.context_no_unordered.remove(
                    i
                )  # self.model.resid_list[i]) # @todo - this was incorrect. i is not an index? Should this be an enumerate?

        for j in self.model.intru_list:
            if self.model.intru_dropdowns[j] == "Treat as TAQ":
                self.CONT_TYPE[np.where(np.array(self.context_no_unordered) == j)[0][0]] = "intrusive"
            elif self.model.intru_dropdowns[j] == "Exclude from modelling":
                self.graphcopy = node_del_fixed(self.graphcopy, j)
                self.CONT_TYPE.pop(np.where(np.array(self.context_no_unordered) == j)[0][0])
                self.context_no_unordered.remove(j)
        self.step_1 = chrono_edge_remov(self.graphcopy)

        # Update the table
        # @todo - superfluous if update_view is called here.
        self.view.update_tree_2col(self.model.group_relationships)

        # Bind buttons
        self.view.bind_confirm_button(lambda: self.on_confirm())
        self.view.bind_render_button(lambda: self.full_chronograph_func())
        self.view.bind_change_button(lambda: self.on_back())

        # Bind canvas events for dragging boxes around
        self.view.bind_phase_box_on_move(self.on_move)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass  # @todo

    def on_confirm(self) -> None:
        self.get_coords()
        # @todo trigger changes in the model for the confirm view
        # @todo - simplify, not using a mediator? Separate views might be nicer but would lead to a lot of duplciation?
        # self.mediator.switch_presenter("residual_check_confirm")

    def on_move(self, event: Optional[Any]) -> None:
        """on move event for dragging boxes around

        Formerly popupWindow3.on_move

        @todo remove tkinter calls from this?"""
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
        self.view.update_tree_2col(self.model.group_relationships)

    def get_coords(self) -> None:
        """Triggered when confirming the provided layout of phase relationships.

        Builds prev_dict, post_dict and menudict based on the relative postiions of the phase boxes before updating the view to the 2nd stage.

        Formerly popupWindow3.get_coords

        @todo - finish improved separation of tkinter from presenter"""
        label_dict = self.view.get_phase_boxes()
        y_list = []
        for i in label_dict.keys():
            yx = label_dict[i].winfo_y()
            my = label_dict[i].winfo_height()
            y_cent = yx + 0.5 * my
            y_list.append((i, y_cent))
        y_final = sorted(y_list, key=lambda x: x[1])
        y_final.reverse()
        ref_y = y_final[0][1]
        ref_h = label_dict[y_final[0][0]].winfo_height()
        ref_w = label_dict[y_final[0][0]].winfo_width()
        ref_gap = 0.25 * ref_w
        orig_x = [label_dict[j[0]].winfo_x() for j in y_final[1:]]
        orig_x_prev = [label_dict[j[0]].winfo_x() + ref_w for j in y_final[:-1]]
        self.prev_dict = {}
        self.post_dict = {}
        self.menudict = {}
        for ind, j in enumerate(y_final[1:]):
            x = orig_x[ind]
            x_prev = orig_x_prev[ind]
            if ind < len(y_final) - 1:
                x_prev_curr = label_dict[y_final[ind][0]].winfo_x() + ref_w
                if x - x_prev < -15:
                    x = x_prev_curr - ref_gap
                    self.prev_dict[str(j[0])] = "overlap"
                    self.post_dict[str(y_final[ind][0])] = "overlap"
                    self.menudict[(str(j[0]), str(y_final[ind][0]))] = "overlap"

                elif x - x_prev > 15:
                    x = x_prev_curr + ref_gap
                    self.prev_dict[str(j[0])] = "gap"
                    self.post_dict[str(y_final[ind][0])] = "gap"
                    self.menudict[(str(j[0]), str(y_final[ind][0]))] = "gap"
                else:
                    x = x_prev_curr
                    self.prev_dict[str(j[0])] = "abutting"
                    self.post_dict[str(y_final[ind][0])] = "abutting"
                    self.menudict[(str(j[0]), str(y_final[ind][0]))] = "abutting"
                y = ref_y - (0.5 + ind + 1) * ref_h  # ceter of top box + (half and scalefactor) times height
                label_dict[j[0]].place(x=x, y=y)
                self.view.update_canvas()

        self.view.on_confirm()
        self.view.update_tree_3col(self.menudict)

    def full_chronograph_func(self) -> None:
        """renders the chronological graph and forms the prev_phase and past_phase vectors

        Formerly popupWindow3.full_chronograph_func
        @todo - how much of this could become a Model method?"""

        workdir = self.model.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)  # @todo - shouldnt be neccessary

        self.prev_phase = ["start"]
        self.post_phase = []
        phase_list = self.step_1[2]
        if len(self.step_1[0][1][3]) != 0:
            self.graphcopy, self.phi_ref, self.null_phases = chrono_edge_add(
                self.graphcopy,
                self.step_1[0],
                self.step_1[1],
                self.menudict,
                self.model.group_relationships,
                self.post_dict,
                self.prev_dict,
            )
            self.post_phase.append(self.post_dict[self.phi_ref[0]])
            # adds the phase relationships to prev_phase and post_phase
            for i in range(1, len(self.phi_ref) - 1):
                self.prev_phase.append(self.prev_dict[self.phi_ref[i]])
                self.post_phase.append(self.post_dict[self.phi_ref[i]])
            self.prev_phase.append(self.prev_dict[self.phi_ref[len(self.phi_ref) - 1]])
        else:
            self.phi_ref = list(self.step_1[0][1][2])
        self.post_phase.append("end")
        del_phases = [i for i in self.phi_ref if i not in phase_list]
        ref_list = []
        for i in del_phases:
            ref = np.where(np.array(self.phi_ref) == i)[0][0]
            ref_list.append(ref)
        # deletes missing context references from phi_ref
        for index in sorted(ref_list, reverse=True):
            del self.phi_ref[index]
        # change to new phase rels
        for i in ref_list:
            self.prev_phase[i] = "gap"
            self.post_phase[i] = "gap"
        self.graphcopy.graph["graph"] = {"splines": "ortho"}
        atribs = nx.get_node_attributes(self.graphcopy, "Group")
        nodes = self.graphcopy.nodes()
        edge_add = []
        edge_remove = []
        for i, j in enumerate(self.context_no_unordered):
            ####find paths in that phase

            phase = atribs[j]
            root = [i for i in nodes if "b_" + str(phase) in i][0]
            leaf = [i for i in nodes if "a_" + str(phase) in i][0]
            all_paths = []
            all_paths.extend(nx.all_simple_paths(self.graphcopy, source=root, target=leaf))

            if self.CONT_TYPE[i] == "residual":
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.graphcopy.edges():
                    if k[0] == j:
                        edge_remove.append((k[0], k[1]))
            elif self.CONT_TYPE[i] == "intrusive":
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.graphcopy.edges():
                    if k[1] == j:
                        edge_remove.append((k[0], k[1]))
        for a in edge_add:
            self.graphcopy.add_edge(a[0], a[1], arrowhead="none")
        for b in edge_remove:
            self.graphcopy.remove_edge(b[0], b[1])

        # networkx.drawing.nx_pydot.write_dot from networkx < 3.4 does not quote node attributes correctly if they contain characters such as :. Networkx 3.4 is only available for pythono >= 3.10, so a workaround is required for python 3.9 users.
        if packaging.version.parse(nx.__version__) < packaging.version.parse("3.4.0"):
            # Remove the contraction attribute from nodes.
            for i in nodes:
                self.graphcopy.nodes[i].pop("contraction", None)

        # @todo move this into the model?
        write_dot(self.graphcopy, workdir / "fi_new_chrono")

        # write output variables into the Model once it is confirmed.
        # @todo - might be better for this presenter to own a deep copy, which on confirmation is updated? Thoguht that won't be useful for any on-disk files?
        self.model.CONT_TYPE = self.CONT_TYPE
        self.model.prev_phase = self.prev_phase
        self.model.post_phase = self.post_phase
        self.model.phi_ref = self.phi_ref
        self.model.context_no_unordered = self.context_no_unordered
        self.model.chronological_dag = (
            self.graphcopy
        )  # @todo - is this correct? does it need to be graphcopy in the model?
        self.model.node_del_tracker = self.node_del_tracker
        # Close the popup window
        self.close_window()

    def close_window(self, reason: Optional[str] = None) -> None:
        # Close the view
        self.view.destroy()
