import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askopenfile
from typing import Any, Optional

import pandas as pd

from ..interfaces import Navigator
from ..presenters.CalibrateModelSelectPresenter import CalibrateModelSelectPresenter
from ..presenters.DatafilePreviewPresenter import DatafilePreviewPresenter
from ..presenters.MCMCProgressPresenter import MCMCProgressPresenter
from ..presenters.ResidualCheckPopupPresenter import ResidualCheckPopupPresenter
from ..presenters.ResidualOrIntrusivePresenter import ResidualOrIntrusivePresenter
from ..views.CalibrateModelSelectView import CalibrateModelSelectView
from ..views.DatafilePreviewView import DatafilePreviewView
from ..views.MCMCProgressView import MCMCProgressView
from ..views.ModelView import ModelView
from ..views.ResidualCheckPopupView import ResidualCheckPopupView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .BaseFramePresenter import BaseFramePresenter


class ModelPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ModelView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.navigator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_presenter("DatingResults"))

        # Bind menu callbacks
        # @todo other menus

        self.view.bind_file_menu_callbacks(
            {
                "Load stratigraphic diagram file (.dot)": lambda: self.open_strat_dot_file(),
                "Load stratigraphic relationship file (.csv)": lambda: self.open_strat_csv_file(),
                "Load scientific dating file (.csv)": lambda: self.open_scientific_dating_file(),
                "Load context grouping file (.csv)": lambda: self.open_context_grouping_file(),
                "Load group relationship file (.csv)": lambda: self.open_group_relationship_file(),
                "Load context equalities file (.csv)": lambda: self.open_scientific_dating_file(),
                "Load new project": lambda: print("@todo"),
                "Load existing model": lambda: print("@todo"),
                "Save changes as current model": lambda: print("@todo"),
                "Save changes as new model": lambda: print("@todo"),
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
        # @todo

        # Bind mouse & keyboard events
        # @todo

        # Update data

    def update_view(self) -> None:
        pass  # @todo

    def popup_calibrate_model(self) -> None:
        """Callback function for when Tools -> Calibrate model is selected

        @todo - this allows multiple open project windows to be created, which is not ideal
        """
        # Create the popup presenter and view
        popup_presenter = MCMCProgressPresenter(self.navigator, MCMCProgressView(self.view), self.model)
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
        self.navigator.switch_presenter("DatingResults")

        # @todo - esnure the presenter is destroyed

    def popup_calibrate_multiple(self) -> None:
        """Callback function for when Tools -> Calibrate multiple projects from project is selected

        Opens a new popup box allowing the user to select which models from a list to calibrate as a batch.
        On close, depending on if any models were selected or not, the models are subsequently calibrated

        @todo - this allows multiple open project windows to be created, which is not ideal
        """
        popup_presenter = CalibrateModelSelectPresenter(self.navigator, CalibrateModelSelectView(self.view), self.model)
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
                self.navigator, ResidualOrIntrusiveView(self.view), self.model
            )
            popup_presenter.view.deiconify()
            popup_presenter.view.lift()  # @todo - not sure these are neccesary
        else:
            # If not, show the residual check presenter, formerly popupWindow3
            popup_presenter = ResidualCheckPopupPresenter(self.navigator, ResidualCheckPopupView(self.view), self.model)
            popup_presenter.view.deiconify()
            popup_presenter.view.lift()  # @todo - not sure these are neccesary

    def file_popup(self, df: Any) -> str:
        """For a gien dataframe, preview the data to the user. Returns the users decision

        @todo - make this return a bool instead of 'load' or 'cancel'
        """
        # @todo set and get model data appropriately
        temp_model = {"df": df, "result": "cancel"}
        popup_presenter = DatafilePreviewPresenter(self.navigator, DatafilePreviewView(self.view), temp_model)
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()  # @todo - not sure these are neccesary

        # Prevent the view's canvas element from being interacted with?
        self.view.canvas["state"] = "disabled"  # @todo
        self.view.parent.wait_window(popup_presenter.view)  # @todo - view.parent mignt not have wiat_window?
        self.view.canvas["state"] = "normal"  # @todo
        print(f"temp_model {temp_model}")
        return temp_model["result"]

    def open_strat_dot_file(self) -> None:
        """Callback function when File > Load stratigraphic diagram file (.dot) (.csv) is selected, opening a .dot / graphviz file representing the stratigraphic relationships

        Formerly StartPage.open_file1

        @todo - Implement this, once a "valid" dotfile for this is found.
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

        @todo - finish implementing this with the actual model

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])

        if file is not None:
            try:
                # @todo finish this.
                # self.littlecanvas.delete('all')
                self.stratfile = pd.read_csv(file, dtype=str)
                load_it = self.file_popup(self.stratfile)
                if load_it == "load":
                    # @todo rest of open_file2
                    tk.messagebox.showinfo("Success", "Stratigraphic data loaded")
                    # self.check_list_gen() # @todo
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
                self.datefile = pd.read_csv(file)
                self.datefile = self.datefile.applymap(str)
                load_it = self.file_popup(self.datefile)
                if load_it == "load":
                    for i, j in enumerate(self.datefile["context"]):
                        self.graph.nodes()[str(j)].update(
                            {"Determination": [self.datefile["date"][i], self.datefile["error"][i]]}
                        )
                    # self.context_no_unordered = list(self.graph.nodes()) # @todo
                # self.date_check = True # @todo
                # self.check_list_gen() # @todo
                tk.messagebox.showinfo("Success", "Scientific dating data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_context_grouping_file(self) -> None:
        """Callback function when File > Load context grouping file (.csv) is selected, opening context grouping / phase file

        Formerly StartPage.open_file4

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - finish implementing this with the actual model

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                self.phasefile = pd.read_csv(file)
                self.phasefile = self.phasefile.applymap(str)
                load_it = self.file_popup(self.phasefile)
                if load_it == "load":
                    for i, j in enumerate(self.phasefile["context"]):
                        self.graph.nodes()[str(j)].update({"Group": self.phasefile["Group"][i]})
                # self.phase_check = True # @todo
                # self.check_list_gen() # @todo
                tk.messagebox.showinfo("Success", "Grouping data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_group_relationship_file(self) -> None:
        """Callback function when File > Load group relationship file (.csv) is selected, opening a group relationship / phase relationship file

        Formerly StartPage.open_file5

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - finish implementing this with the actual model

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                phase_rel_df = pd.read_csv(file)
                self.phase_rels = [
                    (str(phase_rel_df["above"][i]), str(phase_rel_df["below"][i])) for i in range(len(phase_rel_df))
                ]
                self.file_popup(pd.DataFrame(self.phase_rels, columns=["Younger group", "Older group"]))
                # self.phase_rel_check = True # @todo
                # self.check_list_gen() # @todo
                tk.messagebox.showinfo("Success", "Group relationships data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_context_equalities_file(self) -> None:
        """Callback function when File > Load context equalities file (.csv) is selected, opening a file providing context equalities (in time)

        Formerly StartPage.open_file6

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - finish implementing this with the actual model

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            try:
                equal_rel_df = pd.read_csv(file)
                self.equal_rel_df = equal_rel_df.applymap(str)
                # @todo - finish this
                # @todo - this method did not open a file_preview / popup.
                # context_1 = list(self.equal_rel_df.iloc[:, 0])
                # context_2 = list(self.equal_rel_df.iloc[:, 1])
                # for k, j in enumerate(context_1):
                #     self.graph = nx.contracted_nodes(self.graph, j, context_2[k])
                #     x_nod = list(self.graph)
                #     newnode = str(j) + " = " + str(context_2[k])
                #     y_nod = [newnode if i == j else i for i in x_nod]
                #     mapping = dict(zip(x_nod, y_nod))
                #     self.graph = nx.relabel_nodes(self.graph, mapping)
                # if phase_true == 1:
                #     imgrender_phase(self.graph)
                # else:
                #     imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
                # self.image = Image.open('testdag.png')
                # scale_factor = min(self.littlecanvas.winfo_width()/self.image_ws.size[0], self.littlecanvas.winfo_height()/self.image_ws.size[1])
                # self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
                # self.width, self.height = self.image.size
                # self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
                # self.show_image()
                tk.messagebox.showinfo("Success", "Equal contexts data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def close_application(self) -> None:
        """Close polychron gracefully via File > Exit"""
        # @todo - alert on any unsaved changed?
        self.navigator.close_navigator("exit")

    def phasing(self):
        """Callback function for View > Display Stratigraphic diagram in phases

        Runs image render function with phases on seperate levels

        Formerly StartPage.phasing

        """
        pass  # @todo - implement this method
        # global phase_true, node_df
        # phase_true = 1
        # self.image = imgrender_phase(self.graph)
        # self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        # self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
        #                                                        image=self.littlecanvas.img)
        # self.width, self.height = self.image.size
        # # self.imscale = 1.0  # scale for the canvaas image
        # self.delta = 1.1  # zoom magnitude
        # # Put image into container rectangle and use it to set proper coordinates to the image
        # self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        # self.imscale  = min(921/self.image.size[0], 702/self.image.size[1])
        # self.littlecanvas.scale('all', 0, 0, self.delta, self.delta)  # rescale all canvas objects
        # self.show_image()
        # self.bind("<Configure>", self.resize)
        # self.littlecanvas.bind("<Configure>", self.resize)
        # self.delnodes = []
        # self.delnodes_meta = []
        # self.canvas.delete('all')
        # self.littlecanvas.bind("<Button-3>", self.preClick)
        # self.show_image()

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
