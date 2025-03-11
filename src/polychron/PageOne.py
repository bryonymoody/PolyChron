import tkinter as tk
from tkinter import simpledialog, ttk

import matplotlib as plt
import networkx as nx
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import ImageTk

from . import automated_mcmc_ordering_coupling_copy as mcmc
from . import globals
from .util import imgrender2, node_coords_fromjson, phase_length_finder


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        """initilises page one"""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        startpage = self.controller.get_page("StartPage")
        self.configure(background="#fcfdfd")
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg="#FFE9D6")
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)
        self.button1 = tk.Button(
            self,
            text="Stratigraphy and supplementary data",
            font="helvetica 12 bold",
            fg="#2F4858",
            command=lambda: controller.show_frame("StartPage"),
            bd=0,
            highlightthickness=0,
            bg="#AEC7D6",
        )
        self.button1.place(relx=0.38, rely=0.0, relwidth=0.17, relheight=0.03)
        self.button1_a = tk.Button(
            self,
            text="Dating Results",
            font="helvetica 12 bold",
            fg="#8F4300",
            command=lambda: controller.show_frame("PageOne"),
            bd=0,
            highlightthickness=0,
            bg="#FFE9D6",
        )
        self.button1_a.place(relx=0.55, rely=0.0, relwidth=0.15, relheight=0.03)
        # define all variables that are used
        self.h_1 = 0
        self.w_1 = 0
        self.transx2 = 0
        self.transy2 = 0
        self.meta1 = ""
        #        self.metatext = ""
        self.mode = ""
        ##### intial values for all the functions
        self.delnodes = []
        self.delnodes_meta = []
        self.edge_nodes = []
        self.comb_nodes = []
        self.edges_del = []
        self.temp = []
        self.results_list = []
        self.cont_canvas_list = ""
        self.x_1 = 1
        self.image = "noimage"
        self.phase_rels = None
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1
        self.results_text = None
        self.canvas_plt = None
        self.phase_len_nodes = []
        self.fig = None
        self.file_menubar = ttk.Menubutton(
            self,
            text="File",
        )
        # Adding File Menu and commands
        file = tk.Menu(self.file_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.file_menubar["menu"] = file
        file.add_separator()
        file.add_command(
            label="Save project progress", command=lambda: startpage.save_state_1(), font=("helvetica 11 bold")
        )
        self.file_menubar.place(relx=0.0, rely=0, relwidth=0.1, relheight=0.03)
        self.view_menubar = ttk.Menubutton(self, text="View")
        # Adding File Menu and commands
        file1 = tk.Menu(self.view_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.view_menubar["menu"] = file1
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)
        self.tool_menubar = ttk.Menubutton(
            self,
            text="Tools",
        )
        # Adding File Menu and commands
        file2 = tk.Menu(self.tool_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.tool_menubar["menu"] = file2
        self.tool_menubar.place(relx=0.15, rely=0, relwidth=0.1, relheight=0.03)
        # forming and placing canvas and little canvas
        self.behindcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas.place(relx=0.6, rely=0.038, relwidth=0.39, relheight=0.96)
        #######################
        self.littlecanvas2_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2_label.place(relx=0.003, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas2_label_id = self.littlecanvas2_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas2_label.itemconfig(
            self.littlecanvas2_label_id, text="Chronological graph", font="helvetica 12 bold"
        )
        #######################
        self.littlecanvas = tk.Canvas(
            self.behindcanvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        ##########################################
        self.behindcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas2.place(relx=0.003, rely=0.038, relwidth=0.37, relheight=0.96)
        ##########################################
        self.littlecanvas_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_label.place(relx=0.6, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas_label_id = self.littlecanvas_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas_label.itemconfig(
            self.littlecanvas_label_id, text="Posterior densities", font="helvetica 12 bold"
        )
        #########################################
        self.littlecanvas_a_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_a_label.place(relx=0.375, rely=0.518, relwidth=0.08, relheight=0.027)
        self.littlecanvas_a_label_id = self.littlecanvas_a_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas_a_label.itemconfig(
            self.littlecanvas_a_label_id, text="Context list", font="helvetica 12 bold"
        )
        ############################################
        self.behindcanvas_a = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas_a.place(relx=0.375, rely=0.038, relwidth=0.223, relheight=0.45)
        ######################################
        self.littlecanvas_a = tk.Canvas(
            self.behindcanvas_a, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_a.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        #####################################################
        self.behindcanvas_3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas_3.place(relx=0.375, rely=0.545, relwidth=0.223, relheight=0.45)
        ########################################3
        self.littlecanvas2 = tk.Canvas(
            self.behindcanvas2, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        #######################################################
        ################################
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

        ###############################################
        self.littlecanvas3_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas3_label.place(relx=0.375, rely=0.011, relwidth=0.14, relheight=0.027)
        self.littlecanvas3_label_id = self.littlecanvas3_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas3_label.itemconfig(
            self.littlecanvas3_label_id, text="Calendar date range estimates", font="helvetica 12 bold"
        )

        #################################
        self.littlecanvas2.bind("<MouseWheel>", self.wheel2)
        self.littlecanvas2.bind("<Button-4>", self.wheel2)  # only with Linux, wheel scroll down
        self.littlecanvas2.bind("<Button-5>", self.wheel2)
        self.littlecanvas2.bind("<Button-3>", self.onRight)
        self.littlecanvas2.bind("<Button-1>", self.move_from2)
        self.littlecanvas2.bind("<B1-Motion>", self.move_to2)
        # placing image on littlecanvas from graph
        self.littlecanvas2.rowconfigure(0, weight=1)
        self.littlecanvas2.columnconfigure(0, weight=1)
        self.littlecanvas2.update()
        # placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)

        #########deleted nodes##################
        self.button2 = ttk.Button(self.behindcanvas_3, text="Posterior densities", command=self.mcmc_output)
        self.button2.place(relx=0.008, rely=0.92, relwidth=0.402, relheight=0.07)
        self.button2a = ttk.Button(self.behindcanvas_3, text="HPD intervals", command=self.get_hpd_interval)
        self.button2a.place(relx=0.415, rely=0.92, relwidth=0.322, relheight=0.07)
        self.button3 = ttk.Button(self.behindcanvas_3, text="Clear list", command=self.clear_results_list)
        self.button3.place(relx=0.74, rely=0.92, relwidth=0.252, relheight=0.07)
        self.ResultList = [
            "Add to results list",
            "Get time elapsed",
        ]
        self.variable = tk.StringVar(self.littlecanvas)
        self.variable.set("Add to results list")
        self.testmenu2 = ttk.OptionMenu(
            self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
        )

    def clear_results_list(self):
        """deletes nodes from results lists"""
        self.results_list = []
        self.littlecanvas3.delete(self.results_text)
        self.canvas_plt.get_tk_widget().pack_forget()
        for item in self.tree_phases.get_children():
            self.tree_phases.delete(item)

    def node_finder(self, currentevent):
        """finds nodes in the chronodag on results page"""
        self.testmenu2.place_forget()
        startpage = self.controller.get_page("StartPage")
        self.chronograph = startpage.chrono_dag
        x = str(self.chrono_nodes(currentevent))

        if self.variable.get() == "Add to results list":
            self.littlecanvas3.delete(self.results_text)
            # ref = np.where(np.array(startpage.CONTEXT_NO) == x)[0][0]
            if x != "no node":
                self.results_list.append(x)

        if len(self.phase_len_nodes) == 1:
            if (
                self.variable.get()
                == "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context"
            ):
                self.phase_len_nodes = np.append(self.phase_len_nodes, x)
                if self.canvas_plt is not None:
                    self.canvas_plt.get_tk_widget().pack_forget()
                #        font = {'size': 11}
                # using rc function

                self.fig = Figure()
                #     self.fig.rc('font', **font)
                LENGTHS = phase_length_finder(
                    self.phase_len_nodes[0], self.phase_len_nodes[1], startpage.all_results_dict
                )
                plot1 = self.fig.add_subplot(111)
                plot1.hist(LENGTHS, bins="auto", color="#0504aa", rwidth=1, density=True)
                #  plot1.xlabel('Time elapsed in calibrated years (cal BP)')
                #  plot1.ylabel('Probability density')
                plot1.spines["right"].set_visible(False)
                plot1.spines["top"].set_visible(False)
                # plot1.set_ylim([0, 0.05])
                # plot1.set_xlim([0, 400])
                plot1.title.set_text(
                    "Time elapsed between " + str(self.phase_len_nodes[0]) + " and " + str(self.phase_len_nodes[1])
                )
                interval = list(mcmc.HPD_interval(np.array(LENGTHS[1000:])))
                columns = ("context_1", "context_2", "hpd_interval")
                #       self.fig.set_tight_layout(True)
                self.canvas_plt = FigureCanvasTkAgg(self.fig, master=self.littlecanvas)
                self.canvas_plt.get_tk_widget().place(relx=0, rely=0, relwidth=1)
                self.canvas_plt.draw_idle()
                # show hpd intervlls -----------
                self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show="headings")
                # define headings
                self.tree_phases.heading("context_1", text="Context 1")
                self.tree_phases.heading("context_2", text="Context 2")
                self.tree_phases.heading("hpd_interval", text="HPD interval")
                intervals = []
                hpd_str = ""
                refs = [k for k in range(len(interval)) if k % 2]
                for i in refs:
                    hpd_str = hpd_str + str(np.abs(interval[i - 1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                # add data to the treeview
                intervals.append((self.phase_len_nodes[0], self.phase_len_nodes[1], hpd_str))
                for contact in intervals:
                    self.tree_phases.insert("", tk.END, values=contact)
                self.tree_phases.place(relx=0, rely=0, relwidth=1)
                # add a scrollbar
                scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
                self.tree_phases.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky="nsew")
            self.ResultList.remove("Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context")
            self.testmenu2 = ttk.OptionMenu(
                self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
            )
            self.phase_len_nodes = []

        if self.variable.get() == "Get time elapsed":
            if len(self.phase_len_nodes) == 1:
                self.ResultList.remove(
                    "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context"
                )
                self.testmenu2 = ttk.OptionMenu(
                    self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
                )
                self.phase_len_nodes = []
            self.phase_len_nodes = np.append(self.phase_len_nodes, x)
            self.ResultList.append("Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context")
            self.testmenu2 = ttk.OptionMenu(
                self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
            )
        self.littlecanvas3.delete(self.results_text)
        self.littlecanvas3.delete(self.littlecanvas3_id)
        self.cont_canvas_list = ""
        for i in set(self.results_list):
            self.cont_canvas_list = self.cont_canvas_list + str(i) + "\n"
        self.results_text = self.littlecanvas3.create_text(
            5, 10, anchor="nw", text=self.cont_canvas_list, fill="#0A3200", font=("Helvetica 12 bold")
        )
        self.variable.set("Add to results list")

    def onRight(self, *args):
        """makes test menu appear after right click"""
        self.littlecanvas2.unbind("Button-1>")
        self.littlecanvas2.bind("<Button-1>", self.onLeft)
        # Here we fetch our X and Y coordinates of the cursor RELATIVE to the window
        self.cursorx2 = int(self.littlecanvas2.winfo_pointerx() - self.littlecanvas2.winfo_rootx())
        self.cursory2 = int(self.littlecanvas2.winfo_pointery() - self.littlecanvas2.winfo_rooty())

        # Now we define our right click menu canvas
        # And here is where we use our X and Y variables, to place the menu where our cursor is,
        # That's how right click menus should be placed.
        self.testmenu2.place(x=self.cursorx2, y=self.cursory2, relwidth=0.2)
        # This is for packing our options onto the canvas, to prevent the canvas from resizing.
        # This is extremely useful if you split your program into multiple canvases or frames
        # and the pack method is forcing them to resize.
        self.testmenu2.pack_propagate(0)
        # Here is our label on the right click menu for deleting a row, notice the cursor
        # value, which will give us a pointy finger when you hover over the option.
        self.testmenu2.config(width=10)
        # This function is for removing the canvas when an option is clicked.

    def preClick(self, *args):
        """makes test menu appear and removes any previous test menu"""
        try:
            self.testmenu2.place_forget()
            self.onRight()
        except Exception:
            self.onRight()

    # Hide menu when left clicking
    def onLeft(self, *args):
        """hides menu when left clicking"""
        try:
            self.testmenu2.place_forget()
        except Exception:
            pass

    def mcmc_output(self):
        """loads posterior density plots into the graph"""
        startpage = self.controller.get_page("StartPage")
        if globals.mcmc_check == "mcmc_loaded":
            if self.canvas_plt is not None:
                self.canvas_plt.get_tk_widget().pack_forget()
                self.toolbar.destroy()
            fig = Figure(figsize=(8, min(30, len(self.results_list) * 3)), dpi=100)
            for i, j in enumerate(self.results_list):
                if len(self.results_list) < 10:
                    n = len(self.results_list)
                else:
                    n = 10
                plt.rcParams["text.usetex"]

                plot_index = int(str(n) + str(1) + str(i + 1))
                plot1 = fig.add_subplot(plot_index)
                plot1.hist(startpage.resultsdict[j], bins="auto", color="#0504aa", alpha=0.7, rwidth=1, density=True)
                plot1.spines["right"].set_visible(False)
                plot1.spines["top"].set_visible(False)
                fig.gca().invert_xaxis()
                plot1.set_ylim([0, 0.02])
                nodes = list(nx.topological_sort(startpage.chrono_dag))
                uplim = nodes[0]
                lowlim = nodes[-1]
                min_plot = min(startpage.resultsdict[uplim])
                max_plot = max(startpage.resultsdict[lowlim])
                plot1.set_xlim(min_plot, max_plot)
                node = str(j)
                if ("a" in node) or ("b" in node):
                    if "a" in node:
                        node = node.replace("a_", r"\alpha_{")
                    if "b" in node:
                        node = node.replace("b_", r"\beta_{")
                    if "=" in node:
                        node = node.replace("=", "} = ")
                    plot1.title.set_text(r"Group boundary " + r"$" + node + "}$")
                else:
                    plot1.title.set_text(r"Context " + r"$" + node + "}$")

            fig.set_tight_layout(True)
            self.canvas_plt = FigureCanvasTkAgg(fig, master=self.littlecanvas)
            self.canvas_plt.draw()
            # creating the Matplotlib toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas_plt, self.littlecanvas)  #
            self.toolbar.update()  #
            self.canvas_plt.get_tk_widget().pack()

    def get_hpd_interval(self):
        """loads hpd intervals into the results page"""
        if len(self.results_list) != 0:
            startpage = self.controller.get_page("StartPage")
            USER_INP = simpledialog.askstring(
                title="HPD interval percentage",
                prompt="Please input HPD interval percentage. Note, 95% is used as standard \n \n Percentage:",
            )

            self.lim = np.float64(USER_INP) / 100
            if globals.mcmc_check == "mcmc_loaded":
                hpd_str = ""
                columns = ("context", "hpd_interval")
                self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show="headings")
                self.tree_phases.heading("context", text="Context")
                self.tree_phases.heading("hpd_interval", text=str(USER_INP) + "% HPD interval")
                intervals = []
                for i, j in enumerate(list(set(self.results_list))):
                    node = str(j)
                    interval = list(mcmc.HPD_interval(np.array(startpage.resultsdict[j][1000:]), lim=self.lim))
                    # define headings
                    hpd_str = ""
                    refs = [k for k in range(len(interval)) if k % 2]
                    for i in refs:
                        hpd_str = hpd_str + str(np.abs(interval[i - 1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                    # add data to the treeview
                    intervals.append((node, hpd_str))
                for contact in intervals:
                    self.tree_phases.insert("", tk.END, values=contact)
                self.tree_phases.place(relx=0, rely=0, relwidth=0.99)
                # add a scrollbar
                scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
                self.tree_phases.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky="nsew")
                self.littlecanvas_a.create_text(150, 80, text=hpd_str, fill="#0A3200")

    def chronograph_render_post(self):
        if globals.load_check == "loaded":
            self.image2 = imgrender2(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
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

    def tkraise(self, aboveThis=None):
        self.chronograph_render_post()
        super().tkraise(aboveThis)

    def move_from2(self, event):
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image2 != "noimage":
            self.littlecanvas2.scan_mark(event.x, event.y)

    def move_to2(self, event):
        """Drag (move) canvas to the new position"""
        if self.image2 != "noimage":
            self.littlecanvas2.scan_dragto(event.x, event.y, gain=1)
            self.show_image2()

    def wheel2(self, event):
        """Zoom with mouse wheel"""
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

    def show_image2(self):
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

    def nodecheck(self, x_current, y_current):
        """returns the node that corresponds to the mouse cooridinates"""
        node_inside = "no node"
        node_df_con = node_coords_fromjson(self.chronograph)
        globals.node_df = node_df_con[0]
        xmax, ymax = node_df_con[1]
        # forms a dataframe from the dicitonary of coords
        x, y = self.image2.size
        cavx = x * self.imscale2
        cany = y * self.imscale2
        xscale = (x_current) * (xmax) / cavx
        yscale = (cany - y_current) * (ymax) / cany
        outline = nx.get_node_attributes(self.chronograph, "color")
        for n_ind in range(globals.node_df.shape[0]):
            if (globals.node_df.iloc[n_ind].x_lower < xscale < globals.node_df.iloc[n_ind].x_upper) and (
                globals.node_df.iloc[n_ind].y_lower < yscale < globals.node_df.iloc[n_ind].y_upper
            ):
                node_inside = globals.node_df.iloc[n_ind].name
                outline[node_inside] = "red"
                nx.set_node_attributes(self.chronograph, outline, "color")
        return node_inside

    def chrono_nodes(self, current):
        """scales the nodes on chronodag"""
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        return node
