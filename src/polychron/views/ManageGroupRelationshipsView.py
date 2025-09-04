from __future__ import annotations

import math
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Any, Callable, Literal

import numpy as np
from matplotlib import color_sequences, colormaps
from matplotlib.colors import hex2color, to_hex

from ..util import contrast_ratio, luminance
from .PopupView import PopupView


class GroupBoxPalette:
    """A sequence of colours used as a palette for the group boxes"""

    __TEXT_COLOURS = {c: luminance(c) for c in [hex2color("#131E29"), hex2color("#F8F8F9")]}

    def __init__(self, palette: Literal["pastel", "tab20", "cubehelix"] = "pastel"):
        """Initialise the colour palette using a sequence from matplotlib, with some re-ordering so sequential elements are not matched"""
        if palette == "pastel":
            colours = [
                (to_hex(c), to_hex(self.__contrasting_color(c)))
                for c in color_sequences["Pastel1"] + color_sequences["Pastel2"]
            ]
        elif palette == "tab20":
            tab20 = [(to_hex(c), to_hex(self.__contrasting_color(c))) for c in color_sequences["tab20"]]
            colours = tab20[::2] + tab20[1::2]
        else:  # if palette == "cubehelix":
            # interleaved discrete samples from the continuous colour map
            cmap = colormaps["cubehelix"](np.linspace(0, 1, 40))
            interleaved = [item for i in range(5) for item in cmap[i::5]]
            colours = [(to_hex(c), to_hex(self.__contrasting_color(c))) for c in interleaved]
        self._colours: list[str] = colours
        """The sequence of colours from tab20 and a corresponding contrasting text colour, but reordered a little"""

    def __len__(self) -> int:
        """Get the number of colours in the palette

        Returns:
            The number of colours in the palette
        """
        return len(self._colours)

    def __getitem__(self, idx: int) -> tuple[str, str]:
        """Get the pair of colours from the index, containing the background colour, and the contrasting label colour

        parameters:
            idx: the index / key of the item to access

        returns:
            The pair of colours at the specified index in hex codes"""
        return self._colours[idx % len(self)]

    @classmethod
    def __contrasting_color(cls, rgb: tuple[float, float, float]) -> tuple[float, float, float]:
        """Given an rgb-tuple of floats in the range [0,1], return the colour with the most contrast from the list of available text colours.

        Ideally a contrast ratio threshold of 4.5:1 or 3:1 would also be required following accessibility guidelines, but that is not possible for all colour palettes in distributed with matplotlib

        Parameters:
            rgb: a 3-tuple of normalised colour channels

        Returns:
            a 3-tuple of normalised colour channels with sufficient contrast to the base colour
        """
        # Get the luminance of the rgb colour (including gamma correction)
        l = luminance(rgb)

        # Calculate contrast ratio with each text colour
        contrasts = {text: contrast_ratio(l, text_l) for text, text_l in cls.__TEXT_COLOURS.items()}

        # Sort the list of contrasting colours and ratios by contrast value
        sorted_text_colours = sorted(contrasts.items(), key=lambda item: item[1], reverse=True)

        # Return the text colour with the larger contrast ratio
        return sorted_text_colours[0][0]


