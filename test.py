import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

class DataEntryApp:
    def __init__(self):
        self.conn = sqlite3.connect('Athletics.db')
        self.curr = self.conn.cursor()

        self.win = tk.Tk()
        self.win.title("Data Entry")

        self.tables = self.get_tables()
        self.selected_table = tk.StringVar(value=self.tables[0] if self.tables else "")
        self.selected_table.trace_add('write', self.update_attributes)

        self.create_widgets()

        self.win.mainloop()

    def create_widgets(self):
        tk.Label(self.win, text="Select Table:").pack()
        tk.OptionMenu(self.win, self.selected_table, *self.tables).pack()

        self.attributes_frame = tk.Frame(self.win)
        self.attributes_frame.pack()

        self.btn_submit = tk.Button(self.win, text="Submit", command=self.submit_data)
        self.btn_submit.pack()

        for text, command in [("Add Column", self.add_column),
                              ("Drop Column", self.drop_column),
                              ("Drop Row", self.drop_row),
                              ("Drop Table", self.drop_table),
                              ("Create Table", self.create_table),
                              ("Alter Row", self.alter_row)]:
            self.create_button(text, command)

    def create_button(self, text, command):
        tk.Button(self.win, text=text, command=command, width=20).pack(pady=5)

    def get_tables(self):
        self.curr.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in self.curr.fetchall()]

    def update_attributes(self, *args):
        for widget in self.attributes_frame.winfo_children():
            widget.destroy()

        table_name = self.selected_table.get()
        if not table_name:
            return

        self.curr.execute(f"PRAGMA table_info({table_name});")
        self.attributes = [attribute[1] for attribute in self.curr.fetchall()]

        for attribute in self.attributes:
            tk.Label(self.attributes_frame, text=attribute, width=20, anchor="w").pack(fill=tk.X)
            tk.Entry(self.attributes_frame).pack(fill=tk.X)

    def submit_data(self):
        table_name = self.selected_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table")
            return

        data = [widget.get() for widget in self.attributes_frame.winfo_children() if isinstance(widget, tk.Entry)]
        if not all(data):
            messagebox.showerror("Error", "Please enter values for all attributes")
            return

        try:
            self.curr.execute(f"INSERT INTO {table_name} VALUES ({','.join(['?']*len(data))})", data)
            self.conn.commit()
            messagebox.showinfo("Success", "Data inserted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting data: {str(e)}")

        for widget in self.attributes_frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

    def add_column(self):
        table_name = self.selected_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table")
            return

        column_name = simpledialog.askstring("Add Column", "Enter column name:")
        if not column_name:
            return

        data_type = simpledialog.askstring("Add Column", "Enter data type:")
        if not data_type:
            return

        try:
            self.curr.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type}")
            self.conn.commit()
            messagebox.showinfo("Success", "Column added successfully")
            self.update_attributes()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding column: {str(e)}")

    def drop_column(self):
        table_name = self.selected_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table")
            return

        column_name = simpledialog.askstring("Drop Column", "Enter column name:")
        if not column_name:
            return

        try:
            self.curr.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
            self.conn.commit()
            messagebox.showinfo("Success", "Column dropped successfully")
            self.update_attributes()
        except Exception as e:
            messagebox.showerror("Error", f"Error dropping column: {str(e)}")

    def drop_row(self):
        table_name = self.selected_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table")
            return

        primary_key = self.attributes[0] 
        value = simpledialog.askstring("Drop Row", f"Enter {primary_key} to drop:")
        if not value:
            return

        try:
            self.curr.execute(f"DELETE FROM {table_name} WHERE {primary_key}=?", (value,))
            self.conn.commit()
            messagebox.showinfo("Success", "Row dropped successfully")
            self.update_attributes()
        except Exception as e:
            messagebox.showerror("Error", f"Error dropping row: {str(e)}")

    def drop_table(self):
        table_name = self.selected_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table")
            return

        try:
            self.curr.execute(f"DROP TABLE {table_name}")
            self.conn.commit()
            messagebox.showinfo("Success", "Table dropped successfully")
            self.update_attributes()
        except Exception as e:
            messagebox.showerror("Error", f"Error dropping table: {str(e)}")

    def create_table(self):
        table_name = simpledialog.askstring("Create Table", "Enter table name:")
        if not table_name:
            return

        attributes = []
        while True:
            attribute_name = simpledialog.askstring("Create Table", "Enter attribute name (leave empty to finish):")
            if not attribute_name:
                break
            data_type = simpledialog.askstring("Create Table", "Enter data type:")
            if not data_type:
                break
            attributes.append(f"{attribute_name} {data_type}")

        if not attributes:
            return

        try:
            self.curr.execute(f"CREATE TABLE {table_name} ({', '.join(attributes)})")
            self.conn.commit()
            messagebox.showinfo("Success", "Table created successfully")
            self.update_attributes()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating table: {str(e)}")

    def alter_row(self):
        table_name = self.selected_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table")
            return

        primary_key = self.attributes[0]  
        value = simpledialog.askstring("Alter Row", f"Enter {primary_key} to alter:")
        if not value:
            return

        self.curr.execute(f"SELECT * FROM {table_name} WHERE {primary_key}=?", (value,))
        row = self.curr.fetchone()
        if not row:
            messagebox.showerror("Error", "Row not found")
            return

        new_data = {}
        for attribute, value in zip(self.attributes[1:], row[1:]):
            new_value = simpledialog.askstring("Alter Row", f"Enter new value for {attribute} (current value: {value}):")
            if new_value is None:
                return
            new_data[attribute] = new_value

        if not new_data:
            return

        try:
            set_clause = ', '.join([f"{key}='{value}'" for key, value in new_data.items()])
            self.curr.execute(f"UPDATE {table_name} SET {set_clause} WHERE {primary_key}='{value}'")
            self.conn.commit()
            messagebox.showinfo("Success", "Row altered successfully")
            self.update_attributes()
        except Exception as e:
            messagebox.showerror("Error", f"Error altering row: {str(e)}")

app = DataEntryApp()
