import tkinter as tk
from tkinter import messagebox
from db_config import get_conn
from tkinter import *
from tkinter import Toplevel


class LoginWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.parent = parent
        self.win.title("Login")
        self.win.geometry("400x400")
        self.win.resizable(False, False)
        self.win.grab_set()

        # ------  UH DESIGN

        tk.Label(self.win, text="Username:").grid(row=0, column=0, padx=10, pady=(20, 5), sticky="e")
        self.user_entry = tk.Entry(self.win, width=25)
        self.user_entry.grid(row=0, column=1, pady=(20, 5), padx=5)

        tk.Label(self.win, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.pas_entry = tk.Entry(self.win, show="*", width=25)
        self.pas_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Button(self.win, text="Login", command=self.handle_login).grid(row=2, column=0, columnspan=2, pady=15)

        self.user_entry.focus()

    def handle_login(self):
        user = self.user_entry.get()
        pas = self.pas_entry.get()

        try:
            with get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM LoginInfo WHERE Username=? AND Password=?", (user, pas))
                result = cursor.fetchone()

            if result:
                self.win.destroy()
                self.parent.deiconify()
            else:
                messagebox.showerror("Login Failed!", "Invalid username or Password")

        except Exception as e:
            messagebox.showerror("Database Error", f"{e}")