import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Optional, Tuple

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import ImageTk

from .FrameView import FrameView


class DatingResultsView(FrameView):
    """View for displaying post-calibration "Dating Results" for a model.

    I.e. the "Dating Results" tab

    Formerly part of `PageOne`

    @todo - consider splitting each canvas to it's own separate classes?
    @todo - Split the navbar into it's own class, to reduce duplication with ModelView)
    @todo - rename a lot of the tk references.
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # Some class scoped variables for local state, set in one method but used by another.
        self.transx2: int = 0
        self.transy2: int = 0

        self.imscale2 = 1.0  # scale for the canvaas image
        self.delta2 = 1.1

        self.image2 = None  # @todo - can this just be model_model.crhono_image?

        self.tree_phases = None
        """Table tree, doenst' always exist @todo"""

        self.results_text = None
        """tkinter text handle within the littlecanvas3."""

        self.canvas_plt: Optional[FigureCanvasTkAgg] = None
        """Canvas which cotnains a plot"""

        self.toolbar: Optional[NavigationToolbar2Tk] = None
        """Matplotlib toolkbar for the canvas_plt if it exists"""

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

        # Add the file menu button
        self.file_menubar = ttk.Menubutton(self, text="File", state=tk.DISABLED)
        self.file_menubar["menu"] = tk.Menu(self.file_menubar, tearoff=0, bg="#fcfdfd", font=("helvetica", 11))
        self.file_menubar.place(relx=0.0, rely=0, relwidth=0.1, relheight=0.03)

        # Adding View menu button
        self.view_menubar = ttk.Menubutton(self, text="View", state=tk.DISABLED)
        self.view_menubar["menu"] = tk.Menu(self.view_menubar, tearoff=0, bg="#fcfdfd", font=("helvetica", 11))
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)

        # Adding Tools menu button
        self.tool_menubar = ttk.Menubutton(self, text="Tools", state=tk.DISABLED)
        self.tool_menubar["menu"] = tk.Menu(self.tool_menubar, tearoff=0, bg="#fcfdfd", font=("helvetica", 11))
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
        self.__testmenu2_variable = tk.StringVar(self.littlecanvas)  # @todo - not using but required?
        self.__testmenu2_variable.set("Add to results list")
        self.__testmenu2_callback: Callable[[], Optional[Any]] = lambda event: None
        self.testmenu2 = ttk.OptionMenu(
            self.littlecanvas2,
            self.__testmenu2_variable,
            self.ResultList[0],
            *self.ResultList,
            command=lambda event: self.__testmenu2_callback(event),
        )

    def get_testmenu2_selection(self) -> str:
        """Return the most recent value for the testmenu"""
        return self.__testmenu2_variable.get()

    def set_testmenu2_selection(self, value: str) -> None:
        """Set the value for the testmenu"""
        return self.__testmenu2_variable.set(value)

    def bind_testmenu2_commands(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for the stratigraphic graph right-click menu

        ttk.OptionMenu doesn not accept commadns to .config, only on the constructor? So in this case the view contains a reference to the callback

        @todo rename testmenu and this method
        """
        self.__testmenu2_callback = callback

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

    def bind_littlecanvas2_callback(self, sequence: str, callback: Callable[[], Optional[Any]]):
        """Bind a single callback to the specified sequence on the littlecanvas2. This is an alternative to an all in one bind method, as the canvas repeatedly gets cleared"""
        self.littlecanvas2.bind(sequence, callback)

    def unbind_littlecanvas2_callback(self, sequence: str):
        """Unbind a single callback to the specified sequence on the littlecanvas2. This is an alternative to an all in one bind method, as the canvas repeatedly gets cleared"""
        self.littlecanvas2.unbind(sequence)

    def bind_littlecanvas2_events(
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
        self.littlecanvas2.bind("<MouseWheel>", callback_wheel)
        self.littlecanvas2.bind("<Button-4>", callback_wheel)  # only with Linux, wheel scroll down
        self.littlecanvas2.bind("<Button-5>", callback_wheel)
        self.littlecanvas2.bind("<Button-3>", callback_rightclick)
        self.littlecanvas2.bind("<Button-1>", callback_move_from)
        self.littlecanvas2.bind("<B1-Motion>", callback_move_to)

    def build_file_menu(self, items: List[Optional[Tuple[str, Callable[[], Optional[Any]]]]]) -> None:
        """Builds the 'file' menu element with labels and callback functions.

        Parameters:
            items: A List of menu entries to add, which may be None to identify a separator, or a tuple containing a label anf callback fucntion.

        Todo:
            Not sure Optional[Any] is required in this type hint?
        """
        # Get a handle to the Menu belonging to the MenuButton
        menubar: ttk.Menubutton = self.file_menubar
        menu: tk.Menu = self.nametowidget(menubar.cget("menu"))
        # Clear existing items
        menu.delete(0, "end")
        # Iterate the items to add to the menu
        for item in items:
            if item is not None:
                # If the item is not None, it should be a Tuple contianing a string label and a callback function
                label, callback = item
                menu.add_command(font="helvetica 12 bold", label=label, command=callback)
            else:
                # Add a separator if the item is None
                menu.add_separator()
        # Mark the menubutton as not disabled
        if len(items) > 0:
            menubar.configure(state=tk.NORMAL)

    def build_view_menu(self, items: List[Optional[Tuple[str, Callable[[], Optional[Any]]]]]) -> None:
        """Builds the 'view' menu element with labels and callback functions.

        Parameters:
            items: A List of menu entries to add, which may be None to identify a separator, or a tuple containing a label anf callback fucntion.

        Todo:
            Not sure Optional[Any] is required in this type hint?
        """
        # Get a handle to the Menu belonging to the MenuButton
        menubar: ttk.Menubutton = self.view_menubar
        menu: tk.Menu = self.nametowidget(menubar.cget("menu"))
        # Clear existing items
        menu.delete(0, "end")
        # Iterate the items to add to the menu
        for item in items:
            if item is not None:
                # If the item is not None, it should be a Tuple contianing a string label and a callback function
                label, callback = item
                menu.add_command(font="helvetica 12 bold", label=label, command=callback)
            else:
                # Add a separator if the item is None
                menu.add_separator()
        # Mark the menubutton as not disabled
        if len(items) > 0:
            menubar.configure(state=tk.NORMAL)

    def build_tool_menu(self, items: List[Optional[Tuple[str, Callable[[], Optional[Any]]]]]) -> None:
        """Builds the 'tools' menu element with labels and callback functions.

        Parameters:
            items: A List of menu entries to add, which may be None to identify a separator, or a tuple containing a label anf callback fucntion.

        Todo:
            Not sure Optional[Any] is required in this type hint?
        """
        # Get a handle to the Menu belonging to the MenuButton
        menubar: ttk.Menubutton = self.tool_menubar
        menu: tk.Menu = self.nametowidget(menubar.cget("menu"))
        # Clear existing items
        menu.delete(0, "end")
        # Iterate the items to add to the menu
        for item in items:
            if item is not None:
                # If the item is not None, it should be a Tuple contianing a string label and a callback function
                label, callback = item
                menu.add_command(font="helvetica 12 bold", label=label, command=callback)
            else:
                # Add a separator if the item is None
                menu.add_separator()
        # Mark the menubutton as not disabled
        if len(items) > 0:
            menubar.configure(state=tk.NORMAL)

    def update_littlecanvas2(self, image):
        """Update the image within the littlecanvas2 element - i.e. the chronological graph.

        Formerly part of PageOne.chornograph_render_post

        @todo type hints
        @todo bindings
        @todo - rename method
        @todo - which of these values are actually needed as class members?
        """
        self.image2 = image  # @todo don't store this in the view.
        #    scale_factor = min(self.littlecanvas2.winfo_width()/self.image_ws.size[0], self.littlecanvas2.winfo_height()/self.image_ws.size[1])
        #    self.image2 = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)

        self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
        self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw", image=self.littlecanvas2.img)

        self.width2, self.height2 = self.image2.size
        #   self.imscale2 = 1.0  # scale for the canvaas image
        self.delta2 = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
        self.imscale2 = min(921 / self.image2.size[0], 702 / self.image2.size[1])
        self.littlecanvas2.scale("all", 0, 0, self.delta2, self.delta2)  # rescale all canvas objects
        self.show_image2()

    def show_image2(self):
        """Show image on the 2nd Canvas

        @todo the logic for this should probably be elsewhere / add parameters?
        @todo rename method"""
        """Show image on the Canvas"""
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
            self.littlecanvas.imagetk2 = self.imagetk2

    def wheel2(self, event):
        """Zoom with mouse wheel for the stratigraphic image canvas

        Formerly (part of) `PageOne.wheel`
        """

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

    def show_testmenu(self, has_image: bool) -> Tuple[Optional[int], Optional[int]]:
        """Show the test menu within the little canvas2 at the cursors' coordinates

        Formerly part of PageOne.onRight

        Parameters:
            has_image: If the littlecanvas2 has been rendered with an image or not.
        """
        # Here we fetch our X and Y coordinates of the cursor RELATIVE to the window
        cursor_x2 = int(self.littlecanvas2.winfo_pointerx() - self.littlecanvas2.winfo_rootx())
        cursor_y2 = int(self.littlecanvas2.winfo_pointery() - self.littlecanvas2.winfo_rooty())

        # Now we define our right click menu canvas
        # And here is where we use our X and Y variables, to place the menu where our cursor is,
        # That's how right click menus should be placed.
        self.testmenu2.place(x=cursor_x2, y=cursor_y2)
        # This is for packing our options onto the canvas, to prevent the canvas from resizing.
        # This is extremely useful if you split your program into multiple canvases or frames
        # and the pack method is forcing them to resize.
        self.testmenu2.pack_propagate(0)
        # Here is our label on the right click menu for deleting a row, notice the cursor
        # value, which will give us a pointy finger when you hover over the option.
        self.testmenu2.config(width=10)

        # Return the scaled x and y coords so the presenter can check if a node was presessed, this was part of PageOne.chrono_nodes
        # @todo improve this separation of concerns
        if has_image:
            x_scal = cursor_x2 + self.transx2
            y_scal = cursor_y2 + self.transy2
            # self.node = self.nodecheck(x_scal, y_scal)
            return x_scal, y_scal
        else:
            return None, None

    def update_hpd_interval(self, USER_INP: str, intervals: List[Tuple[str, str]]) -> None:
        """UI parts of loads hpd intervals into the results page

        Formerly PageOne.get_hpd_interval
        @todo - more refacotring, typehints"""

        hpd_str = ""
        columns = ("context", "hpd_interval")
        self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show="headings")
        self.tree_phases.heading("context", text="Context")
        self.tree_phases.heading("hpd_interval", text=str(USER_INP) + "% HPD interval")
        for contact in intervals:
            self.tree_phases.insert("", tk.END, values=contact)
        self.tree_phases.place(relx=0, rely=0, relwidth=0.99)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
        self.tree_phases.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="nsew")
        self.littlecanvas_a.create_text(150, 80, text=hpd_str, fill="#0A3200")

    def update_hpd_interval_3col(self, intervals: List[Tuple[str, str, str]]) -> None:
        """UI parts of loads hpd intervals into the results page, with 3 clumsn this time?

        Formerly PageOne.get_hpd_interval
        @todo - more refacotring, typehints"""
        columns = ("context_1", "context_2", "hpd_interval")
        self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show="headings")
        # define headings
        self.tree_phases.heading("context_1", text="Context 1")
        self.tree_phases.heading("context_2", text="Context 2")
        self.tree_phases.heading("hpd_interval", text="HPD interval")
        # add data to the treeview
        for contact in intervals:
            self.tree_phases.insert("", tk.END, values=contact)
        self.tree_phases.place(relx=0, rely=0, relwidth=1)

        # add a scrollbar
        scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
        self.tree_phases.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="nsew")

    def append_testmenu2_entry(self, text) -> None:
        """Append an entry to the end of the right click testmenu2.

        @todo - insert instead?
        @todo - edit instead of overwrite self.testmenu2"""
        self.ResultList.append(text)
        self.testmenu2 = ttk.OptionMenu(
            self.littlecanvas2,
            self.__testmenu2_variable,
            self.ResultList[0],
            *self.ResultList,
            command=self.__testmenu2_callback,
        )

    def remove_testmenu2_entry(self, text) -> None:
        """Remove an entry to the end of the right click testmenu2.

        @todo - edit instead of overwrite self.testmenu2"""

        self.ResultList.remove(text)
        self.testmenu2 = ttk.OptionMenu(
            self.littlecanvas2,
            self.__testmenu2_variable,
            self.ResultList[0],
            *self.ResultList,
            command=self.__testmenu2_callback,
        )

    def hide_canvas_plt(self) -> None:
        if self.canvas_plt is not None:
            self.canvas_plt.get_tk_widget().pack_forget()

    def clear_littlecanvas3(self, id: bool = False):
        """Clear the littlecanvas3, always delting results_text, and sometiems littelcanvas3_id
        @todo rename"""
        self.littlecanvas3.delete(self.results_text)
        if id:
            self.littlecanvas3.delete(self.littlecanvas3_id)

    def clear_tree_phases(self) -> None:
        if self.tree_phases is not None:
            for item in self.tree_phases.get_children():
                self.tree_phases.delete(item)

    def update_littlecanvas3(self, results_list: List[str]) -> None:
        """Update the contents of littlecanvas3

        Formerly part of PageOne.chornograph_render_post

        @todo type hints
        @todo bindings
        @todo - rename method
        @todo - which of these values are actually needed as class members?
        """
        self.clear_littlecanvas3()
        cont_canvas_list = ""
        for i in set(results_list):
            cont_canvas_list = cont_canvas_list + str(i) + "\n"
        self.results_text = self.littlecanvas3.create_text(
            5, 10, anchor="nw", text=cont_canvas_list, fill="#0A3200", font=("Helvetica 12 bold")
        )

    def show_canvas_plot(self, fig: Figure) -> None:
        """Add (or reaplce) the visible plot with the provided figure"""
        self.canvas_plt = FigureCanvasTkAgg(fig, master=self.littlecanvas)
        self.canvas_plt.get_tk_widget().place(relx=0, rely=0, relwidth=1)
        self.canvas_plt.draw_idle()

    def show_canvas_plot_with_toolbar(self, fig: Figure) -> None:
        """Add (or reaplce) the visible plot with the provided figure

        @todo - combine with show_canvas_plot, but one uses pack and the other uses place"""
        self.canvas_plt = FigureCanvasTkAgg(fig, master=self.littlecanvas)
        self.canvas_plt.draw()
        # creating the Matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas_plt, self.littlecanvas)
        self.toolbar.update()
        self.canvas_plt.get_tk_widget().pack()
