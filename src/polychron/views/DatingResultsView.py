import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from .BaseFrameView import BaseFrameView


class DatingResultsView(BaseFrameView):
    """View for displaying post-calibration "Dating Results" for a model.

    I.e. the "Dating Results" tab

    Formely part of `PageOne`

    @todo - consider splitting each canvas to it's own separate classes?
    @todo - Split the navbar into it's own class, to reduce duplication with ModelView)
    """

    def __init__(self, parent: tk.Frame):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        self.configure(background="#fcfdfd")

        # Use a canvas to add a background colour below the menu bar
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg="#FFE9D6")
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)

        # Add buttons to switch between the main windows.
        # @todo - abstract this esle where to avoid duplication
        self.sasd_tab_button = tk.Button(
            self,
            text="Stratigraphy and supplementary data",
            font="helvetica 12 bold",
            fg="#2F4858",
            bd=0,
            highlightthickness=0,
            bg="#AEC7D6",
        )
        self.sasd_tab_button.place(relx=0.38, rely=0.0, relwidth=0.17, relheight=0.03)
        self.dr_tab_button = tk.Button(
            self,
            text="Dating Results",
            font="helvetica 12 bold",
            fg="#8F4300",
            bd=0,
            highlightthickness=0,
            bg="#FFE9D6",
        )
        self.dr_tab_button.place(relx=0.55, rely=0.0, relwidth=0.15, relheight=0.03)

        # Add the file menu button and it's options
        # @todo - (partially) abstract this away to avoid duplication
        self.file_menubar = ttk.Menubutton(
            self,
            text="File",
        )
        self.file_menu = tk.Menu(self.file_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.file_menubar["menu"] = self.file_menu
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save project progress", font=("helvetica 11 bold"))
        self.file_menubar.place(relx=0.0, rely=0, relwidth=0.1, relheight=0.03)
        self.view_menubar = ttk.Menubutton(self, text="View")

        # Adding View menu with (no) sub options
        self.view_menubar["menu"] = tk.Menu(self.view_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)
        self.tool_menubar = ttk.Menubutton(
            self,
            text="Tools",
        )

        # Adding Tools menu with no suboptions
        self.tool_menubar["menu"] = tk.Menu(self.tool_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.tool_menubar.place(relx=0.15, rely=0, relwidth=0.1, relheight=0.03)
        # forming and placing canvas and little canvas
        self.behindcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas.place(relx=0.6, rely=0.038, relwidth=0.39, relheight=0.96)

        self.littlecanvas2_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2_label.place(relx=0.003, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas2_label_id = self.littlecanvas2_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas2_label.itemconfig(
            self.littlecanvas2_label_id, text="Chronological graph", font="helvetica 12 bold"
        )

        self.littlecanvas = tk.Canvas(
            self.behindcanvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)

        self.behindcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas2.place(relx=0.003, rely=0.038, relwidth=0.37, relheight=0.96)

        self.littlecanvas_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_label.place(relx=0.6, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas_label_id = self.littlecanvas_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas_label.itemconfig(
            self.littlecanvas_label_id, text="Posterior densities", font="helvetica 12 bold"
        )

        self.littlecanvas_a_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_a_label.place(relx=0.375, rely=0.518, relwidth=0.08, relheight=0.027)
        self.littlecanvas_a_label_id = self.littlecanvas_a_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas_a_label.itemconfig(
            self.littlecanvas_a_label_id, text="Context list", font="helvetica 12 bold"
        )

        self.behindcanvas_a = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas_a.place(relx=0.375, rely=0.038, relwidth=0.223, relheight=0.45)

        self.littlecanvas_a = tk.Canvas(
            self.behindcanvas_a, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_a.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)

        self.behindcanvas_3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas_3.place(relx=0.375, rely=0.545, relwidth=0.223, relheight=0.45)
        3
        self.littlecanvas2 = tk.Canvas(
            self.behindcanvas2, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)

        self.littlecanvas3 = tk.Canvas(
            self.behindcanvas_3, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas3.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.901)
        self.littlecanvas3_id = self.littlecanvas3.create_text(10, 10, anchor="nw", fill="#0A3200")
        self.littlecanvas3.itemconfig(
            self.littlecanvas3_id,
            text="No contexts chosen for results. \n\nTo add a context to the results list right click on \nthe context you want then select 'add to list'",
            font="helvetica 12 bold",
        )

        self.littlecanvas3_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas3_label.place(relx=0.375, rely=0.011, relwidth=0.14, relheight=0.027)
        self.littlecanvas3_label_id = self.littlecanvas3_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas3_label.itemconfig(
            self.littlecanvas3_label_id, text="Calendar date range estimates", font="helvetica 12 bold"
        )

        # placing image on littlecanvas from graph
        self.littlecanvas2.rowconfigure(0, weight=1)
        self.littlecanvas2.columnconfigure(0, weight=1)
        self.littlecanvas2.update()
        # placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)

        # Buttons for context list management
        self.posterior_densities_button = ttk.Button(
            self.behindcanvas_3,
            text="Posterior densities",
        )
        self.posterior_densities_button.place(relx=0.008, rely=0.92, relwidth=0.402, relheight=0.07)
        self.hpd_button = ttk.Button(
            self.behindcanvas_3,
            text="HPD intervals",
        )
        self.hpd_button.place(relx=0.415, rely=0.92, relwidth=0.322, relheight=0.07)
        self.clear_list_button = ttk.Button(
            self.behindcanvas_3,
            text="Clear list",
        )
        self.clear_list_button.place(relx=0.74, rely=0.92, relwidth=0.252, relheight=0.07)

        # Right click menu for the chrono graph canvas
        self.ResultList = [
            "Add to results list",
            "Get time elapsed",
        ]
        self.variable = tk.StringVar(self.littlecanvas)
        self.variable.set("Add to results list")
        self.testmenu2 = ttk.OptionMenu(
            self.littlecanvas2,
            self.variable,
            self.ResultList[0],
            *self.ResultList,
        )

    def bind_sasd_tab_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the sasd_tab_button is pressed"""
        if callback is not None:
            self.sasd_tab_button.config(command=callback)

    def bind_dr_tab_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the dr_tab_button is pressed"""
        if callback is not None:
            self.dr_tab_button.config(command=callback)

    def bind_posterior_densities_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the posterior_densities_button is pressed"""
        if callback is not None:
            self.posterior_densities_button.config(command=callback)

    def bind_hpd_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the hpd_button is pressed"""
        if callback is not None:
            self.hpd_button.config(command=callback)

    def bind_clear_list_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the clear_list_button is pressed"""
        if callback is not None:
            self.clear_list_button.config(command=callback)

    def bind_graphcanvas_events(
        self,
        callback_wheel: Callable[[], Optional[Any]],
        callback_rightclick: Callable[[], Optional[Any]],
        callback_move_from: Callable[[], Optional[Any]],
        callback_move_to: Callable[[], Optional[Any]],
    ) -> None:
        """Bind mouse callback events for interacting with the graph canvas

        @todo - split this method?

        @todo better callback names
        """
        self.graphcanvas.bind("<MouseWheel>", callback_wheel)
        self.graphcanvas.bind("<Button-4>", callback_wheel)  # only with Linux, wheel scroll down
        self.graphcanvas.bind("<Button-5>", callback_wheel)
        self.graphcanvas.bind("<Double-Button-3>", callback_rightclick)
        self.graphcanvas.bind("<Button-1>", callback_move_from)
        self.graphcanvas.bind("<B1-Motion>", callback_move_to)

    def bind_file_menu_commands(self):
        """Bind commands to the menu bar entires. This need some thought. One method per "menubar" which passes in a list of label/command pairs?"""
        pass

    def bind_view_menu_commands(self):
        """Bind commands to the menu bar entires. This need some thought. One method per "menubar" which passes in a list of label/command pairs?"""
        pass

    def bind_tools_menu_commands(self):
        """Bind commands to the menu bar entires. This need some thought. One method per "menubar" which passes in a list of label/command pairs?"""
        pass
