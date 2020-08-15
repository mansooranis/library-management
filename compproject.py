import tkinter as tk
import time
import mysql.connector as con
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import socket
import datetime
import ttkwidgets.autocomplete
from tkinter import filedialog
from tkinter import messagebox


adminmonitor = True


def sendmessage(message):
    if adminmonitor == True:
        ClientSocket = socket.socket()
        host = '127.0.0.1'
        port = 1233
        try:
            ClientSocket.connect((host, port))
        except socket.error as e:
            print(str(e))

        # Response = ClientSocket.recv(1024)
        Input = message
        ClientSocket.send(str.encode(Input))
        ClientSocket.close()
    else:
        pass


try:
    F = open("userpwd", "r+")
except FileNotFoundError:
    F = open('userpwd', 'w')

if F.readlines() == []:
    LOGIN = tk.Tk()
    str1 = tk.StringVar()
    str2 = tk.StringVar()
    str3 = tk.StringVar()
    global host, username, pwd


    def connecte():
        global str1, str2, str3, host, username, pwd
        host = str1.get()
        username = str2.get()
        pwd = str3.get()
        F.write(host)
        F.write('\n')
        F.write(username)
        F.write('\n')
        F.write(pwd)
        LOGIN.quit()
        time.sleep(1)
        LOGIN.destroy()


    label1 = tk.Label(LOGIN, text='Enter hostname (localhost):').pack()
    entry1 = tk.Entry(LOGIN, textvariable=str1)
    entry1.pack()
    entry1.insert(0, "localhost")
    label2 = tk.Label(LOGIN, text='Enter username:').pack()
    entry2 = tk.Entry(LOGIN, textvariable=str2)
    entry2.pack()
    entry2.insert(0, "root")
    label3 = tk.Label(LOGIN, text='Enter pwd:').pack()
    entry3 = tk.Entry(LOGIN, textvariable=str3, show="*").pack()
    button1 = tk.Button(LOGIN, text='Submit', command=lambda: connecte()).pack()
    LOGIN.geometry('300x300')
    LOGIN.title("login information")
    LOGIN.mainloop()

F.seek(0)
lst = F.readlines()

mydb = con.connect(
    host=lst[0].strip(),
    user=lst[1].strip(),
    password=lst[2].strip(),
    database="library"
)
if mydb.is_connected():
    db_Info = mydb.get_server_info()
    try:
        sendmessage("user logged in")
    except:
        messagebox.showerror("Error", "Server not started cannot start application")
    cursor = mydb.cursor()
F.close()


def update_payments():
    global ii
    today = datetime.datetime.now()
    date = f"{today.year}-{today.month}-{today.day}"
    cursor.execute(f"select name from customers where expectedreturnd<'{date}'")
    m = cursor.fetchall()
    try:
        for ii in range(len(m)):
            cursor.execute(
                f"update customers set payments = payments + 1, expectedreturnd = '{today + datetime.timedelta(1)}' where name='{m[ii][0]}'")
        cursor.execute(f"select name, payments,expectedreturnd from customers where name='{m[ii][0]}'")
        m = cursor.fetchall()
        mydb.commit()
    except:
        pass

update_payments()

