import tkinter as tk


class popupWindow6(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        top.configure(bg="white")
        self.top.geometry("1000x400")
        self.top.title("Removal of stratigraphic relationship")
        self.l = tk.Label(
            top,
            text="Why are you deleting the stratigraphic relationship between these contexts?",
            bg="white",
            font="helvetica 12",
            fg="#2f4858",
        )
        self.l.place(relx=0.3, rely=0.1)
        self.e = tk.Text(top, font="helvetica 12", fg="#2f4858")
        self.e.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)
        self.b = tk.Button(top, text="OK", command=self.cleanup, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.b.place(relx=0.3, rely=0.7)

    def cleanup(self):
        self.value = self.e.get("1.0", "end")
        self.top.destroy()
