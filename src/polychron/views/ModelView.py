import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional, Tuple

import pandas as pd
from PIL import Image, ImageTk

from .BaseFrameView import BaseFrameView


class ModelView(BaseFrameView):
    """Main view for displaying information about the model.
    I.e. the "Stratigraphy and supplementary data" tab

    Formely part of `StartPage`

    Todo:
        @todo - consider splitting each canvas to it's own separate classes?
        @todo - Make the testmenu have a default option of "Node Action" which appears to have been intended?
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the base class constructor
        super().__init__(parent)

        self.configure(background="white")

        # Use a canvas to add a background colour below the menu bar
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg="#AEC7D6")
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

        # Adding File Menu and commands
        # @todo - (partially) abstract this away to avoid duplication
        self.file_menubar = ttk.Menubutton(self, text="File")
        file = tk.Menu(self.file_menubar, tearoff=0, bg="white", font=("helvetica 12 bold"))
        self.file_menubar["menu"] = file
        file.add_separator()
        file.add_command(label="Load stratigraphic diagram file (.dot)", font="helvetica 12 bold")
        file.add_command(label="Load stratigraphic relationship file (.csv)", font="helvetica 12 bold")
        file.add_command(label="Load scientific dating file (.csv)", font="helvetica 12 bold")
        file.add_command(label="Load context grouping file (.csv)", font="helvetica 12 bold")
        file.add_command(label="Load group relationship file (.csv)", font="helvetica 12 bold")
        file.add_command(label="Load context equalities file (.csv)", font="helvetica 12 bold")
        file.add_command(label="Load new project", font="helvetica 12 bold")
        file.add_command(label="Load existing model", font="helvetica 12 bold")
        file.add_command(label="Save changes as current model", font="helvetica 12 bold", accelerator="Ctrl+s")
        file.add_command(
            label="Save changes as new model",
            font="helvetica 12 bold",  # , accelerator="Ctrl+Shift+s"
        )
        file.add_separator()
        file.add_command(label="Exit", font="helvetica 12 bold", accelerator="Ctrl+w")
        self.file_menubar.place(relx=0.00, rely=0, relwidth=0.1, relheight=0.03)

        # Adding View Menu and commands
        self.view_menubar = ttk.Menubutton(self, text="View")
        view_menu = tk.Menu(self.view_menubar, tearoff=0, bg="white", font=("helvetica", 11))
        self.view_menubar["menu"] = view_menu
        view_menu.add_command(label="Display Stratigraphic diagram in phases", font="helvetica 12 bold")
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)

        # Adding Tool Menu and commands
        self.tool_menubar = ttk.Menubutton(self, text="Tools")
        tool_menu = tk.Menu(self.tool_menubar, tearoff=0, bg="white", font=("helvetica", 11))
        self.tool_menubar["menu"] = tool_menu
        # tool_menu.add_separator()
        tool_menu.add_command(label="Render chronological graph", font="helvetica 12 bold")
        tool_menu.add_command(label="Calibrate model", font="helvetica 12 bold")
        tool_menu.add_command(
            label="Calibrate multiple projects from project", font="helvetica 12 bold"
        )  #  command=lambda: popupWindow8(self, proj_dir))
        tool_menu.add_command(
            label="Calibrate node delete variations (alpha)", font="helvetica 12 bold"
        )  #  command=lambda: popupWindow9(self, proj_dir))
        tool_menu.add_command(
            label="Calibrate important variations (alpha)", font="helvetica 12 bold"
        )  #  command=lambda: popupWindow10(self, proj_dir))
        # tool_menu.add_separator()
        self.tool_menubar.place(relx=0.14, rely=0, relwidth=0.1, relheight=0.03)

        self.behindcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas.place(relx=0.003, rely=0.038, relwidth=0.37, relheight=0.96)

        self.behindcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas2.place(relx=0.38, rely=0.038, relwidth=0.37, relheight=0.96)

        self.labelcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas.place(relx=0.003, rely=0.011, relwidth=0.18, relheight=0.027)
        self.labelcanvas1_id = self.labelcanvas.create_text(10, 3, anchor="nw", fill="white")
        self.labelcanvas.itemconfig(self.labelcanvas1_id, text="Stratigraphic graph", font="helvetica 12 bold")

        self.littlecanvas = tk.Canvas(
            self.behindcanvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_id = self.littlecanvas.create_text(10, 10, anchor="nw", fill="#2f4845")
        self.littlecanvas.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        self.littlecanvas.itemconfig(
            self.littlecanvas_id,
            text="No stratigraphic graph loaded. \n \n \nTo load, go to File > Load stratigraphic diagram",
            font="helvetica 12 bold",
        )
        self.littlecanvas.update()

        self.littlecanvas2 = tk.Canvas(
            self.behindcanvas2, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2_id = self.littlecanvas2.create_text(10, 10, anchor="nw", fill="#2f4845")
        self.littlecanvas2.itemconfig(
            self.littlecanvas2_id,
            text="No chronological graph loaded. \n \n \nYou must load a stratigraphic graph first. \nTo load, go to File > Load stratigraphic diagram \nTo load your chronological graph, go to Tools > Render chronological graph",
            font="helvetica 12 bold",
        )
        self.littlecanvas2.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)

        self.labelcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas2.place(relx=0.38, rely=0.011, relwidth=0.18, relheight=0.027)
        self.labelcanvas2_id = self.labelcanvas2.create_text(10, 3, anchor="nw", fill="white")
        self.labelcanvas2.itemconfig(self.labelcanvas2_id, text="Chronological graph", font="helvetica 12 bold")

        # placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)
        self.littlecanvas2.rowconfigure(0, weight=1)
        self.littlecanvas2.columnconfigure(0, weight=1)
        self.littlecanvas2.update()

        # Right click menu for stratigraphic graph canvas
        self.OptionList = [
            # "Node Action", # Add a do nothing option that provides the title?
            "Delete context",
            "Delete stratigraphic relationship",
            "Get supplementary data for this context",
            "Equate context with another",
            "Place above other context",
            "Add new contexts",
            # "Supplementary data menu (BROKEN)", # @todo see https://github.com/bryonymoody/PolyChron/issues/69
        ]
        self.__testmenu_variable = tk.StringVar(self.littlecanvas)  # @todo - not using but required?
        self.__testmenu_variable.set("Node Action")
        self.__testmenu_callback: Callable[[], Optional[Any]] = lambda event: None
        """reference to the callback method for the test menu, as it does not appear that an OptionMenu(command) can be changed after construction."""
        self.testmenu = ttk.OptionMenu(
            self.littlecanvas,
            self.__testmenu_variable,
            self.OptionList[0],
            *self.OptionList,
            command=lambda event: self.__testmenu_callback(event),
        )
        # meta data table
        self.labelcanvas3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas3.place(relx=0.755, rely=0.695, relwidth=0.17, relheight=0.029)
        self.behindcanvas3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas3.place(relx=0.755, rely=0.719, relwidth=0.23, relheight=0.278)
        self.metatext_id = self.labelcanvas3.create_text(10, 5, anchor="nw", fill="white")
        self.labelcanvas3.itemconfig(self.metatext_id, text="Supplementary data", font="helvetica 12 bold")
        self.tree1 = ttk.Treeview(self.canvas)
        self.tree1["columns"] = ["Data"]
        self.tree1.place(relx=0.758, rely=0.725)
        self.tree1.column("Data", anchor="w")
        self.tree1.heading("Data", text="Data")
        # deleted contexts table
        self.labelcanvas4 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas4.place(relx=0.755, rely=0.04, relwidth=0.17, relheight=0.029)
        self.behindcanvas4 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas4.place(relx=0.755, rely=0.069, relwidth=0.23, relheight=0.278)
        self.delcontext_id = self.labelcanvas4.create_text(10, 5, anchor="nw", fill="white")
        self.labelcanvas4.itemconfig(self.delcontext_id, text="Deleted Contexts", font="helvetica 12 bold")

        # Table / treeview for deleted nodes with their reasons
        self.tree2 = ttk.Treeview(self.canvas)
        self.tree2.heading("#0", text="Context")
        self.tree2["columns"] = ["Meta"]
        self.tree2.place(relx=0.758, rely=0.0729)
        self.tree2.column("Meta", anchor="w")
        self.tree2.heading("Meta", text="Reason for deleting")

        # deleted edges table
        self.labelcanvas5 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas5.place(relx=0.755, rely=0.371, relwidth=0.17, relheight=0.029)
        self.behindcanvas5 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas5.place(relx=0.755, rely=0.399, relwidth=0.23, relheight=0.278)
        self.deledge_id = self.labelcanvas5.create_text(10, 5, anchor="nw", fill="white")
        self.labelcanvas5.itemconfig(
            self.deledge_id, text="Deleted Stratigraphic Relationships", font="helvetica 12 bold"
        )
        self.tree3 = ttk.Treeview(self.canvas)
        self.tree3.heading("#0", text="Stratigraphic relationship")
        self.tree3["columns"] = ["Meta"]
        self.tree3.place(relx=0.758, rely=0.405)
        self.tree3.heading("Meta", text="Reason for deleting")
        # @todo - this was in StartPage.__init__, however f_1 is used to comapre to f_2 and set newvars which is never used, so don't think it's required?
        # f = dir(self)
        # self.f_1 = [var for var in f if ('__' or 'grid' or 'get') not in var]
        # self.littlecanvas.update()
        # try:
        #     self.restore_state()
        # except FileNotFoundError:
        #     self.save_state_1()

        # Button and canvas for showing what data has been loaded so far.
        self.data_button = tk.Button(
            self, text="Data loaded  ↙", font="helvetica 12 bold", fg="white", bd=0, highlightthickness=0, bg="#33658a"
        )  # command=lambda: self.display_data_func()
        self.data_button.place(relx=0.303, rely=0.04, relwidth=0.07, relheight=0.028)
        self.datacanvas = tk.Canvas(self.behindcanvas, bd=0, highlightthickness=0, bg="#33658a")
        self.datacanvas.place(relx=0.55, rely=0.0, relwidth=0.45, relheight=0.2)
        self.datalittlecanvas = tk.Canvas(
            self.datacanvas, bd=8, bg="white", highlightbackground="#33658a", highlightthickness=5
        )
        self.datalittlecanvas.place(relx=0.015, rely=0.015, relwidth=0.97, relheight=0.97)
        tk.Misc.lift(self.littlecanvas)

    def get_testmenu_selection(self) -> str:
        """Return the most recent value for the testmenu"""
        return self.__testmenu_variable.get()

    def set_testmenu_selection(self, value: str) -> None:
        """Set the value for the testmenu"""
        return self.__testmenu_variable.set(value)

    def bind_testmenu_commands(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for the stratigraphic graph right-click menu

        ttk.OptionMenu doesn not accept commadns to .config, only on the constructor? So in this case the view contains a reference to the callback

        @todo rename testmenu and this method
        """
        self.__testmenu_callback = callback

    def bind_sasd_tab_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the sasd_tab_button is pressed"""
        if callback is not None:
            self.sasd_tab_button.config(command=callback)

    def bind_dr_tab_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the dr_tab_button is pressed"""
        if callback is not None:
            self.dr_tab_button.config(command=callback)

    def bind_data_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the data_button is pressed"""
        if callback is not None:
            self.data_button.config(command=callback)

    def bind_littlecanvas_callback(self, sequence: str, callback: Callable[[], Optional[Any]]) -> None:
        """Bind a single callback to the specified sequence on the littlecanvas. This is an alternative to an all in one bind method, as the canvas repeatedly gets cleared"""
        self.littlecanvas.bind(sequence, callback)

    def unbind_littlecanvas_callback(self, sequence: str) -> None:
        """Unbind a single callback to the specified sequence on the littlecanvas. This is an alternative to an all in one bind method, as the canvas repeatedly gets cleared"""
        self.littlecanvas.unbind(sequence)

    def bind_littlecanvas2_callback(self, sequence: str, callback: Callable[[], Optional[Any]]) -> None:
        """Bind a single callback to the specified sequence on the littlecanvas2. This is an alternative to an all in one bind method, as the canvas repeatedly gets cleared"""
        self.littlecanvas2.bind(sequence, callback)

    def unbind_littlecanvas2_callback(self, sequence: str) -> None:
        """Unbind a single callback to the specified sequence on the littlecanvas2. This is an alternative to an all in one bind method, as the canvas repeatedly gets cleared"""
        self.littlecanvas2.unbind(sequence)

    def show_testmenu(self, has_image: bool) -> Tuple[Optional[int], Optional[int]]:
        """Show the test menu within the little canvas at the cursors' coordinates

        Formerly part of StartPage.onRight

        Parameters:
            has_image: If the little canvas has been rendered with an image or not.
        """
        # Get the curosr position relative to the window / canvas
        cursor_x = int(self.littlecanvas.winfo_pointerx() - self.littlecanvas.winfo_rootx())
        cursor_y = int(self.littlecanvas.winfo_pointery() - self.littlecanvas.winfo_rooty())

        # Now we define our right click menu canvas
        # And here is where we use our X and Y variables, to place the menu where our cursor is,
        # That's how right click menus should be placed.
        self.testmenu.place(x=cursor_x, y=cursor_y)
        # This is for packing our options onto the canvas, to prevent the canvas from resizing.
        # This is extremely useful if you split your program into multiple canvases or frames
        # and the pack method is forcing them to resize.
        self.testmenu.pack_propagate(0)
        # Here is our label on the right click menu for deleting a row, notice the cursor
        # value, which will give us a pointy finger when you hover over the option.
        testmenuWidth = len(max(self.OptionList, key=len))
        self.testmenu.config(width=testmenuWidth)

        # Return the scaled x and y coords so the presenter can check if a node was presesd.
        # @todo improve this separation of concerns
        if has_image:
            x_scal = cursor_x + self.transx
            y_scal = cursor_y + self.transy
            # self.node = self.nodecheck(x_scal, y_scal)
            return x_scal, y_scal
        else:
            return None, None

    def bind_littlecanvas_events(
        self,
        callback_wheel: Callable[[], Optional[Any]],
        callback_move_from: Callable[[], Optional[Any]],
        callback_move_to: Callable[[], Optional[Any]],
    ) -> None:
        """Bind mouse callback events for interacting with the graph canvas

        @todo - split this method?

        @todo better callback names
        """
        self.littlecanvas.bind("<MouseWheel>", callback_wheel)
        self.littlecanvas.bind("<Button-4>", callback_wheel)  # only with Linux, wheel scroll down
        self.littlecanvas.bind("<Button-5>", callback_wheel)
        self.littlecanvas.bind("<Button-1>", callback_move_from)
        self.littlecanvas.bind("<B1-Motion>", callback_move_to)

    def bind_littlecanvas2_events(
        self,
        callback_wheel: Callable[[], Optional[Any]],
        callback_move_from: Callable[[], Optional[Any]],
        callback_move_to: Callable[[], Optional[Any]],
    ) -> None:
        """Bind mouse callback events for interacting with the graph canvas

        @todo - split this method?

        @todo better callback names
        """
        self.littlecanvas2.bind("<MouseWheel>", callback_wheel)
        self.littlecanvas2.bind("<Button-4>", callback_wheel)  # only with Linux, wheel scroll down
        self.littlecanvas2.bind("<Button-5>", callback_wheel)
        self.littlecanvas2.bind("<Button-1>", callback_move_from)
        self.littlecanvas2.bind("<B1-Motion>", callback_move_to)

    def bind_file_menu_callbacks(self, callbacks: Dict[str, Callable[[], Optional[Any]]]) -> None:
        """Binds callback methods to file menu elements by label

        @todo - standardise this with how other menu callbacks are set in ModelView/DatingResultsVeiw. Probably a Dict[str, Callable] usign the menu label? Or just have a member dict of function pointers and directly bind to that for each command on creation.
        Would be nicer to not have to re-use the full label?
        """
        file_menu = self.nametowidget(self.file_menubar.cget("menu"))
        for entry_label, callback in callbacks.items():
            if callback is not None:
                # @todo - handle missing labels gracefully
                file_menu.entryconfig(entry_label, command=callback)

    def bind_view_menu_callbacks(self, callbacks: Dict[str, Callable[[], Optional[Any]]]) -> None:
        """Binds callback methods to view menu elements by label

        @todo - standardise this with how other menu callbacks are set in ModelView/DatingResultsVeiw. Probably a Dict[str, Callable] usign the menu label? Or just have a member dict of function pointers and directly bind to that for each command on creation.
        Would be nicer to not have to re-use the full label?
        """
        view_menu = self.nametowidget(self.view_menubar.cget("menu"))
        for entry_label, callback in callbacks.items():
            if callback is not None:
                # @todo - handle missing labels gracefully
                view_menu.entryconfig(entry_label, command=callback)

    def bind_tool_menu_callbacks(self, callbacks: Dict[str, Callable[[], Optional[Any]]]) -> None:
        """Binds callback methods to file menu elements by label

        @todo - standardise this with how other menu callbacks are set in ModelView/DatingResultsVeiw. Probably a Dict[str, Callable] usign the menu label? Or just have a member dict of function pointers and directly bind to that for each command on creation.
        Would be nicer to not have to re-use the full label?
        """
        tool_menu = self.nametowidget(self.tool_menubar.cget("menu"))
        for entry_label, callback in callbacks.items():
            if callback is not None:
                # @todo - handle missing labels gracefully
                tool_menu.entryconfig(entry_label, command=callback)

    def lift_datacanvas(self) -> None:
        """Lift the datacanvas element to the top of the littlecanvas"""
        tk.Misc.lift(self.datacanvas)
        self.data_button["text"] = "Data loaded ↗"

    def lift_littelcanvas(self) -> None:
        """Lift the littlecanvas element to the top of the datacanvas"""
        tk.Misc.lift(self.littlecanvas)
        self.data_button["text"] = "Data loaded ↙"

    def update_datacanvas_checklist(
        self, strat_check: bool, date_check: bool, phase_check: bool, phase_rel_check: bool
    ) -> None:
        """Update the contents of the datacanvas checklist based on provided model state

        Formerly part of StartPage.check_list_gen
        """

        if strat_check:
            strat = "‣ Stratigraphic relationships"
            col1 = "green"
        else:
            strat = "‣ Stratigraphic relationships"
            col1 = "black"
        if date_check:
            date = "‣ Radiocarbon dates"
            col2 = "green"
        else:
            date = "‣ Radiocarbon dates"
            col2 = "black"
        if phase_check:
            phase = "‣ Groups for contexts"
            col3 = "green"
        else:
            phase = "‣ Groups for contexts"
            col3 = "black"
        if phase_rel_check:
            rels = "‣ Relationships between groups"
            col4 = "green"
        else:
            rels = "‣ Relationships between groups"
            col4 = "black"

        self.datalittlecanvas.delete("all")
        self.datalittlecanvas.create_text(
            10, 20, anchor="nw", text=strat + "\n\n", font=("Helvetica 12 bold"), fill=col1
        )
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(
            10, 50, anchor="nw", text=date + "\n\n", font=("Helvetica 12 bold"), fill=col2
        )
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(
            10, 80, anchor="nw", text=phase + "\n\n", font=("Helvetica 12 bold"), fill=col3
        )
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(10, 110, anchor="nw", text=rels, font=("Helvetica 12 bold"), fill=col4)
        self.datalittlecanvas.pack()

    def update_littlecanvas(self, image) -> None:
        """Update the image within the littlecanvas element

        @todo bindings"""
        self.image = image  # @todo don't store this in the view.
        self.littlecanvas.delete("all")
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw", image=self.littlecanvas.img)
        self.width, self.height = self.image.size
        # self.imscale = 1.0 #, self.littlecanvas.winfo_height()/self.image.size[1])# scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.imscale = min(921 / self.image.size[0], 702 / self.image.size[1])
        self.littlecanvas.scale("all", 0, 0, self.delta, self.delta)  # rescale all canvas objects
        self.show_image()

    def show_image(self) -> None:
        """Show image on the Canvas

        @todo the logic for this should probably be elsewhere / add parameters?"""
        bbox1 = [0, 0, int(self.image.size[0] * self.imscale), int(self.image.size[1] * self.imscale)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.littlecanvas.canvasx(0),  # get visible area of the canvas
            self.littlecanvas.canvasy(0),
            self.littlecanvas.canvasx(self.littlecanvas.winfo_width()),
            self.littlecanvas.canvasy(self.littlecanvas.winfo_height()),
        )
        if int(bbox2[3]) == 1:
            bbox2 = [0, 0, 0.96 * 0.99 * 0.97 * 1000, 0.99 * 0.37 * 2000 * 0.96]
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        bbox1 = [0, 0, int(self.image.size[0] * self.imscale), int(self.image.size[1] * self.imscale)]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.littlecanvas.configure(scrollregion=bbox)  # set scroll region
        x_1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y_1 = max(bbox2[1] - bbox1[1], 0)
        x_2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y_2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        if int(x_2 - x_1) > 0 and int(y_2 - y_1) > 0:  # show image if it in the visible area
            x_img = min(int(x_2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x_1 / self.imscale), int(y_1 / self.imscale), x_img, y_img))
            self.imagetk = ImageTk.PhotoImage(image.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas.delete(self.littlecanvas_img)
            self.imageid = self.littlecanvas.create_image(
                max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]), anchor="nw", image=self.imagetk
            )
            self.transx, self.transy = bbox2[0], bbox2[1]
            self.littlecanvas.imagetk = self.imagetk

    def clear_littlecanvas2(self) -> None:
        """Delete all elments from within the littlecavnas2

        @todo - rename to mention chrono graph instead."""
        self.littlecanvas2.delete("all")

    def update_littlecanvas2(self, image: Image.Image) -> None:
        """Update the image within the littlecanvas2 element - i.e. the chronological graph.

        @todo type hints
        @todo bindings
        @todo - rename method
        @todo - which of these values are actually needed as class members?
        """
        self.image2 = image  # @todo don't store this in the view.

        self.littlecanvas2.delete("all")
        self.littlecanvas2.img = ImageTk.PhotoImage(image)
        self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw", image=self.littlecanvas2.img)
        self.width2, self.height2 = image.size
        # self.imscale2 = 1.0  # scale for the canvaas image
        self.delta2 = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
        self.imscale2 = min(921 / image.size[0], 702 / image.size[1])
        self.littlecanvas2.scale("all", 0, 0, self.delta2, self.delta2)  # rescale all canvas objects
        self.show_image2()

    def show_image2(self) -> None:
        """Show image on the 2nd Canvas

        @todo the logic for this should probably be elsewhere / add parameters?
        @todo rename methdo"""
        bbox1 = [0, 0, int(self.image2.size[0] * self.imscale2), int(self.image2.size[1] * self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.littlecanvas2.canvasx(0),  # get visible area of the canvas
            self.littlecanvas2.canvasy(0),
            self.littlecanvas2.canvasx(self.littlecanvas2.winfo_width()),
            self.littlecanvas2.canvasy(self.littlecanvas2.winfo_height()),
        )
        if int(bbox2[3]) == 1:
            bbox2 = [0, 0, 0.96 * 0.99 * 0.97 * 1000, 0.99 * 0.37 * 2000 * 0.96]
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        bbox1 = [0, 0, int(self.image2.size[0] * self.imscale2), int(self.image2.size[1] * self.imscale2)]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.littlecanvas2.configure(scrollregion=bbox)  # set scroll region
        x_1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y_1 = max(bbox2[1] - bbox1[1], 0)
        x_2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y_2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x_2 - x_1) > 0 and int(y_2 - y_1) > 0:  # show image if it in the visible area
            x_img = min(int(x_2 / self.imscale2), self.width2)  # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image2.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2), x_img, y_img))
            self.imagetk2 = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas2.delete(self.littlecanvas2_img)
            self.imageid2 = self.littlecanvas2.create_image(
                max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]), anchor="nw", image=self.imagetk2
            )
            self.transx2, self.transy2 = bbox2[0], bbox2[1]
            self.littlecanvas2.imagetk2 = self.imagetk2

    def update_littlecanvas_image_only(self, image: Image.Image, event: Any) -> None:
        """Update the image within the littlecanvas, during resizing.

        @todo - this and the other update method can probably be combined
        """
        self.littlecanvas.img = ImageTk.PhotoImage(image)
        self.w_1 = event.width  # @todo - not used
        self.h_1 = event.height  # @todo - not used
        self.littlecanvas.itemconfig(self.littlecanvas_img, image=self.littlecanvas.img)

    def update_littlecanvas2_image_only(self, image: Image.Image, event: Any) -> None:
        """Update the image within the littlecanvas2, during resizing.

        @todo - this and the other update method can probably be combined
        """
        self.littlecanvas.img = ImageTk.PhotoImage(image)
        self.w_1 = event.width  # @todo - not used
        self.h_1 = event.height  # @todo - not used
        self.littlecanvas.itemconfig(self.littlecanvas_img, image=self.littlecanvas.img)

    def wheel(self, event: Any) -> None:
        """Zoom with mouse wheel for the stratigraphic image canvas

        Formerly (part of) StartPage.wheel

        @todo this abstraction could probably be improved"""
        x_zoom = self.littlecanvas.canvasx(event.x)
        y_zoom = self.littlecanvas.canvasy(event.y)
        bbox = self.littlecanvas.bbox(self.container)  # get image area
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
        self.littlecanvas.scale("all", 0, 0, scale, scale)  # rescale all canvas objects
        self.show_image()

    def wheel2(self, event: Any) -> None:
        """Zoom with mouse wheel for the stratigraphic image canvas

        Formerly (part of) StartPage.wheel

        @todo this abstraction could probably be improved"""

        # If there is no container2 yet, i.e. no image, don't do anything. @todo improve this check.
        if not hasattr(self, "container2") or self.container2 is None:
            return

        x_zoom = self.littlecanvas2.canvasx(event.x)
        y_zoom = self.littlecanvas2.canvasy(event.y)
        bbox = self.littlecanvas2.bbox(self.container2)  # get image area
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale2 = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width2, self.height2)
            if int(i * self.imscale2) < 30:
                return  # image is less than 30 pixels
            self.imscale2 /= self.delta2
            scale2 /= self.delta2
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
            if i < self.imscale2:
                return  # 1 pixel is bigger than the visible area
            self.imscale2 *= self.delta2
            scale2 *= self.delta2
        self.littlecanvas2.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def append_deleted_node(self, node: str, meta: str) -> None:
        """Append the node and meta data to the deleted nodes treeview

        @todo - make this take an object instead of 2 strs?
        @todo - replace with a method which just updates the treeview from a list of objects?"""
        self.tree2.insert("", "end", text=node, values=[meta])

    def append_deleted_edge(self, edge_label: str, meta: str) -> None:
        """Append the edge and meta data to the deleted edges treeview

        Includes part of StartPage.edgeRender

        @todo - make this 3 cols not 2?
        @todo - replace with a method which just updates the treeview from a list of objects?
        """
        self.tree3.insert("", "end", text=edge_label, values=[meta])

    def append_testmenu_entry(self, text: str) -> None:
        """Append an entry to the end of the right click testmenu.

        @todo - insert instead?
        @todo - edit instead of overwrite self.testmenu"""
        self.OptionList.append(text)
        self.testmenu = ttk.OptionMenu(
            self.littlecanvas,
            self.__testmenu_variable,
            self.OptionList[0],
            *self.OptionList,
            command=self.__testmenu_callback,
        )

    def remove_testmenu_entry(self, text: str) -> None:
        """Remove an entry to the end of the right click testmenu.

        @todo - edit instead of overwrite self.testmenu"""

        self.OptionList.remove(text)
        self.testmenu = ttk.OptionMenu(
            self.littlecanvas,
            self.__testmenu_variable,
            self.OptionList[0],
            *self.OptionList,
            command=self.__testmenu_callback,
        )

    def update_supplementary_data_table(self, node: str, meta_df: pd.DataFrame) -> None:
        """Update the contents of the supplementary data table (tree 1)"""
        # @note fixed this to update the title
        self.labelcanvas3.itemconfig(
            self.metatext_id, text="Supplementary data of node " + str(node), font="helvetica 12 bold"
        )
        cols = list(meta_df.columns)
        # Clear the tree view
        self.tree1.delete(*self.tree1.get_children())
        # re set the tree view data
        self.tree1["columns"] = cols
        self.tree1.place(relx=0.758, rely=0.725, relwidth=0.225)
        self.tree1.column("Data", anchor="w")
        self.tree1.heading("Data", text="Data", anchor="w")
        for index, row in meta_df.iterrows():
            self.tree1.insert("", 0, text=index, values=list(row))
        self.tree1.update()