class app(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (HomePage, issue_a_book, customers, book_entry, returnbook):
            frame = F(container, self)

            self.frames[F] = frame
            frame.config(bg="white")
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(HomePage)

        menu = tk.Menu(self)
        self.config(menu=menu)

        File = tk.Menu(menu, tearoff=False)
        File.add_command(label="Log out", command=lambda: self.log_out())
        File.add_command(label="Exit", command=lambda: exit())
        menu.add_cascade(label="File", menu=File)

        Nav = tk.Menu(menu, tearoff=False)
        Nav.add_command(label="Home Page", command=lambda: self.frames[HomePage].tkraise())
        Nav.add_command(label="Issue a book", command=lambda: self.frames[issue_a_book].tkraise())
        Nav.add_command(label="Return a book", command=lambda: self.frames[returnbook].tkraise())
        Nav.add_command(label="Add books", command=lambda: self.frames[book_entry].tkraise())
        Nav.add_command(label="Customers", command=lambda: self.frames[customers].tkraise())
        menu.add_cascade(label="Navigate", menu=Nav)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def log_out(self):
        F = open("userpwd", 'w')
        F.close()
        self.destroy()


class HomePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        pic1 = Image.open("lib4.jpg")
        self.bgimg = ImageTk.PhotoImage(pic1)
        lab = tk.Label(self, image=self.bgimg)
        lab.place(x=0, y=0, relwidth=1, relheight=1)
        # lab.pack(fill='both',expand=True)
        label1 = tk.Label(self, text="HOME PAGE", font=('Comic Sans MS', 13)).pack()
        pic = Image.open("issueabook2.png")
        self.tkpic = ImageTk.PhotoImage(pic)
        button2 = tk.Button(self, text="issue a book", command=lambda: controller.show_frame(issue_a_book),
                            image=self.tkpic).place(x=60, y=60)
        pic = Image.open("return2.png")
        self.tkpic1 = ImageTk.PhotoImage(pic)
        button3 = tk.Button(self, text="return a book", command=lambda: controller.show_frame(returnbook),
                            image=self.tkpic1).place(x=300, y=60)
        pic = Image.open("Webp.net-resizeimage (1).png")
        self.tkpic2 = ImageTk.PhotoImage(pic)
        button4 = tk.Button(self, text="add a book", command=lambda: controller.show_frame(book_entry),
                            image=self.tkpic2).place(x=60, y=220)
        pic = Image.open("cust.png")
        self.tkpic3 = ImageTk.PhotoImage(pic)
        button5 = tk.Button(self, text="add/remove customer", command=lambda: controller.show_frame(customers),
                            image=self.tkpic3).place(x=300, y=220)

    def show_home(self, controller):
        controller.show_frame(HomePage)


class issue_a_book(tk.Frame):

    def bookissued(self):
        if self.tt > 0:
            customername = self.entry2.get()
            x = datetime.datetime.now()
            date = f"{x.year}-{x.month}-{x.day}"
            newdate1 = x + datetime.timedelta(7)
            newdate = f"{newdate1.year}-{newdate1.month}-{newdate1.day}"
            cursor.execute(
                f"update customers set bookissued = '{self.bookname}', dateofissue='{date}', expectedreturnd='{newdate}' where name='{customername}'")
            labelsucces = tk.Label(self, text=f"the book is issued to {customername} for 7 days")
            labelsucces.place(x=10, y=120)
            self.update_idletasks()
            self.after(3000, labelsucces.destroy())

            cursor.execute(f"update books set availability={(self.availibilty) - 1} where name='{self.bookname}'")
            sendmessage(f"Book was issued to {customername} for 7 days")
            mydb.commit()
        else:
            labelfail = tk.Label(self, text=f"book not available in library").place(x=10, y=120)
            self.update_idletasks()
            self.after(3000, labelfail.destroy())

    def searchbook(self):
        self.bookname = self.entry.get()
        cursor.execute("use library")
        try:
            cursor.execute(f"select name,availability from books where name='{self.bookname}'")
            list = cursor.fetchall()
            self.availibilty = list[0][1]
            cursor.execute(f"select availability from books where name='{self.bookname}'")
            self.tt = cursor.fetchall()[0][0]
            self.ava_lable = tk.Label(self, text=f"availablity: {self.tt}")
            self.ava_lable.place(x=10, y=120)
            self.update_idletasks()
            self.after(3000, self.ava_lable.destroy())
        except:
            label = tk.Label(self, text="book not present").grid(row=5, column=1)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="ISSUE A BOOK", font=('Comic Sans MS', 20)).grid(column=5, columnspan=8, row=0)
        label = tk.Label(self, text="search a book").grid(column=1, row=2)
        bookname = []
        cursor.execute(f"select name from books")
        lst = cursor.fetchall()
        for i in range(len(lst)):
            bookname.append(lst[i][0])
        self.entry = ttkwidgets.autocomplete.AutocompleteCombobox(self, completevalues=bookname)
        self.entry.grid(column=1, row=3)
        label = tk.Label(self, text="customer name:").grid(column=5, row=2)
        names = []
        cursor.execute(f"select name from customers")
        lst = cursor.fetchall()
        for i in range(len(lst)):
            names.append(lst[i][0])
        self.entry2 = ttkwidgets.autocomplete.AutocompleteCombobox(self, completevalues=names)
        self.entry2.grid(column=5, row=3)
        button = tk.Button(self, text="check availibilty", command=lambda: self.searchbook()).grid(column=1, row=5)
        button1 = tk.Button(self, text="issue book?", command=lambda:
        self.bookissued())
        button1.place(x=295, y=62)


