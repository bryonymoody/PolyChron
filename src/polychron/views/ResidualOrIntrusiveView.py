import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Optional

from PIL import ImageTk

from .BasePopupView import BasePopupView


class ResidualOrIntrusiveView(BasePopupView):
    """View for users to provide input on whether contexts are residual or intrusive during chronological graph rendering

    Formerly part of `PageTwo`

    """

    def __init__(self, parent: tk.Frame, start_visible=False):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, start_visible)

        # @todo view level proeprties that might need documenting or removing or refactoring?
        self.imscale2 = 1.0
        self.delta2 = 1.1
        self.icon = None
        self.transx2 = 0
        self.transy2 = 0
        self.width2 = 0
        self.height2 = 0
        self.image = None  # in-memory rendered image. @todo should this actually belong to the model?

        # @todo cleaner popup separation?
        self.title("Identify Residual or Intrusive Contexts")
        self.configure(bg="#AEC7D6")
        self.geometry("2000x1000")  # @todo - differnt geometry?
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.graphcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.graphcanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.9)
        self.graphcanvas.update()  # @todo - is this neccessary?
        self.container = self.graphcanvas.create_rectangle(
            0, 0, self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height(), width=0
        )  # @todo this should be the image width and height?

        # @todo - this label suggests blue boxes, but green is used. https://github.com/bryonymoody/PolyChron/issues/68
        self.label = tk.Message(
            self,
            text="Using this page: \n\n Please click on the buttons below to set into residual or intrusive mode. Then double right click on any context to set as residual/intrusive. \n\n Note that orange boxes denote intrusive contexts and blue boxes denote residual contexts. \n\n If you have clicked on a context by mistake, double right click to remove any label attributed to the context.",
        )
        self.label.place(relx=0.4, rely=0.05)
        self.resid_title_label = ttk.Label(self.canvas, text="Residual Contexts")
        self.resid_title_label.place(relx=0.4, rely=0.4)
        self.residcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.residcanvas.place(relx=0.4, rely=0.42, relwidth=0.35, relheight=0.08)
        self.resid_label = ttk.Label(self.residcanvas)
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.resid_scroll_bar = ttk.Scrollbar(self.residcanvas)
        self.resid_scroll_bar.pack(side=tk.RIGHT)
        self.intrucanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.intrucanvas.place(relx=0.4, rely=0.54, relwidth=0.35, relheight=0.08)
        self.intru_label = ttk.Label(self.intrucanvas)
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.intru_scroll_bar = ttk.Scrollbar(self.intrucanvas)
        self.intru_scroll_bar.pack(side=tk.RIGHT)
        self.intru_title_label = ttk.Label(self.canvas, text="Intrusive Contexts")
        self.intru_title_label.place(relx=0.4, rely=0.52)

        self.proceed_button = ttk.Button(self, text="Proceed")
        self.proceed_button.place(relx=0.48, rely=0.65, relwidth=0.09, relheight=0.03)

        self.residual_mode_button = tk.Button(self, text="Residual mode")
        self.residual_mode_button.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
        self.intrusive_mode_button = tk.Button(self, text="Intrusive mode")
        self.intrusive_mode_button.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)

        self.show_image2()

    def set_resid_label_text(self, resid_list: List[str]):
        """Update the intrusive list

        @todo - check this behaves as intended, it might make a copy?
        """
        self.resid_label["text"] = str(resid_list).replace("'", "")[1:-1]

    def set_intru_label_text(self, intru_list: List[str]):
        """Update the intrusive list

        @todo - check this behaves as intended, it might make a copy?
        """
        self.intru_label["text"] = str(intru_list).replace("'", "")[1:-1]

    def bind_proceed_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the proceed_button is pressed"""
        if callback is not None:
            self.proceed_button.config(command=callback)

    def bind_residual_mode_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the residual_mode_button is pressed"""
        if callback is not None:
            self.residual_mode_button.config(command=callback)

    def bind_intrusive_mode_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the intrusive_mode_button is pressed"""
        if callback is not None:
            self.intrusive_mode_button.config(command=callback)

    def set_residual_mode_button_background(self, color: str):
        self.residual_mode_button.config(background=str(color))

    def set_intrusive_mode_button_background(self, color: str):
        self.intrusive_mode_button.config(background=str(color))

    def bind_graphcanvas_events(
        self,
        callback_wheel: Callable[[], Optional[Any]],
        callback_node_click: Callable[[], Optional[Any]],
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
        self.graphcanvas.bind("<Double-Button-3>", callback_node_click)
        self.graphcanvas.bind("<Button-1>", callback_move_from)
        self.graphcanvas.bind("<B1-Motion>", callback_move_to)

    def wheel2(self, event):
        """Zoom with mouse wheel

        Formerly (part of) PageTwo.wheel

        @todo this abstraction could probably be improved
        @todo - rename this, doesn't need 2"""
        x_zoom = self.graphcanvas.canvasx(event.x)
        y_zoom = self.graphcanvas.canvasy(event.y)
        bbox = self.graphcanvas.bbox(self.container)  # get image area
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
            i = min(self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
            if i < self.imscale2:
                return  # 1 pixel is bigger than the visible area
            self.imscale2 *= self.delta2
            scale2 *= self.delta2
        self.graphcanvas.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def autozoom(self, event):
        """Zoom with mouse wheel

        Formerly StartPage.autozoom

        @toldo - this is unsused. Delete?

        @todo rename?"""
        x_zoom = self.graphcanvas.canvasx(event.x)
        y_zoom = self.graphcanvas.canvasy(event.y)
        bbox = self.graphcanvas.bbox(self.container)  # get image area
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
            i = min(self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
            if i < self.imscale2:
                return  # 1 pixel is bigger than the visible area
            self.imscale2 *= self.delta2
            scale2 *= self.delta2
        self.graphcanvas.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def show_image2(self):
        """Show image on the Canvas

        @todo the logic for this should probably be elsewhere / add parameters?
        @todo - rename this, doesn't need 2
        @todo - can probably refactor this as common canvas zooming behaviour with other views"""

        if self.image is None:
            return

        # startpage = self.controller.get_page('StartPage') # @todo not needed?
        # startpage.update_idletasks()
        bbox1 = [0, 0, int(self.image.size[0] * self.imscale2), int(self.image.size[1] * self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.graphcanvas.canvasx(0),  # get visible area of the canvas
            self.graphcanvas.canvasy(0),
            self.graphcanvas.canvasx(self.graphcanvas.winfo_width()),
            self.graphcanvas.canvasy(self.graphcanvas.winfo_height()),
        )
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        bbox1 = [0, 0, int(self.image.size[0] * self.imscale2), int(self.image.size[1] * self.imscale2)]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.graphcanvas.configure(scrollregion=bbox)  # set scroll region
        x_1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y_1 = max(bbox2[1] - bbox1[1], 0)
        x_2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y_2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        if int(x_2 - x_1) > 0 and int(y_2 - y_1) > 0:  # show image if it in the visible area
            x_img = min(int(x_2 / self.imscale2), self.width2)  # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2), x_img, y_img))
            self.graphcanvas.delete(self.icon)
            self.icon = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.imageid2 = self.graphcanvas.create_image(
                max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]), anchor="nw", image=self.icon
            )
            self.transx2, self.transy2 = bbox2[0], bbox2[1]

        self.graphcanvas.update()

    def tkraise(self, aboveThis=None) -> None:
        """Loads the graph and ensures this window is raised above another.

        Formerly PageTwo.tkraise"""
        self.load_graph()
        super().tkraise(aboveThis)