class ManageGroupRelationshipsView(PopupView):
    """View for managing group relationships

    Formerly part of `popupWindow3`, Part of the Rendering chronological graph process
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # Set the popup title
        self.title("Adding group relationships")

        # Set the geometry, which naturally is centred within the parent window, to the parents window size if possible and not too small, otherwise a sensible minimum that should be usable on 720p displays or half a 1080p
        geometry = "940x700"
        try:
            parent_geometry = self.parent.winfo_toplevel().geometry()
            parent_x, parent_y = map(int, parent_geometry.split("+")[0].split("x"))
            x, y = map(int, geometry.split("x"))
            if parent_x > x or parent_y > y:
                geometry = f"{parent_x}x{parent_y}"
        except Exception:
            pass
        popup_width = int(geometry.split("x")[0])
        popup_height = int(geometry.split("x")[1])
        # Set the window geometry
        self.centered_geometry(popup_width, popup_height)
        # Set the minimum window geometry, so the popup can be scaled up to make more room, but cannot be shrunk
        self.wm_minsize(popup_width, popup_height)

        self.group_label_dict = {}
        """Dictionary of group boxes/tkinter label elements"""

        self.__group_box_mouse_press_callback: Callable[[], Any] = lambda event: None
        """Callback method for mouse press events on group box"""

        self.__group_box_mouse_move_callback: Callable[[], Any] = lambda event: None
        """Callback method for mouse move events on group box"""

        self.__group_box_mouse_release_callback: Callable[[], Any] = lambda event: None
        """Callback method for mouse release events on group box"""

        self.__group_box_mouse_cursor = ""
        """The mouse cursor to display on group boxes when they are movable"""

        self.__confirm_callback: Callable[[], Any] = lambda: None
        """Callback method for when the confirm button is pressed. 
        
        Stored in the view to allow deletion and recreation of the confirm button.
        """

        self.__render_callback: Callable[[], Any] = lambda: None
        """Callback method for when the render button is pressed. 
        
        Stored in the view to allow deletion and recreation of the render button.
        """

        self.__change_callback: Callable[[], Any] = lambda: None
        """Callback method for when the change button is pressed. 
        
        Stored in the view to allow deletion and recreation of the change button.
        """

        # Configure the popupwindow to have a single expandable grid for the background canvas
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add a blue shaded background which is the full size of the popup window
        self.background_frame = tk.Frame(
            self, bg="white", highlightthickness=0, borderwidth=0, highlightbackground="white"
        )
        self.background_frame.grid(row=0, column=0, sticky="nsew")

        # Using the (intended) size of the popup window, set the size things in the right hand column.
        MIN_RIGHT_COL_WIDTH = 470
        right_col_width = max(0.30 * popup_width, MIN_RIGHT_COL_WIDTH)
        # setup the grid of the background frame to be 2 columns and 3 rows
        self.background_frame.grid_columnconfigure(0, weight=2, minsize=right_col_width)
        self.background_frame.grid_columnconfigure(1, weight=0, minsize=right_col_width)
        self.background_frame.grid_rowconfigure(0, weight=0)
        self.background_frame.grid_rowconfigure(1, weight=5)
        self.background_frame.grid_rowconfigure(2, weight=0)

        # Place the canvas for boxes spanning the 0th and 1th rows, in the 0th column of the background frame,
        self.canvas = tk.Canvas(self.background_frame, bg="#f8f8f9", highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=8, pady=8)
        self.canvas.update()

        # Place a white canvas in the 2nd row of the 0th column, as the x axis. For now it will be empty until all elements are drawn.
        self.white_canvas = tk.Canvas(
            self.background_frame,
            bg="white",
            highlightthickness=0,
            borderwidth=0,
            highlightbackground="white",
            height=50,
        )
        self.white_canvas.grid(row=2, column=0, sticky="nsew")
        # When the white canvas is resized, re-draw the arrow.
        self.white_canvas.bind("<Configure>", lambda _: self.draw_arrow())

        # Add a label in the centre of the white canvas
        self.time_label = tk.Label(self.white_canvas, text="Time")
        self.time_label.config(bg="white", font=("helvetica", 12, "bold"), fg="#2f4858")
        self.time_label.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Place a tklabel containing instructions in the top right of the background frame / grid
        self._instructions_text_step_one = "Place the oldest group in the bottom left corner.\nPlace each subsequent group directly above and move it to be overlapping, abutting or to have a gap."
        self._instructions_text_step_two = (
            "If you're happy with your group relationships, click the 'Render chronological graph' button."
        )

        self.instructions_frame = tk.LabelFrame(self.background_frame, bg="white", text="Instructions", height=200)
        self.instructions_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.instructions_frame.grid_columnconfigure(1, weight=1)
        self.instructions_frame.grid_rowconfigure(1, weight=1)
        self.instructions = tk.Label(
            self.instructions_frame, text=self._instructions_text_step_one, padx=8, pady=8, justify="left"
        )
        self.instructions.config(
            bg="white", font=("helvetica", 12, "bold"), fg="#2f4858", wraplength=right_col_width - 32
        )
        self.instructions.grid(row=0, column=0, sticky="nsew")

        # Place a frame for a table of relationships + title in the mid-right
        self.relationships_table_frame = tk.LabelFrame(
            self.background_frame, bg="white", text="User defined group relationships"
        )
        self.relationships_table_frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self.relationships_table_frame.columnconfigure(0, weight=1)
        self.relationships_table_frame.rowconfigure(0, weight=0)
        self.relationships_table_frame.rowconfigure(1, weight=1)

        # Place a tree view (table) in the frame
        self.relationships_table = ttk.Treeview(self.relationships_table_frame)
        self.relationships_table.grid(column=0, row=1, sticky="nsew", padx=8, pady=8)
        self.relationships_table["columns"] = ["Younger group", "Older group", "Relationship"]
        for col in self.relationships_table["columns"]:
            self.relationships_table.column(
                col, anchor="w", width=math.floor(self.relationships_table.winfo_width() / 3)
            )
            self.relationships_table.heading(col, text=col, anchor="w")
        self.relationships_table["show"] = "headings"

        # Place a frame for buttons in the bottom-right
        self.button_frame = tk.Frame(self.background_frame, bg="white", padx=8, pady=8)
        self.button_frame.grid(row=2, column=1, sticky="nsew")
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.rowconfigure(0, weight=1)

        # Place a button in the bottom right  of the background frame
        self.confirm_button = tk.Button(
            self.button_frame,
            text="Confirm groups",
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
            command=lambda: self.__confirm_callback(),
        )
        self.confirm_button.grid(row=0, column=1, sticky="nse")

        # Create but then hide from view the other buttons
        self.render_button = tk.Button(
            self.button_frame,
            text="Render chronological graph",
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
            command=lambda: self.__render_callback(),
        )
        self.render_button.grid(row=0, column=1, sticky="nse")
        self.render_button.grid_remove()

        self.change_button = tk.Button(
            self.button_frame,
            text="Change relationships",
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
            command=lambda: self.__change_callback(),
        )
        self.change_button.grid(row=0, column=0, sticky="nsw")
        self.change_button.grid_remove()

        # Ensure UI dimensions are updated prior to the constructor completing, so the canvas size is correct in get_group_canvas_dimensions
        self.update_idletasks()

        self.COLOURS = GroupBoxPalette()
        """A palette of colours and corresponding text colours for the boxes used for groups. If more colours are required than available the palette will wrap"""

    def get_group_canvas_dimensions(self) -> tuple[int, int]:
        """Get the dimensions of the group canvas, so the presenter can compute initial box placement based on known relationships

        Returns:
            A tuple (width, height) containing the dimensions of the canvas area.
        """
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        # If the width and height info was not available, fallback to the requested dimensions
        if w == 1 and h == 1:
            w, h = self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight()
        return w, h

    def create_group_boxes(self, group_boxes_xywh: dict[str, tuple[float, float, float, float]]) -> None:
        """Create a box within the canvas for each group label, with an initial location provided by the presenter.

        Colours will be selected from a palette.

        Parameters:
            group_boxes_xywh: an (ordered) dictionary of boxes `(x, y, w, h)` to create from the presenter
        """
        self.group_label_dict = {}
        font_options = [
            tkfont.Font(family="helvetica", size=14, weight="bold"),
            tkfont.Font(family="helvetica", size=12, weight="bold"),
            tkfont.Font(family="helvetica", size=10, weight="bold"),
            tkfont.Font(family="helvetica", size=8, weight="bold"),
        ]

        for idx, (group_label, (x, y, w, h)) in enumerate(group_boxes_xywh.items()):
            # Measure the label in each font size, until the text fits, or the last option is reached
            for font in font_options:
                if font.measure(group_label) <= w:
                    break

            bg, fg = self.COLOURS[idx]

            label = tk.Label(self.canvas, text=str(group_label), bg=bg, fg=fg, font=font)
            label.bind("<ButtonPress-1>", lambda event: self.__group_box_mouse_press_callback(event))
            label.bind("<B1-Motion>", lambda event: self.__group_box_mouse_move_callback(event))
            label.bind("<ButtonRelease-1>", lambda event: self.__group_box_mouse_release_callback(event))
            label.bind("<Enter>", lambda event: event.widget.config(cursor=self.__group_box_mouse_cursor))
            label.bind("<Leave>", lambda event: event.widget.config(cursor=""))
            label.place(x=x, y=y, width=w, height=h)
            self.group_label_dict[group_label] = label

    def get_group_box_properties(self) -> dict[str, tuple[float, float, float, float]]:
        """Get a dictionary containing the `(x, y, w, h)` for each group box

        Returns:
            A dictionary indexed by the group label with the `(x, y, w, h)` for each box.
        """
        return {
            group: (tk_label.winfo_x(), tk_label.winfo_y(), tk_label.winfo_width(), tk_label.winfo_height())
            for group, tk_label in self.group_label_dict.items()
        }

    def update_box_coords(self, boxes: dict[str, tuple[float, float]]):
        """Update the coordinates and size for each group box

        Parameters:
            boxes: A dictionary indexed by the group label with the `(x, y)` for each box.
        """
        # Iterate the boxes, updating the position / dimensions based on the provided values
        for group, tk_label in self.group_label_dict.items():
            if group in boxes:
                new_x, new_y = boxes[group]
                tk_label.place(x=new_x, y=new_y)

        # ensure the canvas is updated for rendering / updated coordinates
        self.update_canvas()

    def update_canvas(self) -> None:
        """Update the canvas to ensure coordinates are correct?"""
        self.canvas.update()

    def draw_arrow(self) -> None:
        """draw the x-axis arrow / label on the white canvas"""
        self.white_canvas.update()
        self.white_canvas.delete("all")

        canvas_w, canvas_h = self.white_canvas.winfo_width(), self.white_canvas.winfo_height()
        # Add a line and a label to the canvas, which is vertically centred with some horizontal space
        X_MARGIN_FACTOR = 0.15
        y = canvas_h / 2
        x0 = X_MARGIN_FACTOR * canvas_w
        x1 = canvas_w - x0
        self.white_canvas.create_line(x0, y, x1, y, arrow=tk.LAST, width=3)

    def update_relationships_table(self, relationships_dict: dict[tuple[str, str], str | None]) -> None:
        """Update the table of group relationships.

        This is the 3 column version, for the confirmation step in the residual checking process.

        Formerly part of `popupwindow3.get_coords`

        Parameters:
            relationship_dict: A dictionary of relationship types for each directed group relationship
        """
        # Clear the treeview
        self.relationships_table.delete(*self.relationships_table.get_children())

        # Update the data in the table
        for index, ((younger, older), relationship) in enumerate(relationships_dict.items()):
            row = [younger, older, str(relationship) if relationship is not None else ""]
            self.relationships_table.insert("", tk.END, text=index, values=row)

    def bind_group_box_mouse_events(
        self,
        on_press: Callable[[], Any] | None,
        on_move: Callable[[], Any] | None,
        on_release: Callable[[], Any] | None,
        cursor: Literal["", "fleur"] | None,
    ) -> None:
        """Bind the callback for mouse events to move group boxes.

        This is set on a (private) view class members, to avoid having to call this method again if the group boxes are ever re-generated.

        Parameters:
            on_press: Callback function for mouse press events on the group box labels
            on_move: Callback function for mouse move events on the group box labels
            on_release: Callback function for mouse release events on the group box labels
            cursor: The tkinter cursor string to use when the mouse is over the group box labels. Use 'fluer' when the boxes can be dragged.
        """
        if on_press is not None:
            self.__group_box_mouse_press_callback = on_press
        if on_move is not None:
            self.__group_box_mouse_move_callback = on_move
        if on_release is not None:
            self.__group_box_mouse_release_callback = on_release

        # Also set the cursor to use for the group boxes
        self.__group_box_mouse_cursor = cursor

    def bind_confirm_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the confirm_button is pressed"""
        if callback is not None:
            self.__confirm_callback = callback

    def bind_render_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the render_button is pressed"""
        if callback is not None:
            self.__render_callback = callback

    def bind_change_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the change_button is pressed"""
        if callback is not None:
            self.__change_callback = callback

    def layout_step_two(self) -> None:
        """Update the view to show the UI for when after the confirm button has been pressed.

        This updates updates some text and changes which buttons are visible

        Formerly part of `popupWindow3.get_coords`
        """
        # Update the instructions text
        self.instructions.configure(
            text=self._instructions_text_step_two,
        )

        # Hide the confirm button
        self.confirm_button.grid_remove()

        # Show the render and change buttons.
        self.render_button.grid()
        self.change_button.grid()

    def layout_step_one(self) -> None:
        """Update the view to show the pre-confirmation state

        This updates updates some text and changes which buttons are visible


        Formerly `popupWindow3.back_func`
        """

        # Update the instructions text
        self.instructions.configure(text=self._instructions_text_step_one)

        # Hide the render and change buttons.
        self.render_button.grid_remove()
        self.change_button.grid_remove()

        # Show the confirm button
        self.confirm_button.grid()