class customers(tk.Frame):

    def des(self):
        self.label1.destroy()
        self.label2.destroy()
        self.button1.destroy()
        self.entry2.destroy()
        self.entry1.destroy()
        self.label3.destroy()
        self.show_options()

    def add_multiplecust(self):
        try:
            file_path = filedialog.askopenfilename(title="Open File",
                                                   filetypes=(("comma seperated sheet", "*.csv"), ("All Files", "*.*")))
            data = pd.read_csv(file_path)
            df = pd.DataFrame(data, columns=['id', 'name', "payments"])
            for row in df.itertuples():
                cursor.execute(
                    f'INSERT INTO customers VALUES({row.id},"{row.name}","{row.payments}",NULL,NULL,NULL)')
            mydb.commit()
            lb = tk.Label(self, text="customers added")
            lb.pack()
            self.update_idletasks()
            self.after(1500, lb.destroy())
            sendmessage("multiple customers added using csv format")
        except:
            pass

    def show_customername(self):
        self.label15 = tk.Label(self, text="customer name:")
        self.label15.pack()
        names = []
        cursor.execute(f"select name from customers")
        lst = cursor.fetchall()
        for i in range(len(lst)):
            names.append(lst[i][0])
        self.entry6 = ttkwidgets.autocomplete.AutocompleteCombobox(self, completevalues=names)
        self.entry6.pack()
        self.submit = tk.Button(self, text="Submit", command=lambda: self.view_customerdet())
        self.submit.pack()

    def destroy_customer(self):
        self.label15.destroy()
        self.submit.destroy()
        self.show_options()

    def reset(self):
        self.label12.destroy()
        self.label11.destroy()
        self.entry6.destroy()
        self.bt.destroy()

    def view_customerdet(self):
        self.destroy_customer()
        self.label11 = tk.Label(self, text="customer info:")
        self.label11.pack()
        df = pd.read_sql(f"select payments,bookissued,expectedreturnd from customers where name='{self.entry6.get()}'",
                         con=mydb)
        self.label12 = tk.Label(self, text=df)
        self.label12.pack()
        self.bt = tk.Button(self, text="Reset", command=lambda: self.reset())
        self.bt.pack()

    def clean_make_payments(self):
        self.label15.destroy()
        self.submit2.destroy()
        self.entry6.destroy()
        self.entry7.destroy()
        self.label13.destroy()
        self.label14.destroy()
        self.entry7.destroy()
        self.btn2.destroy()
        self.show_options()

    def sql_make_payments(self):
        m = self.entry7.get()
        if int(self.entry7.get()) > int(self.payments):
            label20 = tk.Label(self, text="Cannot pay more than amount mentioned")
            label20.pack()
            self.update_idletasks()
            self.after(1500, lambda: label20.destroy())
        else:
            cursor.execute(
                f"update customers set payments= payments-{int(self.payments)} where name='{self.entry6.get()}'")
            label20 = tk.Label(self, text="payment done")
            label20.pack()
            sendmessage(f"{int(self.payments)} paid by {self.entry6.get()}")
            self.update_idletasks()
            self.after(1500, lambda: label20.destroy())
            mydb.commit()
            self.clean_make_payments()

    def sql_show_payments(self):
        m = self.entry6.get()
        cursor.execute(f"select payments from customers where name = '{m}'")
        self.payments = cursor.fetchall()[0][0]
        self.label14 = tk.Label(self, text=f"{m} has to pay {int(self.payments)}")
        self.label14.pack()
        self.label13 = tk.Label(self, text="Enter amount to be paid")
        self.label13.pack()
        self.entry7 = tk.Entry(self)
        self.entry7.pack()
        self.btn2 = tk.Button(self, text="Make payments", command=lambda: self.sql_make_payments())
        self.btn2.pack()

    def clear_payments(self):
        self.label15 = tk.Label(self, text="customer name:")
        self.label15.pack()
        names = []
        cursor.execute(f"select name from customers")
        lst = cursor.fetchall()
        for i in range(len(lst)):
            names.append(lst[i][0])
        self.entry6 = ttkwidgets.autocomplete.AutocompleteCombobox(self, completevalues=names)
        self.entry6.pack()
        self.submit2 = tk.Button(self, text="Submit", command=lambda: self.sql_show_payments())
        self.submit2.pack()

    def remove_customer(self):
        cursor.execute(f"select payments from customers where name='{self.entry6.get()}'")
        m = int(cursor.fetchall()[0][0])
        cursor.execute(f"select bookissued from customers where name='{self.entry6.get()}'")
        k = cursor.fetchall()[0][0]
        if m > 0:
            label = tk.Label(self, text=f"{self.entry6.get()} did not complete his payment")
            label.pack()
            self.update_idletasks()
            self.after(1500, lambda: label.destroy())
            self.label16.destroy()
            self.entry6.destroy()
            self.btn3.destroy()
            self.show_options()
        elif k != None:
            label = tk.Label(self, text=f"{self.entry6.get()} did not return his book")
            label.pack()
            self.update_idletasks()
            self.after(1500, lambda: label.destroy())
            self.label16.destroy()
            self.entry6.destroy()
            self.btn3.destroy()
            self.show_options()
        else:
            cursor.execute(f"delete from customers where name='{self.entry6.get()}'")
            mydb.commit()
            label = tk.Label(self, text="customer deleted")
            label.pack()
            self.update_idletasks()
            self.after(1500, lambda: label.destroy())
            sendmessage(f"{self.entry6.get()} was removed")
            self.label16.destroy()
            self.entry6.destroy()
            self.btn3.destroy()
            self.show_options()

    def show_removecust(self):
        self.label16 = tk.Label(self, text="customer name: ")
        self.label16.pack()
        names = []
        cursor.execute(f"select name from customers")
        lst = cursor.fetchall()
        for i in range(len(lst)):
            names.append(lst[i][0])
        self.entry6 = ttkwidgets.autocomplete.AutocompleteCombobox(self, completevalues=names)
        self.entry6.pack()
        self.btn3 = tk.Button(self, text="Remove customer?", command=lambda: self.remove_customer())
        self.btn3.pack()

    def aftersubmit(self):
        a = self.opt.get()
        if a == "Add one Customer":
            self.opt.destroy()
            self.btn1.destroy()
            self.add_onecustomer()
        elif a == "Add multiple customers(csv)":
            self.add_multiplecust()
        elif a == "View Customer details":
            self.opt.destroy()
            self.btn1.destroy()
            self.show_customername()
        elif a == "Clear payments":
            self.opt.destroy()
            self.btn1.destroy()
            self.clear_payments()
        elif a == "Remove Customer":
            self.opt.destroy()
            self.btn1.destroy()
            self.show_removecust()

    def show_options(self):
        self.OptionList = ["Add one Customer", "Add multiple customers(csv)"]
        self.opt = ttk.Combobox(self, width=30)
        self.opt["values"] = (
            "Add one Customer", "Add multiple customers(csv)", "View Customer details", "Clear payments",
            "Remove Customer")
        self.opt.pack()
        self.opt.current(2)
        self.btn1 = tk.Button(self, text="Submit", command=lambda: self.aftersubmit())
        self.btn1.pack()

    def add_new(self):
        cursor.execute(f"use library")
        cursor.execute(f"select * from customers")
        list = cursor.fetchall()
        self.int1 = list[-1][0]
        id = self.int1 + 1
        name = self.str1.get()
        flag = False
        for i in list:
            if i[1] == name:
                self.label3 = tk.Label(self, text="customer already exists")
                self.label3.pack()
                flag = True
                break
        if flag == False:
            payments = self.str2.get()
            cursor.execute(f"insert customers values({id},'{name}',{payments}, NULL,NULL,NULL);")
            self.label3 = tk.Label(self, text="Customer added")
            self.label3.pack()
            sendmessage(f"{name} was added as customers with fees {payments}")
            mydb.commit()

        self.update_idletasks()
        self.after(2000, lambda: self.des())

    def add_onecustomer(self):
        self.str1 = tk.StringVar()  # stringvar is just a string variable which is not None
        self.str2 = tk.StringVar()
        self.label1 = tk.Label(self, text='Enter new customer name:')
        self.label1.pack()
        self.entry1 = tk.Entry(self, textvariable=self.str1)
        self.entry1.pack()
        self.label2 = tk.Label(self, text='Enter entry fees:')
        self.label2.pack()
        self.entry2 = tk.Entry(self, textvariable=self.str2)
        self.entry2.pack()
        self.button1 = tk.Button(self, text='Submit', command=lambda: self.add_new())
        self.button1.pack()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.show_options()


