from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from matplotlib import color_sequences
from matplotlib.colors import hex2color, to_hex

from ..util import contrast_ratio, luminance
from .PopupView import PopupView


class GroupBoxPalette:
    """A sequence of colours used as a palette for the group boxes"""

    __TEXT_COLOURS = {c: luminance(c) for c in [hex2color("#131E29"), hex2color("#F8F8F9")]}

    def __init__(self):
        """Initialise the colour palette using a sequence from matplotlib, with some re-ordering so sequential elements are not matched"""
        tab20 = [(to_hex(c), to_hex(self.__contrasting_color(c))) for c in color_sequences["tab20"]]
        self._colours: list[str] = tab20[::2] + tab20[1::2]
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

        # Set the geometry, which naturally is centred within the parent window
        self.geometry("1500x400")

        self.group_label_dict = {}
        """Dictionary of group boxes/tkinter label elements"""

        self.__group_box_move_callback: Callable[[], Any] = lambda event: None
        """Callback method for when a group box is moved."""

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

        self.maincanvas = tk.Canvas(
            self, bg="#AEC7D6", highlightthickness=0, borderwidth=0, highlightbackground="white"
        )
        self.maincanvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.maincanvas.update()

        self.backcanvas = tk.Canvas(
            self.maincanvas, bg="white", highlightthickness=0, borderwidth=0, highlightbackground="white"
        )
        self.backcanvas.place(relx=0.135, rely=0.9, relheight=0.13, relwidth=0.53)
        self.backcanvas.create_line(150, 30, 600, 30, arrow=tk.LAST, width=3)

        self.time_label = tk.Label(self.maincanvas, text="Time")
        self.time_label.config(bg="white", font=("helvetica", 12, "bold"), fg="#2f4858", wraplength=130)
        self.time_label.place(relx=0.32, rely=0.91, relwidth=0.12, relheight=0.05)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.place(relx=0.135, rely=0.05, relheight=0.85, relwidth=0.53)
        self.canvas.update()

        self.instruc_label = tk.Label(
            self.maincanvas,
            text="Instructions: \n Place the oldest group in the bottom left corner then for each subseqent group, place it directly above and move it to be overlapping, abutting or to have a gap.",
        )
        self.instruc_label.config(bg="white", font=("helvetica", 12, "bold"), fg="#2f4858", wraplength=130)
        self.instruc_label.place(relx=0.01, rely=0.05, relwidth=0.12, relheight=0.85)

        self.instruc_label2 = tk.Label(self.maincanvas, text="User defined group relationships")
        self.instruc_label2.config(bg="white", font=("helvetica", 12, "bold"), fg="#2f4858")
        self.instruc_label2.place(relx=0.67, rely=0.17, relwidth=0.32, relheight=0.1)

        self.confirm_button = tk.Button(
            self.maincanvas,
            text="Confirm groups",
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
            command=lambda: self.__confirm_callback(),
        )
        self.confirm_button.place(relx=0.8, rely=0.91)

        # Add an empty table
        self.relationships_table_frame = tk.LabelFrame(self.maincanvas, bg="white")
        self.relationships_table_frame.columnconfigure(0, weight=1)
        self.relationships_table_frame.rowconfigure(0, weight=1)
        self.relationships_table = ttk.Treeview(self.relationships_table_frame)
        self.relationships_table_frame.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.relationships_table.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)

        # member variables which will store other tkinter buttons once confirm has been pressed.
        self.render_button = None
        self.change_button = None

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
        for idx, (group_label, (x, y, w, h)) in enumerate(group_boxes_xywh.items()):
            label = tk.Label(self.canvas, text=str(group_label))
            bg, fg = self.COLOURS[idx]
            label.config(bg=bg, fg=fg, font=("helvetica", 14, "bold"))
            label.bind("<B1-Motion>", lambda event: self.__group_box_move_callback(event))
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

    def update_relationships_table(self, relationships_dict: dict[tuple[str, str], str | None]) -> None:
        """Update the table of group relationships.

        This is the 3 column version, for the confirmation step in the residual checking process.

        Formerly part of `popupwindow3.get_coords`

        Parameters:
            relationship_dict: A dictionary of relationship types for each directed group relationship
        """

        # Destroy the old table
        self.relationships_table.destroy()
        self.relationships_table_frame.destroy()

        # Create the new table and populate with the 3 col data.
        self.relationships_table_frame = tk.LabelFrame(self.maincanvas, bg="white")
        self.relationships_table_frame.columnconfigure(0, weight=1)
        self.relationships_table_frame.rowconfigure(0, weight=1)
        self.relationships_table = ttk.Treeview(self.relationships_table_frame)
        self.relationships_table_frame.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.relationships_table.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)
        self.relationships_table["columns"] = ["Younger group", "Older group", "Relationship"]
        for col in self.relationships_table["columns"]:
            self.relationships_table.column(col, anchor="w", width=100)
            self.relationships_table.heading(col, text=col, anchor="w")

        for index, ((younger, older), relationship) in enumerate(relationships_dict.items()):
            row = [younger, older, str(relationship) if relationship is not None else ""]

            self.relationships_table.insert("", tk.END, text=index, values=row)
        self.relationships_table["show"] = "headings"

    def bind_group_box_on_move(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for moving the group boxes.

        This is set on a (private) view class member, to avoid havnig to call this method again if the group boxes are ever re-generated.
        """
        if callback is not None:
            self.__group_box_move_callback = callback

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

    def on_confirm(self) -> None:
        """Update the view to show the UI for when after the confirm button has been pressed.

        This destroys then re-creates elements.

        Formerly part of `popupWindow3.get_coords`
        """
        self.instruc_label.destroy()
        self.confirm_button.destroy()
        self.relationships_table.destroy()
        self.relationships_table_frame.destroy()
        self.maincanvas.columnconfigure(0, weight=1)
        self.maincanvas.rowconfigure(0, weight=1)
        self.maincanvas.update()
        self.instruc_label = tk.Label(
            self.maincanvas,
            text="If you're happy with your group relationships, click the Render Chronological Graph button.",
        )
        self.instruc_label.config(bg="white", font=("helvetica", 12, "bold"), wraplength=130)
        self.instruc_label.place(relx=0.01, rely=0.05, relwidth=0.12, relheight=0.85)

        self.render_button = tk.Button(
            self.maincanvas,
            text="Render Chronological graph",
            command=lambda: self.__render_callback(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.render_button.place(relx=0.75, rely=0.91)
        self.change_button = tk.Button(
            self.maincanvas,
            text="Change relationships",
            command=lambda: self.__change_callback(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.change_button.place(relx=0.55, rely=0.91)

    def on_back(self) -> None:
        """Update the view to show the pre-confirmation state

        Formerly `popupWindow3.back_func`
        """
        self.render_button.destroy()
        self.instruc_label.destroy()
        self.change_button.destroy()
        self.maincanvas.update()
        self.confirm_button = tk.Button(
            self.maincanvas,
            text="Confirm groups",
            command=lambda: self.__confirm_callback(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.confirm_button.place(relx=0.8, rely=0.91)
        self.instruc_label = tk.Label(
            self.maincanvas,
            text="Instructions: \n Place the oldest group in the bottom left corner then for each subseqent group, place it directly above and move it to be overlapping, abutting or to have a gap.",
        )
        self.instruc_label.config(bg="white", font=("helvetica", 12, "bold"), wraplength=130)
        self.instruc_label.place(relx=0.01, rely=0.05, relwidth=0.18, relheight=0.85)
