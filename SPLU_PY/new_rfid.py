import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pymodbus.client import ModbusSerialClient
import asyncio
import src.database as db
import tkinter as tk
from tkinter import messagebox
import mysql.connector 
import time

class login_window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.master=master
        self.login_func()

    def login_func(self):
        self.master.title("LOGIN")
        self.pack(fill=tk.BOTH, expand=1)
        lbl = tk.Label(self, text="PASSWORD").grid(column=0, row=0)

        # Entry to get a input from the user
        self.pwrd = tk.Entry(self,show="*")
        self.pwrd.focus_set()
        self.pwrd.grid(column=1, row=0)

        #login button binded to a function named login
        login = tk.Button(self, text="login", width=20,command=self.check_password)
        login.grid(column=1, row=2)

    def check_password(self):
        with open("/home/admin/SPLU_PY/pass.txt") as f:
            password = f.read()

            if self.pwrd.get()==password[:-1]:
                self.master.destroy()
                root = tk.Tk()
                main_interface(root)
                root.mainloop()
                

            else:
                messagebox.showinfo("ERROR ","Password Salah")

class main_interface(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.master=master
        
        self.button_clicked = False

        self.main_func()

    def click_button(self):
        self.button_clicked = True
    
    def check_if_button_clicked(self):
        return self.button_clicked

    def close(self):
        self.master.destroy()

    def main_func(self):

        self.master.title("Daftar RFID")
        self.pack(fill=tk.BOTH, expand=1)

        rfid = SimpleMFRC522()

        title = tk.Frame(self, borderwidth=0, relief='solid', height=100, width=300, padx=20, pady=20)
        title.grid(row=0)

        content = tk.Frame(self, borderwidth=0, relief='solid', height=100, width=300, padx=20, pady=20)
        content.grid(row=1)

        rfid_value = tk.StringVar()

        title_label = tk.Label(title, borderwidth=0, relief='solid', text='Tempelkan RFID yang ingin didaftarkan', 
            font=('Arial', 28), height=3)
        title_label.grid(row=0, column=0)

        content_label = tk.Label(title, borderwidth=0, relief='solid', textvariable=rfid_value, font=('Arial', 28), height=1)
        content_label.grid(column=0, row=1)

        repeat = tk.Button(self, text="Daftarkan Kartu Lainnya", width=20, command=self.main_func)
        repeat.grid(row=2)

        # exit = tk.Button(self, text="Keluar", width=20, command=self.click_button)
        # exit.grid(row=3)

        rfid_value.set('')
        self.master.update_idletasks()


        id, text = rfid.read()
        if(id != None):
                # rfid_value.set(str(id))
            id = str(id)
    
            try:
                if(db.add_new_idtag(id)):
                    rfid_value.set("RFID Berhasil Ditambahkan!")
            except mysql.connector.errors.IntegrityError:
                rfid_value.set("RFID Sudah Terdaftar!")

        else:
            rfid_value.set('')

        self.master.update_idletasks()



if __name__ == '__main__':
    try:
        root = tk.Tk()
        login_window(root)
        # main_interface(root)
        root.mainloop()
    except KeyboardInterrupt:
        GPIO.cleanup()
    


        