class book_entry(tk.Frame):
    def des(self):
        self.labe1.destroy()
        self.labe2.destroy()
        self.labe3.destroy()
        self.labe5.destroy()
        self.labe6.destroy()
        self.entry1.destroy()
        self.entry2.destroy()
        self.entry4.destroy()
        self.entry5.destroy()
        self.entry6.destroy()
        self.button1.destroy()
        self.label16.destroy()

    def onebook_submit(self):
        cursor.execute(f"use library")
        cursor.execute(f"select * from books;")
        list = cursor.fetchall()
        self.int1 = list[-1][0]
        id = self.int1 + 1
        name = self.str1.get()
        author = self.str2.get()
        genre = self.str3.get()
        price = int(self.str4.get())
        quantity = 0
        quantity = int(self.str5.get())
        flag = False
        for i in list:
            if i[1] == name:
                quantity2 = i[4] + 1 + quantity
                cursor.execute(f"update books set quantity={quantity2} where '{i[1]}'={name}")
                cursor.execute(f"update books set availability={quantity2} where '{i[1]}'={name}")
                break
        cursor.execute(f"insert books values({id},'{name}','{author}','{genre}',{price},{quantity},{quantity});")
        self.label16 = tk.Label(self, text="book added")
        self.label16.pack()
        mydb.commit()
        sendmessage(f"New book added name: {name}")
        self.update_idletasks()
        self.after(2000, self.des())
        self.show_options()

    def add_onebook(self):
        self.str1 = tk.StringVar()
        self.str2 = tk.StringVar()
        self.str3 = tk.StringVar()
        self.str4 = tk.StringVar()
        self.str5 = tk.StringVar()
        self.labe1 = tk.Label(self, text="enter book name")
        self.labe1.pack()
        self.entry1 = tk.Entry(self, textvariable=self.str1)
        self.entry1.pack()
        self.labe2 = tk.Label(self, text="enter book author")
        self.labe2.pack()
        self.entry2 = tk.Entry(self, textvariable=self.str2)
        self.entry2.pack()
        self.labe3 = tk.Label(self, text="enter book genre")
        self.labe3.pack()
        self.entry4 = tk.Entry(self, textvariable=self.str3)
        self.entry4.pack()
        self.labe5 = tk.Label(self, text="enter book price")
        self.labe5.pack()
        self.entry5 = tk.Entry(self, textvariable=self.str4)
        self.entry5.pack()
        self.labe6 = tk.Label(self, text="enter quantity")
        self.labe6.pack()
        self.entry6 = tk.Entry(self, textvariable=self.str5)
        self.entry6.pack()
        self.button1 = tk.Button(self, text="submit", command=lambda: self.onebook_submit())
        self.button1.pack()

    def add_mutiplebooks(self):
        try:
            file_path = filedialog.askopenfilename(title="Open File",
                                                   filetypes=(("comma seperated sheet", "*.csv"), ("All Files", "*.*")))
            data = pd.read_csv(file_path)
            df = pd.DataFrame(data, columns=['id', 'name', "authorname", 'genre'])
            for row in df.itertuples():
                cursor.execute(
                    f'INSERT INTO books VALUES({row.id},"{row.name}","{row.authorname}","{row.genre}",NULL,NULL,NULL)')
            mydb.commit()
            lb = tk.Label(self, text="books added")
            lb.pack()
            self.update_idletasks()
            self.after(1500, lb.destroy())
            sendmessage("multiple books added using csv format")
        except:
            pass

    def check(self):
        a = self.opt.get()
        if a == "Add one book":
            self.add_onebook()
            self.opt.destroy()
            self.btn1.destroy()
        elif a == "Add multiple books(csv format)":
            self.add_mutiplebooks()

        else:
            lb = tk.Label(self, text="Invalid option selected, choose again")
            lb.pack()
            self.update_idletasks()
            self.after(1500, lb.destroy())

    def show_options(self):
        self.OptionList = ["Add one book", "Add multiple books(csv)"]
        self.opt = ttk.Combobox(self, width=30)
        self.opt["values"] = ("Add one book", "Add multiple books(csv format)")
        self.opt.pack()
        self.opt.current(0)
        self.btn1 = tk.Button(self, text="Submit", command=lambda: self.check())
        self.btn1.pack()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Add Books").pack()
        self.show_options()


