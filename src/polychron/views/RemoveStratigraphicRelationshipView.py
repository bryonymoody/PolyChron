import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class RemoveStratigraphicRelationshipView(ttk.Frame):
    """View for providing the reason wehn removing a specific stratigraphic relationship

    Formerly `popupWindow6`

    @todo - Add the specific relationship details to the text label?
    @todo - Add the option to not remove the relationship, i.e. cancel / go back?
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        # @todo cleaner popup separation?
        self.top=tk.Toplevel(root)
        self.top.configure(bg ='white')
        self.top.geometry("1000x400")
        self.top.title("Removal of stratigraphic relationship")
        self.top.attributes('-topmost', 'true')  # @todo maybe remove. # Forces the top level to always be on top. 

        self.label=tk.Label(self.top,text="Why are you deleting the stratigraphic relationship between these contexts?", bg ='white', font='helvetica 12', fg = '#2f4858')
        self.label.place(relx = 0.3, rely = 0.1)
        self.text=tk.Text(self.top, font='helvetica 12', fg = '#2f4858')
        self.text.place(relx = 0.3, rely = 0.2, relheight= 0.5, relwidth = 0.5)
        self.ok_button=tk.Button(self.top,text='OK', bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
        self.ok_button.place(relx = 0.3, rely = 0.7)
    
    # def cleanup(self):
    #     self.value=self.text.get('1.0', 'end')
    #     self.top.destroy()

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)
