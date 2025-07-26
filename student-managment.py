from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from ignored_file import get_conn
from Login_window import LoginWindow

root = Tk()
root.title('student manager')
root.geometry('650x600')
root.resizable(False, False)
root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure(0, weight=1)

selected_student_id = None

style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
                background="#f9f9f9",
                foreground="#222",
                rowheight=28,
                fieldbackground="#f9f9f9",
                font=('Segoe UI', 10))

style.configure("Treeview.Heading",
                font=('Segoe UI', 11, 'bold'),
                background="#ddeeff",
                foreground="#000")

style.map("Treeview", background=[('selected', '#add8e6')])

title = Label(root, text="Student Management System", font=("Segoe UI", 16, "bold"))
title.grid(row=0, column=0, columnspan=4, pady=20)

# --------LABEL + ENTRY(the empty box!)

form_frame = Frame(root)
form_frame.grid(row=1, column=0, columnspan=4, pady=5)

# first row
Label(form_frame, text="Full Name:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_full = Entry(form_frame, font=('Segoe UI', 10), width=25)
entry_full.grid(row=0, column=1, padx=5, pady=5)

Label(form_frame, text="Student Number:", font=('Segoe UI', 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
entry_num = Entry(form_frame, font=('Segoe UI', 10), width=15)
entry_num.grid(row=0, column=3, padx=5, pady=5)

# second row
Label(form_frame, text="Major:", font=('Segoe UI', 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_major = Entry(form_frame, font=('Segoe UI', 10), width=20)
entry_major.grid(row=1, column=1, padx=5, pady=5)

Label(form_frame, text="Semester:", font=('Segoe UI', 10)).grid(row=1, column=2, sticky="e", padx=5, pady=5)
entry_sem = Entry(form_frame, font=('Segoe UI', 10), width=10)
entry_sem.grid(row=1, column=3, padx=5, pady=5)

# ----------- LOGIN WINDOW

Button(root, text="Login", command=lambda: LoginWindow(root)).pack()

# ----------- SUBMIT STUDENT


def submit_student():
    fullname = entry_full.get()
    student_number = entry_num.get()
    major = entry_major.get()
    semester = entry_sem.get()

    if not fullname or not student_number or not major or not semester:
        messagebox.showerror('ERROR', 'PLS fill in all fields.')
        return

    try:
        semester = int(semester)
    except ValueError:
        messagebox.showerror("Error", "Semester must be digit!")
        return

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM StudentInfo WHERE StudentNUM = ?", student_number)
            existing = cursor.fetchone()
            if existing:
                messagebox.showerror("Error", "The Student Number is already submitted!")
                return

            cursor.execute("""
                INSERT INTO StudentInfo (FullName, StudentNUM, Major, Semester)
                VALUES (?, ?, ?, ?)
            """, fullname, student_number, major, semester)
            conn.commit()

        messagebox.showinfo('success', 'Student added successfully!')
        show_students()

        entry_full.delete(0, END)
        entry_num.delete(0, END)
        entry_major.delete(0, END)
        entry_sem.delete(0, END)

    except Exception as e:
        messagebox.showerror('DB Error', f'Error occurred:\n{e}')

    finally:
        if 'conn' in locals():
            conn.close()


# ------------ Treeview

tree_frame = Frame(root)
tree_frame.grid(row=5, column=0, columnspan=4, pady=10, padx=10)

scrollbar = Scrollbar(tree_frame)
scrollbar.pack(side=RIGHT, fill=Y)

tree = ttk.Treeview(tree_frame,
                    columns=("ID", "FullName", "StudentNUM", "Major", "Semester"),
                    show="headings",
                    yscrollcommand=scrollbar.set)
tree.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar.config(command=tree.yview)

# اضافه‌کردن عنوان ستون‌ها
tree.heading("ID", text="ID")
tree.heading("FullName", text="Full Name")
tree.heading("StudentNUM", text="Student Number")
tree.heading("Major", text="Major")
tree.heading("Semester", text="Semester")

tree.column("ID", width=50, anchor=CENTER)
tree.column("FullName", width=180, anchor=W)
tree.column("StudentNUM", width=120, anchor=CENTER)
tree.column("Major", width=120, anchor=W)
tree.column("Semester", width=80, anchor=CENTER)


# -------------- SHOW STUDENTS


def show_students():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                        SELECT * FROM StudentInfo ORDER BY ID DESC
                        """)
            rows = cursor.fetchall()

        tree.delete(*tree.get_children())

        for row in rows:
            ID, fullname, studentNUM, major, semester = row
            tree.insert("", END, values=(str(ID), fullname, studentNUM, major, str(semester)))

    except Exception as e:
        messagebox.showerror("DB Error", f"{e}")
    finally:
        if 'conn' in locals():
            conn.close()


# --------------- SELECT STUDENT


def select_student(event):
    selected = tree.focus()  # ID
    if not selected:
        return

    values = tree.item(selected, "values")  # مقادیر ایتم انتخاب شده

    entry_full.delete(0, END)
    entry_full.insert(0, values[1])

    entry_num.delete(0, END)
    entry_num.insert(0, values[2])

    entry_major.delete(0, END)
    entry_major.insert(0, values[3])

    entry_sem.delete(0, END)
    entry_sem.insert(0, values[4])

    global selected_student_id
    selected_student_id = int(values[0])  # saves selected students id


tree.bind("<ButtonRelease-1>", select_student)


# ------------- DELETE STUDENT


def delete_student():
    global selected_student_id

    if not selected_student_id:
        messagebox.showerror("Error", "please select one student!")
        return

    confirm = messagebox.askyesno("Delete", "confirm deletion:")
    if not confirm:
        return

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM StudentInfo WHERE ID = ?", selected_student_id)
            conn.commit()

        messagebox.showinfo("Success", "student info is cleared!")
        show_students()  # update tree

        entry_full.delete(0, END)
        entry_num.delete(0, END)
        entry_major.delete(0, END)
        entry_sem.delete(0, END)

    except Exception as e:
        messagebox.showerror("DB Error", f"{e}")
    finally:
        if 'conn' in locals():
            conn.close()
        selected_student_id = None


# -------------- EDIT STUDENT


def edit_student():
    global selected_student_id

    if not selected_student_id:
        messagebox.showerror("Error", "please select one student!")
        return

    confirm = messagebox.askyesno("Edit", "Confirm Edit:")
    if not confirm:
        return

    fullname = entry_full.get()
    student_number = entry_num.get()
    major = entry_major.get()
    semester = entry_sem.get()

    if not fullname or not student_number or not major or not semester:
        messagebox.showerror("Error", "PLS fill in all fields.")
        return

    try:
        semester = int(semester)
    except ValueError:
        messagebox.showerror("Error", "Semester must be digits!.")
        return

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM StudentInfo WHERE StudentNUM = ? AND ID != ?", student_number,
                           selected_student_id)
            existing = cursor.fetchone()
            if existing:
                messagebox.showerror("Error", "The Student Number is already submitted!")
                return

            cursor.execute("""
                        UPDATE StudentInfo
                        SET FullName = ?, StudentNUM = ?, Major = ?, Semester = ?
                        WHERE ID = ?
                    """, fullname, student_number, major, semester, selected_student_id)
            conn.commit()

        messagebox.showinfo("Success", "student info updated!")
        show_students()

        entry_full.delete(0, END)
        entry_num.delete(0, END)
        entry_major.delete(0, END)
        entry_sem.delete(0, END)

    except Exception as e:
        messagebox.showerror("DB Error", f"{e}")


# ---------- RESET DATA


def reset_data():
    confirm = messagebox.askyesno("Reset", "Are you sure you want to delete all data? This operation cannot be undone")
    if not confirm:
        return

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM StudentInfo")
            cursor.execute("DBCC CHECKIDENT ('StudentInfo', RESEED, ?)", 0)
            conn.commit()

        tree.delete(*tree.get_children())
        entry_full.delete(0, END)
        entry_num.delete(0, END)
        entry_major.delete(0, END)
        entry_sem.delete(0, END)

        messagebox.showinfo("Reset", "All data was successfully erased.")

    except Exception as e:
        messagebox.showerror("Error", f"{e}")


# ------------ BUTTON STYLE

btn_style = {
    "font": ('Vazir', 10, 'bold'),
    "bg": "#4CAF50",
    "fg": "white",
    "width": 12,
    "padx": 5,
    "pady": 3
}

btn_frame = Frame(root)
btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

btn_submit = Button(btn_frame, text="Add", command=submit_student, width=10)
btn_edit = Button(btn_frame, text="Edit", command=edit_student, width=10)
btn_delete = Button(btn_frame, text="Delete", command=delete_student, width=10)
btn_show = Button(btn_frame, text="Show All", command=show_students, width=10)
btn_reset = Button(btn_frame, text="Reset DB", command=reset_data, width=10, bg="#9E9E9E")

btn_submit.grid(row=0, column=0, padx=5)
btn_edit.grid(row=0, column=1, padx=5)
btn_delete.grid(row=0, column=2, padx=5)
btn_show.grid(row=0, column=3, padx=5)
btn_reset.grid(row=0, column=4, padx=5)

root.mainloop()