class returnbook(tk.Frame):
    def destroyed(self):
        self.update_idletasks()
        self.btn1.destroy()
        self.entry.destroy()
        self.lbl.destroy()
        self.labelsucces.destroy()

    def bookreturned(self):
        cursor.execute(f"select availability from books where name='{self.entry.get()}'")
        avail = cursor.fetchall()[0][0]
        customername = self.entry2.get()
        cursor.execute(f"update books set availability={(avail) + 1} where name='{self.entry.get()}'")
        cursor.execute(f"update customers set bookissued=NULL where name='{self.entry2.get()}'")
        cursor.execute(
            f"update customers set dateofissue=Null where name='{self.entry2.get()}'")
        cursor.execute(
            f"update customers set expectedreturnd=Null where name='{self.entry2.get()}'")
        self.labelsucces = tk.Label(self, text=f"{self.entry.get()} returned by {customername}")
        self.labelsucces.place(x=10, y=120)
        mydb.commit()
        sendmessage(f"{self.entry.get()} returned by {customername}")
        self.update_idletasks()
        self.after(3000, self.destroyed())

    def check_books(self):
        try:
            customername = self.entry2.get()
            cursor.execute(f"select bookissued, expectedreturnd from customers where name='{customername}'")
            m = cursor.fetchall()
            self.bookslist = [m[0][0]]
            self.entry = ttkwidgets.autocomplete.AutocompleteCombobox(self, completevalues=self.bookslist)
            self.entry.grid(column=5, row=3)
            self.lbl = tk.Label(self, text="Book Name:")
            self.lbl.grid(column=5, row=2)
            self.btn1 = tk.Button(self, text="return book?", command=lambda: self.bookreturned())
            self.btn1.place(x=295, y=62)
        except:
            self.labelsucces = tk.Label(self, text=f"No book issued by {self.entry2.get()}")
            self.labelsucces.place(x=10, y=120)
            self.update_idletasks()
            self.after(3000, self.labelsucces.destroy())

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="RETURN A BOOK", font=('Comic Sans MS', 20)).grid(column=5, columnspan=8, row=0)
        label = tk.Label(self, text="customer name:").grid(column=1, row=2)
        names = []
        cursor.execute(f"select name from customers")
        lst = cursor.fetchall()
        for i in range(len(lst)):
            names.append(lst[i][0])
        self.entry2 = ttkwidgets.autocomplete.AutocompleteCombobox(self, completevalues=names)
        self.entry2.grid(column=1, row=3)
        button1 = tk.Button(self, text="Check books", command=lambda: self.check_books())
        button1.grid(column=1, row=5)


app = app()
app.title('Library management')
app.geometry('500x500')
app.resizable(False, False)
app.config(background='white')

app.withdraw()

def show_root():
    splashscreen.destroy()
    app.deiconify()

splashscreen = tk.Tk()
splashscreen.geometry('500x500')
splashscreen.resizable(False, False)
progress = ttk.Progressbar(splashscreen, orient='horizontal',
                       length=100, mode='determinate')

def bar():
    import time
    progress['value'] = 20
    splashscreen.update_idletasks()
    time.sleep(1)

    progress['value'] = 40
    splashscreen.update_idletasks()
    time.sleep(1)

    progress['value'] = 50
    splashscreen.update_idletasks()
    time.sleep(1)

    progress['value'] = 60
    splashscreen.update_idletasks()
    time.sleep(1)

    progress['value'] = 80
    splashscreen.update_idletasks()
    time.sleep(1)
    progress['value'] = 100

label = tk.Label(splashscreen,text="Good things take time.",font=('Comic Sans MS', 20))
label.place(y=150,x=100)

progress.place(y=220,x=200)
splashscreen.after(1000,bar)

splashscreen.after(6500,lambda:show_root())
splashscreen.title("Loading...")
splashscreen.mainloop()

app.mainloop()