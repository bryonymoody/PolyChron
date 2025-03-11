import tkinter as tk
from tkinter import ttk


class popupWindow2(object):
    def __init__(self, master, graph, canvas):
        """initiliases popup2"""
        self.top = tk.Toplevel(master)
        self.top.title("Adding new supplementary data")
        self.top.configure(bg="#AEC7D6")
        self.top.geometry("1000x400")
        # this popup window lets us change the metadata after popupwindow has gone
        self.graph = graph
        self.canvas2 = tk.Canvas(self.top)
        self.canvas2.place(relx=0, rely=0, relwidth=1, relheight=1)
        #        #making node add section
        # defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self.top)
        self.variable_b = tk.StringVar(self.top)
        self.variable_c = tk.StringVar(self.top)
        self.variable_d = tk.StringVar(self.top)
        self.label4 = ttk.Label(self.canvas2)
        self.entry4 = ttk.Entry(self.canvas2)
        self.label5 = ttk.Label(self.canvas2)
        self.entry5 = ttk.Entry(self.canvas2)
        self.label6 = ttk.Label(self.canvas2)
        self.entry6 = ttk.Entry(self.canvas2)
        #        #entry box for adding metadata
        self.entry3 = ttk.Entry(self.canvas2)
        #  self.button3 = ttk.Button(self.top, text='Add Metadata to node', command=self.testcom())#need to add command
        self.label3 = ttk.Label(self.canvas2, text="Node")
        self.canvas2.create_window(40, 60, window=self.entry3, width=50)
        self.canvas2.create_window(40, 35, window=self.label3)
        # needs way more detail adding to this
        self.dict = {
            "Find Type": ["Find1", "Find2", "Find3"],
            "Determination": ["None", "Input date"],
            "Group": ["None", "Input Group"],
        }
        #       #defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self.top)
        self.variable_b = tk.StringVar(self.top)
        self.variable_c = tk.StringVar(self.top)
        self.variable_d = tk.StringVar(self.top)
        self.optionmenu_a = ttk.OptionMenu(self.top, self.variable_a, list(self.dict.keys())[0], *self.dict.keys())
        self.optionmenu_b = ttk.OptionMenu(self.top, self.variable_b, "None", "None")
        self.optionmenu_a.place(relx=0.3, rely=0.15)
        self.optionmenu_b.place(relx=0.6, rely=0.15)
        self.variable_a.trace("w", self.update_options)
        self.variable_b.trace("w", self.testdate_input)
        self.variable_c.trace("w", self.update_options)
        self.variable_d.trace("w", self.update_options)
        self.variable_a.set("Determination")

    #   self.button3.place(relx=0.1, rely=0.7)

    def testdate_input(self):
        """formats the windows so that they have the right inputs depending of if it's a date or a phase"""
        if self.variable_b.get() == "Input date":
            self.label4 = ttk.Label(self.canvas2, text="Radiocarbon Date")
            self.entry4 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry4, width=50)
            self.canvas2.create_window(90, 90, window=self.label4)
            self.label5 = ttk.Label(self.canvas2, text="Error")
            self.entry5 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(200, 130, window=self.entry5, width=50)
            self.canvas2.create_window(200, 90, window=self.label5)
        if self.variable_b.get() == "Input group":
            self.label6 = ttk.Label(self.canvas2, text="Group")
            self.entry6 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry6, width=50)
            self.canvas2.create_window(90, 90, window=self.label6)

    # def testcom(self):
    #     """metadata menu 2 update"""
    #     #these if loops clean up after user input for chaging meta data
    #     if self.variable_a.get() == "Group":
    #         if self.variable_b.get() == "Input Group":
    #             self.graph.nodes()[str(self.entry3.get())].update({"Group":self.entry6.get()})
    #             self.label6.destroy()
    #             self.entry6.destroy()
    #         else:
    #             self.graph.nodes()[str(self.entry3.get())].update({"Group":self.variable_b.get()})
    #     elif self.variable_a.get() == "Determination":
    #         if self.variable_b.get() == "Input date":
    #             self.graph.nodes()[str(self.entry3.get())].update({"Determination": [self.entry4.get(), self.entry5.get()]})
    #             self.label4.destroy()
    #             self.entry4.destroy()
    #             self.label5.destroy()
    #             self.entry5.destroy()
    #         else:
    #             self.graph.nodes()[str(self.entry3.get())].update({"Determination":self.variable_b.get()})
    #     elif self.variable_a.get() == "Find_Type":
    #         self.graph.nodes()[str(self.entry3.get())].update({"Find_Type":self.variable_b.get()})
    # #    self.canvas2.create_window((0, 0), window=self.metatext, anchor='nw')
    #     self.meta1 = pd.DataFrame.from_dict(self.graph.nodes()[str(self.entry3.get())],
    #                                         orient='index')
    #     self.meta2 = self.meta1.loc["Determination":"Group",]
    #     self.meta2.columns = ["Data"]
    #     if self.meta2.loc["Determination"][0] != "None":
    #         self.meta2.loc["Determination"][0] = str(self.meta2.loc["Determination"][0][0]) + " +- " + str(self.meta2.loc["Determination"][0][1]) + " Carbon BP"
    #     #self.canvas.itemconfig(self.metatext_id, text="Metadata of node " + str(self.entry3),  font='helvetica 12 bold')
    #     cols = list(self.meta2.columns)
    #     tree = ttk.Treeview(self.canvas)
    #     tree["columns"] = cols
    #     tree.place(relx=0.76, rely=0.65)
    #     tree.column("Data", anchor="w")
    #     tree.heading("Data", text="Data", anchor='w')
    #     for index, row in self.meta2.iterrows():
    #         tree.insert("", 0, text=index, values=list(row))

    def update_options(self, *args):
        """updates metadata drop down menu 1"""
        meta_data = self.dict[self.variable_a.get()]
        self.variable_b.set(meta_data[0])
        menu = self.optionmenu_b["menu"]
        menu.delete(0, "end")
        for meta in meta_data:
            menu.add_command(label=meta, command=lambda nation=meta: self.variable_b.set(nation))

    def cleanup(self):
        """cleans up popup2"""
        self.top.destroy()
