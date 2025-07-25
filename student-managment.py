import pyodbc
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from ignored_file import get_conn

root = Tk()
root.title('student manager')
root.geometry('600x550')
selected_student_id = None

# --------LABEL + ENTRY

Label(root, text='fullname').grid(row=0, column=0, sticky=W, padx=5, pady=5)
entry_full = Entry(root)
entry_full.grid(row=0, column=1, padx=5)

Label(root, text='StudentNUM').grid(row=1, column=0, sticky=W, padx=5, pady=5)
entry_num = Entry(root)
entry_num.grid(row=1, column=1, padx=5)

Label(root, text='Major').grid(row=2, column=0, sticky=W, padx=5, pady=5)
entry_major = Entry(root)
entry_major.grid(row=2, column=1, padx=5)

Label(root, text='Semester').grid(row=3, column=0, sticky=W, padx=5, pady=5)
entry_sem = Entry(root)
entry_sem.grid(row=3, column=1, padx=5)


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


submit_btn = Button(root, text='Submit', command=submit_student)
submit_btn.grid(row=4, column=1, pady=10)

# ------------ Treeview

tree = ttk.Treeview(root, columns=("ID", "FullName", "StudentNUM", "Major", "Semester"), show="headings")
tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

tree.heading("ID", text="ID")
tree.heading("FullName", text="FullName")
tree.heading("StudentNUM", text="StudentNUM")
tree.heading("Major", text="Major")
tree.heading("Semester", text="Semester")


tree.column("ID", width=100, anchor="w")  # Configure column width and alignment
tree.column("FullName", width=100, anchor="w")
tree.column("StudentNUM", width=100, anchor="w")
tree.column("Major", width=100, anchor="w")
tree.column("Semester", width=100, anchor="w")

scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=5, column=2, sticky="ns")

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


btn_show = Button(root, text="show all", command=show_students)
btn_show.grid(row=4, column=0, pady=10)

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


btn_delete = Button(root, text="Delete", command=delete_student)
btn_delete.grid(row=6, column=0, pady=10)

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
            cursor.execute("SELECT * FROM StudentInfo WHERE StudentNUM = ? AND ID != ?", student_number, selected_student_id)
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


btn_update = Button(root, text="Edit", command=edit_student)
btn_update.grid(row=6, column=1, pady=10)

root.mainloop()
