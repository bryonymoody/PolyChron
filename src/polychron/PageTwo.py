import copy
import tkinter as tk
from tkinter import ttk

import networkx as nx
from PIL import Image, ImageTk

from . import globals
from .popupWindow4 import popupWindow4
from .util import imgrender, imgrender_phase, node_coords_fromjson


class PageTwo(object):
    def __init__(self, master, controller):
        """initilaising page two"""
        self.top = tk.Toplevel(controller)
        self.top.geometry("2000x1000")
        self.intru_list = []
        self.resid_list = []
        self.controller = controller
        self.h_1 = 0
        self.w_1 = 0
        self.transx2 = 0
        self.transy2 = 0
        self.modevariable = None
        self.meta1 = ""
        #        self.metatext = ""
        self.mode = ""
        ##### intial values for all the functions
        self.delnodes = []
        self.edge_nodes = []
        self.comb_nodes = []
        self.edges_del = []
        self.temp = []
        self.results_list = []
        self.x_1 = 1
        self.image = "noimage"
        self.phase_rels = None
        # self.imscale2 = 1.0  # scale for the canvaas image
        self.delta2 = 1.1
        self.results_text = None
        self.canvas_plt = None
        self.phase_len_nodes = []
        self.canvas = tk.Canvas(self.top, bd=0, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        startpage = self.controller.get_page("StartPage")
        self.graphcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.graphcanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.9)
        label = tk.Message(
            self.top,
            text="Using this page: \n\n Please click on the buttons below to set into residual or intrusive mode. Then double right click on any context to set as residual/intrusive. \n\n Note that orange boxes denote intrusive contexts and blue boxes denote residual contexts. \n\n If you have clicked on a context by mistake, double right click to remove any label attributed to the context.",
        )
        label.place(relx=0.4, rely=0.05)
        label2 = ttk.Label(self.canvas, text="Residual Contexts")
        label2.place(relx=0.4, rely=0.4)
        self.graphcanvas.update()
        self.residcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.residcanvas.place(relx=0.4, rely=0.42, relwidth=0.35, relheight=0.08)
        self.intrucanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.intrucanvas.place(relx=0.4, rely=0.54, relwidth=0.35, relheight=0.08)

        self.resid_label = ttk.Label(self.residcanvas, text=self.resid_list)
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        self.intru_label = ttk.Label(self.intrucanvas, text=self.intru_list)
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        label3 = ttk.Label(self.canvas, text="Intrusive Contexts")
        label3.place(relx=0.4, rely=0.52)
        if startpage.graph is not None:
            self.graphcopy = self.load_graph()
            self.imscale2 = min(921 / self.image.size[0], 702 / self.image.size[1])
            self.graphcanvas.scale("all", 0, 0, self.delta2, self.delta2)  # rescale all canvas objects
            self.show_image2()
        self.graphcanvas.update()
        button = ttk.Button(self.top, text="Proceed", command=lambda: self.popup4_wrapper(controller))

        button1 = tk.Button(self.top, text="Residual mode", command=lambda: self.mode_set("resid"))
        button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
        button3 = tk.Button(self.top, text="Intrusive mode", command=lambda: self.mode_set("intru"))
        button.place(relx=0.48, rely=0.65, relwidth=0.09, relheight=0.03)
        button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)
        self.graphcanvas.bind("<MouseWheel>", self.wheel2)
        self.graphcanvas.bind("<Button-4>", self.wheel2)  # only with Linux, wheel scroll down
        self.graphcanvas.bind("<Button-5>", self.wheel2)
        self.graphcanvas.bind("<Double-Button-3>", self.resid_node_click)
        self.graphcanvas.bind("<Button-1>", self.move_from2)
        self.graphcanvas.bind("<B1-Motion>", self.move_to2)
        master.wait_window(self.top)
        # placing image on littlecanvas from graph

    def popup4_wrapper(self, controller):
        """wraps popup4 so we can get the variables from self.popup4"""
        self.popup4 = popupWindow4(
            self, controller, self.resid_list, self.intru_list, self.node_del_tracker, self.graphcopy
        )
        self.top.destroy()

    def mode_set(self, var_set):
        """sets the mode to residual or intrusive and highlights the colour of the  button"""
        self.modevariable = var_set
        if var_set == "resid":
            button1 = tk.Button(
                self.top, text="Residual mode", command=lambda: self.mode_set("resid"), background="orange"
            )
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(self.top, text="Intrusive mode", command=lambda: self.mode_set("intru"))
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)
        if var_set == "intru":
            button1 = tk.Button(self.top, text="Residual mode", command=lambda: self.mode_set("resid"))
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(
                self.top, text="Intrusive mode", command=lambda: self.mode_set("intru"), background="lightgreen"
            )
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)

    def tkraise(self, aboveThis=None):
        """runs loads graph"""
        self.load_graph()
        super().tkraise(aboveThis)

    def load_graph(self):
        """loads graph on results page"""
        # loads start page so we get get variables from that class
        startpage = self.controller.get_page("StartPage")
        self.graphcopy = copy.deepcopy(startpage.graph)
        datadict = nx.get_node_attributes(self.graphcopy, "Determination")
        nodes = self.graphcopy.nodes()
        self.node_del_tracker = []
        for i in nodes:
            if datadict[i] == [None, None]:
                self.node_del_tracker.append(i)
        color = nx.get_node_attributes(self.graphcopy, "color")
        fill = nx.get_node_attributes(self.graphcopy, "fontcolor")
        for j in self.node_del_tracker:
            color[j] = "gray"
            fill[j] = "gray"
        nx.set_node_attributes(self.graphcopy, color, "color")
        nx.set_node_attributes(self.graphcopy, fill, "fontcolor")
        if globals.phase_true == 1:
            self.image = imgrender_phase(self.graphcopy)
        else:
            self.image = imgrender(self.graphcopy, self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
        #    scale_factor = min(self.graphcanvas.winfo_width()/self.image_ws.size[0], self.graphcanvas.winfo_height()/self.image_ws.size[1])
        #     self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
        self.icon = ImageTk.PhotoImage(self.image)
        self.graphcanvas_img = self.graphcanvas.create_image(0, 0, anchor="nw", image=self.icon)
        self.width2, self.height2 = self.image.size
        self.imscale2 = 1.0  # scale for the canvaas image
        self.delta2 = 1.1  # zoom magnitude
        startpage.update_idletasks()
        self.container = self.graphcanvas.create_rectangle(0, 0, self.width2, self.height2, width=0)
        return self.graphcopy

    def move_from2(self, event):
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image != "noimage":
            self.graphcanvas.scan_mark(event.x, event.y)

    def move_to2(self, event):
        """Drag (move) canvas to the new position"""
        if self.image != "noimage":
            self.graphcanvas.scan_dragto(event.x, event.y, gain=1)
            self.show_image2()

    def wheel2(self, event):
        """Zoom with mouse wheel"""
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
        #    print(scale2)
        self.graphcanvas.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def autozoom(self, event):
        """Zoom with mouse wheel"""
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
        """Show image on the Canvas"""
        startpage = self.controller.get_page("StartPage")
        startpage.update_idletasks()
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

    def nodecheck(self, x_current, y_current):
        """returns the node that corresponds to the mouse cooridinates"""
        startpage = self.controller.get_page("StartPage")
        # updates canvas to get the right coordinates
        startpage.update_idletasks()

        node_inside = "no node"
        if self.graphcopy is not None:
            # gets node coordinates from the graph
            node_df_con = node_coords_fromjson(self.graphcopy)
            # forms a dataframe from the dicitonary of coords
            globals.node_df = node_df_con[0]
            xmax, ymax = node_df_con[1]
            # scales the coordinates using the canvas and image size
            x, y = self.image.size
            cavx = x * self.imscale2
            cany = y * self.imscale2
            xscale = (x_current) * (xmax) / cavx
            yscale = (cany - y_current) * (ymax) / cany
            # gets current node colours
            outline = nx.get_node_attributes(self.graphcopy, "color")
            for n_ind in range(globals.node_df.shape[0]):
                if (globals.node_df.iloc[n_ind].x_lower < xscale < globals.node_df.iloc[n_ind].x_upper) and (
                    globals.node_df.iloc[n_ind].y_lower < yscale < globals.node_df.iloc[n_ind].y_upper
                ):
                    node_inside = globals.node_df.iloc[n_ind].name
                    nx.set_node_attributes(self.graphcopy, outline, "color")
        return node_inside

    def resid_node_click(self, event):
        """Gets node that you're clicking on and sets it as the right colour depending on if it's residual or intrusive"""
        startpage = self.controller.get_page("StartPage")
        startpage.update_idletasks()
        self.cursorx2 = int(self.graphcanvas.winfo_pointerx() - self.graphcanvas.winfo_rootx())
        self.cursory2 = int(self.graphcanvas.winfo_pointery() - self.graphcanvas.winfo_rooty())
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        outline = nx.get_node_attributes(self.graphcopy, "color")
        # changes colour of the node outline to represent: intrustive (green), residual (orange) or none (black)
        if (node in self.resid_list) and (self.modevariable != "intru"):
            self.resid_list.remove(node)
            outline[node] = "black"
        elif (node in self.resid_list) and (self.modevariable == "intru"):
            self.resid_list.remove(node)
            outline[node] = "green"
            self.intru_list.append(node)
        elif (node in self.intru_list) and (self.modevariable != "resid"):
            self.intru_list.remove(node)
            outline[node] = "black"
        elif (node in self.intru_list) and (self.modevariable == "resid"):
            self.intru_list.remove(node)
            self.resid_list.append(node)
            outline[node] = "orange"
        elif (self.modevariable == "resid") and (node not in self.resid_list):
            self.resid_list.append(node)
            outline[node] = "orange"
        elif self.modevariable == "intru" and (node not in self.intru_list):
            self.intru_list.append(node)
            outline[node] = "green"
        self.resid_label = ttk.Label(self.residcanvas, text=str(self.resid_list).replace("'", "")[1:-1])
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.intru_label = ttk.Label(self.intrucanvas, text=str(self.intru_list).replace("'", "")[1:-1])
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        # adds scrollbars to the canvas
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        # updates the node outline colour
        nx.set_node_attributes(self.graphcopy, outline, "color")
        if globals.phase_true == 1:
            imgrender_phase(self.graphcopy)
        else:
            imgrender(self.graphcopy, self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
        # rerends the image of the strat DAG with right colours
        self.image = Image.open("fi_new.png")
        self.width2, self.height2 = self.image.size
        self.container = self.graphcanvas.create_rectangle(0, 0, self.width2, self.height2, width=0)
        self.show_image2()
        return node
