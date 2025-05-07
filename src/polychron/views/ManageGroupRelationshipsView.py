import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd

from .BasePopupView import BasePopupView


class ManageGroupRelationshipsView(BasePopupView):
    """View for managing group relationships

    Formerly part of `popupWindow3`, Part of the Rendering chronological graph process

    @todo - make this a popup rather than child of parent?
    """

    def __init__(self, parent: tk.Frame):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # Set the popup title
        self.title("Adding group relationships")

        # Set the geometry, which naturally is centered within the parent window
        self.geometry("1500x400")

        # Ensure this window is on top
        self.attributes("-topmost", "true")  # @todo maybe remove.

        self.label_dict = {}
        """Dictionary of phases boxes/tkinter label elements"""

        self.__phase_box_move_callback: Callable[[], Optional[Any]] = lambda event: None
        """Callback method for when a phase box is moved."""

        self.__confirm_callback: Callable[[], Optional[Any]] = lambda: None
        """Callback method for when the confirm button is pressed. 
        
        Stored in the view to allow deletion and recreation of the confirm button.
        @todo consider if moving 2 views would be cleaner?"""

        self.__render_callback: Callable[[], Optional[Any]] = lambda: None
        """Callback method for when the render button is pressed. 
        
        Stored in the view to allow deletion and recreation of the render button.
        @todo consider if moving 2 views would be cleaner?"""

        self.__change_callback: Callable[[], Optional[Any]] = lambda: None
        """Callback method for when the change button is pressed. 
        
        Stored in the view to allow deletion and recreation of the change button.
        @todo consider if moving 2 views would be cleaner?"""

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

        # @todo - less hardcoded version of this and start wrapping iff too many groups?
        self.COLORS = [
            "LavenderBlush2",
            "powder blue",
            "LavenderBlush3",
            "LemonChiffon4",
            "dark khaki",
            "LightGoldenrod1",
            "aquamarine2",
            "hot pink",
            "DarkOrchid4",
            "pale turquoise",
            "LightSteelBlue2",
            "DeepPink4",
            "firebrick4",
            "khaki4",
            "turquoise3",
            "alice blue",
            "DarkOrange4",
            "LavenderBlush4",
            "misty rose",
            "pink1",
            "OrangeRed2",
            "chocolate2",
            "OliveDrab2",
            "LightSteelBlue3",
            "firebrick2",
            "dark orange",
            "ivory2",
            "yellow2",
            "DeepPink3",
            "aquamarine",
            "LightPink2",
            "DeepSkyBlue2",
            "LightCyan4",
            "RoyalBlue3",
            "SeaGreen3",
            "SlateGray1",
            "IndianRed3",
            "DarkGoldenrod3",
            "HotPink1",
            "navy",
            "tan2",
            "orange4",
            "tomato",
            "LightSteelBlue1",
            "coral1",
            "MediumOrchid4",
            "light grey",
            "DarkOrchid3",
            "RosyBrown2",
            "LightSkyBlue1",
            "medium sea green",
            "deep pink",
            "OrangeRed3",
            "sienna2",
            "thistle2",
            "linen",
            "tan4",
            "bisque2",
            "MediumPurple4",
            "DarkSlateGray4",
            "mint cream",
            "sienna3",
            "lemon chiffon",
            "ivory3",
            "chocolate1",
            "peach puff",
            "DeepSkyBlue3",
            "khaki2",
            "SlateGray2",
            "dark turquoise",
            "deep sky blue",
            "light sky blue",
            "lime green",
            "yellow",
            "burlywood3",
            "tomato4",
            "orange3",
            "wheat2",
            "olive drab",
            "brown3",
            "burlywood1",
            "LightPink1",
            "light cyan",
            "saddle brown",
            "SteelBlue3",
            "SpringGreen3",
            "goldenrod4",
            "dark salmon",
            "DodgerBlue3",
            "MediumPurple3",
            "azure2",
            "lavender blush",
            "SteelBlue4",
            "honeydew3",
            "LightBlue1",
            "DeepSkyBlue4",
            "medium aquamarine",
            "turquoise1",
            "thistle",
            "DarkGoldenrod2",
            "wheat3",
            "LemonChiffon2",
            "turquoise",
            "light sea green",
            "maroon3",
            "green4",
            "SlateBlue1",
            "DarkOliveGreen3",
            "dark violet",
            "LightYellow3",
            "DarkGoldenrod1",
            "PeachPuff3",
            "DarkOrange1",
            "goldenrod2",
            "goldenrod1",
            "SkyBlue4",
            "ivory4",
            "DarkSeaGreen3",
            "aquamarine4",
            "VioletRed3",
            "orange red",
            "CadetBlue3",
            "DarkSlateGray2",
            "seashell2",
            "DarkOliveGreen4",
            "SkyBlue2",
            "DarkOrchid2",
            "maroon1",
            "orchid1",
            "red3",
            "LightSkyBlue4",
            "HotPink4",
            "LightBlue2",
            "coral3",
            "magenta4",
            "bisque4",
            "SteelBlue1",
            "cornsilk3",
            "dark sea green",
            "RosyBrown3",
            "salmon3",
            "NavajoWhite2",
            "PaleTurquoise4",
            "SteelBlue2",
            "OliveDrab1",
            "ghost white",
            "HotPink3",
            "salmon",
            "maroon",
            "khaki3",
            "AntiqueWhite1",
            "PaleVioletRed2",
            "maroon2",
            "cyan3",
            "MistyRose4",
            "thistle3",
            "gold3",
            "tomato3",
            "tan1",
            "LightGoldenrod3",
            "blue violet",
            "tomato2",
            "RoyalBlue4",
            "pink3",
            "cadet blue",
            "slate gray",
            "medium slate blue",
            "PaleGreen3",
            "DodgerBlue2",
            "LightSkyBlue3",
            "lawn green",
            "PaleGreen1",
            "forest green",
            "thistle1",
            "snow",
            "LightSteelBlue4",
            "medium violet red",
            "pink2",
            "PaleVioletRed4",
            "VioletRed1",
            "gainsboro",
            "navajo white",
            "DarkOliveGreen1",
            "IndianRed2",
            "RoyalBlue2",
            "dark olive green",
            "AntiqueWhite3",
            "DarkSlateGray1",
            "LightSalmon3",
            "salmon4",
            "plum3",
            "orchid3",
            "azure",
            "bisque3",
            "turquoise4",
            "SeaGreen1",
            "sienna4",
            "pink",
            "MediumOrchid1",
            "thistle4",
            "PaleVioletRed3",
            "blanched almond",
            "DarkOrange2",
            "royal blue",
            "blue2",
            "chartreuse4",
            "LightGoldenrod4",
            "NavajoWhite4",
            "dark orchid",
            "plum1",
            "SkyBlue1",
            "OrangeRed4",
            "khaki",
            "PaleGreen2",
            "yellow4",
            "maroon4",
            "turquoise2",
            "firebrick3",
            "bisque",
            "LightCyan2",
            "burlywood4",
            "PaleTurquoise3",
            "azure4",
            "gold",
            "yellow3",
            "chartreuse3",
            "RosyBrown1",
            "white smoke",
            "PaleVioletRed1",
            "papaya whip",
            "medium spring green",
            "AntiqueWhite4",
            "SlateGray4",
            "LightYellow4",
            "coral2",
            "MediumOrchid3",
            "CadetBlue2",
            "LightBlue3",
            "snow2",
            "purple1",
            "magenta3",
            "OliveDrab4",
            "DarkOrange3",
            "seashell3",
            "magenta2",
            "green2",
            "snow4",
            "DarkSeaGreen4",
            "slate blue",
            "PaleTurquoise1",
            "red2",
            "LightSkyBlue2",
            "snow3",
            "green yellow",
            "DeepPink2",
            "orange2",
            "cyan",
            "light goldenrod",
            "light pink",
            "honeydew4",
            "RoyalBlue1",
            "sea green",
            "pale violet red",
            "AntiqueWhite2",
            "blue",
            "LightSalmon2",
            "SlateBlue4",
            "orchid4",
            "dark slate gray",
            "dark slate blue",
            "purple",
            "chartreuse2",
            "khaki1",
            "LightBlue4",
            "light yellow",
            "indian red",
            "VioletRed2",
            "gold4",
            "light goldenrod yellow",
            "rosy brown",
            "IndianRed4",
            "azure3",
            "orange",
            "VioletRed4",
            "salmon2",
            "SeaGreen2",
            "pale goldenrod",
            "pale green",
            "plum2",
            "dark green",
            "coral4",
            "LightGoldenrod2",
            "goldenrod3",
            "NavajoWhite3",
            "MistyRose2",
            "wheat1",
            "medium turquoise",
            "floral white",
            "red4",
            "firebrick1",
            "burlywood2",
            "DarkGoldenrod4",
            "goldenrod",
            "sienna1",
            "MediumPurple1",
            "purple2",
            "LightPink4",
            "dim gray",
            "LemonChiffon3",
            "light steel blue",
            "seashell4",
            "brown1",
            "wheat4",
            "MediumOrchid2",
            "DarkOrchid1",
            "RosyBrown4",
            "blue4",
            "cyan2",
            "salmon1",
            "MistyRose3",
            "chocolate3",
            "light salmon",
            "coral",
            "honeydew2",
            "light blue",
            "sandy brown",
            "LightCyan3",
            "brown2",
            "midnight blue",
            "CadetBlue1",
            "LightYellow2",
            "cornsilk4",
            "cornsilk2",
            "SpringGreen4",
            "PeachPuff4",
            "PaleGreen4",
            "SlateBlue2",
            "orchid2",
            "purple3",
            "light slate blue",
            "purple4",
            "lavender",
            "cornflower blue",
            "CadetBlue4",
            "DodgerBlue4",
            "SlateBlue3",
            "DarkSlateGray3",
            "medium orchid",
            "gold2",
            "pink4",
            "DarkOliveGreen2",
            "spring green",
            "dodger blue",
            "IndianRed1",
            "violet red",
            "MediumPurple2",
            "old lace",
            "LightSalmon4",
            "brown4",
            "SpringGreen2",
            "yellow green",
            "plum4",
            "SlateGray3",
            "steel blue",
            "HotPink2",
            "medium purple",
            "LightPink3",
            "PeachPuff2",
            "sky blue",
            "dark goldenrod",
            "PaleTurquoise2",
        ]
        """List of tkinter string colours used for phase boxes."""

    def create_phase_boxes(self, phase_labels: Optional[List[Tuple[str, str]]]) -> None:
        """Create a box within the canvas for each provided phase label"""
        # @todo - propperly clear any existing phase labels
        self.label_dict = {}

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        m = len(phase_labels)

        for idx, phase_label in enumerate(phase_labels):
            label = tk.Label(self.canvas, text=str(phase_label))
            label.config(bg=self.COLORS[idx], font=("helvetica", 14, "bold"))
            label.bind("<B1-Motion>", lambda event: self.__phase_box_move_callback(event))
            label.place(
                x=0.05 * w + (w / (2 * m)) * idx,
                y=0.85 * h - ((0.95 * h) / m) * idx,
                relwidth=0.76 / m,
                relheight=min(0.1, 0.9 / m),
            )
            self.label_dict[phase_label] = label

    def get_phase_boxes(self) -> Dict[str, tk.Label]:
        """Get the dictionary of tk label objects for each phase label
        @todo - replace this with a method which returns a Tuple[width, height, x, y], but will also need to add a method to place them at new locations."""
        return self.label_dict

    def update_canvas(self) -> None:
        """Update the canvas to ensure coordinates are correct?"""
        self.canvas.update()

    def update_tree_2col(self, phase_rels: Optional[List[Tuple[str, str]]]) -> None:
        """Update the table of group relationships to the value(s) provided by the user

        This is the 2 column version, for the first step in the residual checking process.

        @todo - older, younger might fit better with the x axis?"""
        # Prep a local dataframe for presentation
        df = pd.DataFrame(phase_rels, columns=["Younger group", "Older group"])
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

    def update_tree_3col(self, menudict: Dict[Tuple[str, str], str]) -> None:
        """Update the table of group relationships to the value(s) provided by the user

        This is the 3 column version, for the confirmation step in the residual checking process.

        Formerly part of popupwindow3.get_coords"""

        # Prepare the new 3 column dataframe
        col1, col2, col3 = [], [], []
        rels_df = pd.DataFrame()
        for i in menudict.keys():
            col1.append(i[0])
            col2.append(i[1])
            col3.append(menudict[i])
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

    def bind_phase_box_on_move(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for moving the phase boxes.

        This is set on a (private) view class member, to avoid havnig to call this method again if the phase boxes are ever re-generated.
        """
        if callback is not None:
            self.__phase_box_move_callback = callback

    def bind_confirm_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the confirm_button is pressed"""
        if callback is not None:
            self.__confirm_callback = callback

    def bind_render_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the render_button is pressed"""
        if callback is not None:
            self.__render_callback = callback

    def bind_change_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the change_button is pressed"""
        if callback is not None:
            self.__change_callback = callback

    def on_confirm(self) -> None:
        """Update the view to show the UI for when after the confirm button has been pressed.

        This destroys then re-creates elements.

        Formerly part of popupWindow3.get_coords

        @todo - deicde if I am ok with this abstraction.
        @todo rename"""
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

        Formerly popupWindow3.back_func

        @todo - deicde if I am ok with this abstraction.
        @todo rename"""
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
