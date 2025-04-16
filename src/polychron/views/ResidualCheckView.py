import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from .BasePopupView import BasePopupView


class ResidualCheckView(BasePopupView):
    """View for residual vs inclusive contexts

    Formerly `popupWindow3`, Part of the Rendering chronological graph process

    @todo - make this a popup rather than child of parent?
    """

    def __init__(self, parent: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)
        self.parent = parent

        self.geometry("1500x400")
        self.title("Adding group relationships")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

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

        # @todo move this to a method
        # for ind, i in enumerate(self.phase_labels):
        #     msg = tk.Label(self.canvas, text = str(i))
        #     msg.config(bg=self.COLORS[ind], font=('helvetica', 14, 'bold'))
        #     msg.bind('<B1-Motion>',self.on_move)
        #     msg.place(x= 0.05*w + (w/(2*m))*ind, y= 0.85*h - ((0.95*h)/m)*ind, relwidth = 0.76/m, relheight = min(0.1, 0.9/m))
        #     self.label_dict[i] = msg

        self.confirm_button = tk.Button(
            self.maincanvas, text="Confirm groups", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )  # command = lambda: self.get_coords(),
        self.confirm_button.place(relx=0.8, rely=0.91)

        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg="white")
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.tree.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)
        # cols = list(self.df.columns) # @todo
        # self.tree["columns"] = cols # @todo
        #  for i in cols:
        #     self.tree.column(i, anchor="w")
        #     self.tree.heading(i, text=i, anchor='w')
        # for index, row in self.df.iterrows():
        #     self.tree.insert("",0,text=index,values=list(row))
        self.tree["show"] = "headings"
        # master.wait_window(self)

    def bind_confirm_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the confirm_button is pressed"""
        if callback is not None:
            self.confirm_button.config(command=callback)
