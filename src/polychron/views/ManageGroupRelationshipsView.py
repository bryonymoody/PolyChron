from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
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

        # Set the geometry, which naturally is centered within the parent window
        self.geometry("1500x400")

        self.group_label_dict = {}
        """Dictionary of phases boxes/tkinter label elements"""

        self.__phase_box_move_callback: Callable[[], Any] = lambda event: None
        """Callback method for when a phase box is moved."""

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
        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg="white")
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.tree.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)

        # member variables which will store other tkinter buttons once confirm has been pressed.
        self.render_button = None
        self.change_button = None

        self.COLOURS = GroupBoxPalette()
        """A palette of colours and corresponding text colours for the boxes used for groups. If more colours are required than available the palette will wrap"""

    def create_phase_boxes(self, group_labels: List[Tuple[str, str]] | None) -> None:
        """Create a box within the canvas for each provided phase label"""
        self.group_label_dict = {}

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        # If the width and height info was not available, fallback to the requested dimensions
        if w == 1 and h == 1:
            w, h = self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight()
        m = len(group_labels)

        for idx, group_label in enumerate(group_labels):
            label = tk.Label(self.canvas, text=str(group_label))
            bg, fg = self.COLOURS[idx]
            label.config(bg=bg, fg=fg, font=("helvetica", 14, "bold"))
            label.bind("<B1-Motion>", lambda event: self.__phase_box_move_callback(event))
            label.place(
                x=0.05 * w + (w / (2 * m)) * idx,
                y=0.85 * h - ((0.95 * h) / m) * idx,
                relwidth=0.76 / m,
                relheight=min(0.1, 0.9 / m),
            )
            self.group_label_dict[group_label] = label

    def get_phase_boxes(self) -> Dict[str, tk.Label]:
        """Get the dictionary of tk label objects for each phase label"""
        return self.group_label_dict

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

    def update_tree_2col(self, group_relationships: List[Tuple[str, str]] | None) -> None:
        """Update the table of group relationships to the value(s) provided by the user

        This is the 2 column version, for the first step in the residual checking process.

        Parameters:
            group_relationships: A list of tuples containing relationships between groups, (above, below)
        """
        # Prep a local dataframe for presentation
        df = pd.DataFrame(group_relationships, columns=["Younger group", "Older group"])
        cols = list(df.columns)

        # Destroy the old table
        self.tree.destroy()
        self.frmtreeborder.destroy()

        # Create and populate the new table
        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg="white")
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.tree.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)
        self.tree["columns"] = cols
        for i in cols:
            self.tree.column(i, anchor="w")
            self.tree.heading(i, text=i, anchor="w")
        for index, row in df.iterrows():
            self.tree.insert("", 0, text=index, values=list(row))
        self.tree["show"] = "headings"

    def update_tree_3col(self, menudict: Dict[Tuple[str, str], object]) -> None:
        """Update the table of group relationships to the value(s) provided by the user

        This is the 3 column version, for the confirmation step in the residual checking process.

        Formerly part of popupwindow3.get_coords"""

        # Prepare the new 3 column dataframe
        col1, col2, col3 = [], [], []
        rels_df = pd.DataFrame()
        for i in menudict.keys():
            col1.append(i[0])
            col2.append(i[1])
            col3.append(str(menudict[i]))
        rels_df["Younger group"] = col1
        rels_df["Older group"] = col2
        rels_df["Relationship"] = col3
        cols = list(rels_df.columns)

        # Destroy the old table
        self.tree.destroy()
        self.frmtreeborder.destroy()

        # Create the new table and populate with the 3 col data.
        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg="white")
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.tree.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)
        self.tree["columns"] = cols
        for i in cols:
            self.tree.column(i, anchor="w", width=100)
            self.tree.heading(i, text=i, anchor="w")

        for index, row in rels_df.iterrows():
            self.tree.insert("", 0, text=index, values=list(row))
        self.tree["show"] = "headings"

    def bind_phase_box_on_move(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for moving the phase boxes.

        This is set on a (private) view class member, to avoid havnig to call this method again if the phase boxes are ever re-generated.
        """
        if callback is not None:
            self.__phase_box_move_callback = callback

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
        self.tree.destroy()
        self.frmtreeborder.destroy()
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
