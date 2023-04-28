from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import json
import socket
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import tkinter as tk

IP = "localhost"
PORT = 5566
ADDR = (IP, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")


class loginWindow:
    def __init__(self, p):
        self.top = Toplevel(p)

        Label(self.top, text="Username").grid(row=0, column=0)
        self.usEntry = Entry(self.top)
        self.usEntry.grid(row=0, column=1)

        Label(self.top, text="Password").grid(row=1, column=0)
        self.pwdEntry = Entry(self.top, show="*")
        self.pwdEntry.grid(row=1, column=1)

        Button(
            self.top, borderwidth=4, text="Login", width=10, pady=4, command=self.login
        ).grid(row=2, column=0, columnspan=2)

    def login(self):
        client.send(
            json.dumps(
                {
                    "command": "login",
                    "id": self.usEntry.get(),
                    "pwd": self.pwdEntry.get(),
                }
            ).encode()
        )
        self.recv = json.loads(client.recv(1024).decode())
        self.top.destroy()


class adminFrame(Frame):
    def __init__(self, p):
        Frame.__init__(self, p)
        self.auth = None
        self.L = []
        self.idx = -1
        self.addNewFrame("Them Nganh", "addCourse")
        self.addNewFrame("Them Truong", "addUni")
        self.addNewFrame("Them Nganh Xet Tuyen Theo Truong", "addUniCourse")
        self.addNewFrame("Them To Hop xet Tuyen", "addGroup")
        self.addNewFrame("Them Diem Thi Theo Mon", "addSubjectScore")
        self.addNewFrame("Cap nhat ket qua xet tuyen", "updateScore")
        resFrame = ttk.LabelFrame(self, text="Status", width=50)
        resFrame.grid(row=self.idx + 1, column=0, columnspan=3)
        self.scr = scrolledtext.ScrolledText(
            resFrame, width=50, height=10, wrap=WORD, state=DISABLED
        )
        self.scr.grid(row=0, column=0)

    def addNewFrame(self, name, command):
        self.idx += 1
        idx = self.idx
        addFrame = ttk.LabelFrame(self, text=name)
        addFrame.grid(row=idx, column=0, columnspan=3, sticky="ew", pady=5)
        self.L.append(Label(addFrame, text="Chon File...", width=30))
        self.L[idx].grid(row=0, column=0)
        Button(addFrame, text="Chon File", command=lambda: self.choose(idx)).grid(
            row=0, column=2
        )
        Button(addFrame, text="Them", command=lambda: self.add(command, idx)).grid(
            row=0, column=4
        )

    def choose(self, idx):
        filename = askopenfilename()
        if filename == "":
            filename = "Chon File..."
        self.L[idx].configure(text=filename)

    def add(self, command, idx):
        if self.L[idx]["text"] == "Chon File...":
            messagebox.showinfo("Error", "Chon File!")
            return
        f = open(self.L[idx]["text"])
        self.scr.config(state=NORMAL)
        self.scr.delete(1.0, END)
        self.L[idx].configure(text="Chon File...")
        try:
            data = json.load(f)
            for idx, val in enumerate(data):
                self.scr.insert(INSERT, f"add data index {idx} to database...\n")
                client.send(
                    json.dumps(
                        {"command": command, "arg": val, "auth": self.auth}
                    ).encode()
                )
                self.scr.insert(INSERT, client.recv(1024).decode() + "\n")
        except:
            self.scr.insert(INSERT, "wrong json format\n")
        self.scr.config(state=DISABLED)


class mainFrame(Frame):
    def __init__(self, p):
        Frame.__init__(self, p)
        Label(self, text="Phan mem tu van tuyen sinh").grid(
            row=0, column=0, columnspan=2
        )

        Label(self, text="Chon khoi thi").grid(row=1, column=0)
        client.send(json.dumps({"command": "getGroupList"}).encode())
        self.dict = json.loads(client.recv(1024).decode())
        self.dict["chon khoi thi"] = ("Mon 1", "Mon 2", "Mon 3")
        groupList = list(self.dict.keys())
        self.group = StringVar(self)
        self.group.set(groupList[-1])
        OptionMenu(self, self.group, *groupList).grid(row=1, column=1)
        self.group.trace("w", self.updateSubject)

        Label(self, text="Chon nam").grid(row=2, column=0)
        self.year = StringVar(self)
        self.yearList = ["Chon nam"]
        self.year.set(self.yearList[0])
        self.opt = OptionMenu(self, self.year, *self.yearList)
        self.opt.grid(row=2, column=1)

        self.mon1 = Label(self, text="Mon 1")
        self.mon1.grid(row=3, column=0)
        self.diem1 = Entry(self, bd=3)
        self.diem1.grid(row=3, column=1)

        self.mon2 = Label(self, text="Mon 2")
        self.mon2.grid(row=4, column=0)
        self.diem2 = Entry(self, bd=3)
        self.diem2.grid(row=4, column=1)

        self.mon3 = Label(self, text="Mon 3")
        self.mon3.grid(row=5, column=0)
        self.diem3 = Entry(self, bd=3)
        self.diem3.grid(row=5, column=1)

        Button(self, text="xem", command=self.getScoreList).grid(
            row=6, column=1, columnspan=2
        )

        resFrame = ttk.LabelFrame(self, text="Status")
        resFrame.grid(row=7, column=0, columnspan=2)
        self.tv = ttk.Treeview(resFrame, columns=(1, 2, 3), show="headings", height=15)
        self.tv.grid(row=8, column=0)
        columns = ("Ten Truong", "Ten Nganh", "Diem Du Doan")
        self.tv["column"] = columns
        for col in columns:
            self.tv.column(col, minwidth=0, width=140, stretch=NO)
            self.tv.heading(
                col, text=col, command=lambda: self.sortColumn(self.tv, col, False)
            )

    def updateSubject(self, *args):
        self.mon1.config(text=self.dict[self.group.get()][0])
        self.mon2.config(text=self.dict[self.group.get()][1])
        self.mon3.config(text=self.dict[self.group.get()][2])
        client.send(
            json.dumps({"command": "getYearList", "group": self.group.get()}).encode()
        )
        self.yearList = list(json.loads(client.recv(1024).decode()))

        self.opt["menu"].delete(0, "end")
        self.opt["menu"].add_command(
            label="Chon nam", command=tk._setit(self.year, "Chon nam")
        )

        self.year.set("Chon nam")
        for (year,) in self.yearList:
            self.opt["menu"].add_command(label=year, command=tk._setit(self.year, year))

    def getScoreList(self):
        if self.group.get() == "chon khoi thi":
            messagebox.showinfo("Error", "Chon Khoi Thi")
            return
        try:
            d1 = float(self.diem1.get())
            d2 = float(self.diem2.get())
            d3 = float(self.diem3.get())
            assert 0 <= d1 and d1 <= 10
            assert 0 <= d2 and d2 <= 10
            assert 0 <= d3 and d3 <= 10
            score = d1 + d2 + d3
        except:
            messagebox.showinfo("Error", "Nhap diem sai cu phap")
            return
        for i in self.tv.get_children():
            self.tv.delete(i)
        client.send(
            json.dumps(
                {
                    "command": "getScoreList",
                    "group": self.group.get(),
                    "score": score,
                    "year": self.year.get(),
                }
            ).encode()
        )
        rows = json.loads(client.recv(1024).decode())
        for idx, row in enumerate(rows):
            self.tv.insert(parent="", index=idx, iid=idx, values=(row))

    def sortColumn(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children("")]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            tv.move(k, "", index)
        tv.heading(col, command=lambda: self.sortColumn(tv, col, not reverse))


class Controller:
    def __init__(self, root):
        self.root = root
        menuBar = Menu(root)
        root.config(menu=menuBar)
        self.fileMenu = Menu(menuBar, tearoff=0)
        self.fileMenu.add_command(label="Login", command=self.login)
        self.fileMenu.add_command(label="Exit")
        menuBar.add_cascade(label="Option", menu=self.fileMenu)

        self.tabControl = ttk.Notebook(root)
        self.tab1 = mainFrame(self.tabControl)
        self.tabControl.add(self.tab1, text="Trang chu")
        self.tab2 = adminFrame(self.tabControl)
        self.tabControl.pack(expand=1, fill="both")

    def login(self):
        w = loginWindow(self.root)
        self.root.wait_window(w.top)
        recv = w.recv
        messagebox.showinfo("Status", recv["status"])
        if recv["status"] == "Login success!":
            self.tabControl.add(self.tab2, text="Admin")
            self.fileMenu.entryconfig(0, label="Logout", command=self.logout)
            self.auth = recv["auth"]
            print(self.auth)
            self.tab2.auth = self.auth

    def logout(self):
        self.auth = None
        self.tabControl.forget(self.tab2)
        self.fileMenu.entryconfig(0, label="Login", command=self.login)


if __name__ == "__main__":
    root = Tk()
    Controller(root)
    root.mainloop()
