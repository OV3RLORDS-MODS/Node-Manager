import os
import shutil
import zipfile
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class PlayerDataManager(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#1E1E1E")
        self.parent = parent
        self.default_paths = {
            "db": os.path.expanduser(r"~\Zomboid\db"),
            "logs": os.path.expanduser(r"~\Zomboid\Logs")
        }
        self.current_path = self.default_paths["db"]
        self.original_items = []
        self.current_file = None
        self.create_widgets()
        self.list_directory()

    def create_widgets(self):
        # Path display with breadcrumb navigation
        path_frame = tk.Frame(self, bg="#1E1E1E")
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        self.path_label = tk.Label(path_frame, text=self.current_path, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12))
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Directory navigation buttons
        button_frame = tk.Frame(path_frame, bg="#1E1E1E")
        button_frame.pack(side=tk.RIGHT)

        self.select_dir_button = tk.Button(button_frame, text="Select Directory", command=self.select_directory,
                                           bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.select_dir_button.pack(side=tk.LEFT, padx=5)

        self.db_button = tk.Button(button_frame, text="Go to DB", command=self.go_to_db,
                                   bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.db_button.pack(side=tk.LEFT, padx=5)

        self.logs_button = tk.Button(button_frame, text="Go to Logs", command=self.go_to_logs,
                                     bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.logs_button.pack(side=tk.LEFT, padx=5)

        self.edit_ini_button = tk.Button(button_frame, text="Edit INI", command=self.select_ini_file,
                                         bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.edit_ini_button.pack(side=tk.LEFT, padx=5)

        self.back_button = tk.Button(button_frame, text="Back", command=self.go_back,
                                     bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat")
        self.back_button.pack(side=tk.LEFT, padx=5)

        # File operations buttons
        button_frame = tk.Frame(self, bg="#1E1E1E")
        button_frame.pack(pady=10)

        self.upload_file_button = tk.Button(button_frame, text="Upload File", command=self.upload_file,
                                            bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.upload_file_button.grid(row=0, column=0, padx=5, pady=5)

        self.upload_zip_button = tk.Button(button_frame, text="Upload ZIP", command=self.upload_zip,
                                           bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12), relief="flat", width=12)
        self.upload_zip_button.grid(row=0, column=1, padx=5, pady=5)

        # Search bar
        search_frame = tk.Frame(self, bg="#1E1E1E")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_search_results)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
        self.search_entry.pack(fill=tk.X, expand=True)

        # Directory content display
        self.listbox = tk.Listbox(self, width=80, height=20, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12),
                                 selectbackground="#004000", selectforeground="#FFFFFF")
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-1>', self.on_item_double_click)
        self.listbox.bind('<Button-3>', self.show_context_menu)

        # Context menu for right-click actions
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2E2E2E", fg="#00FF00", font=("Consolas", 12))
        self.context_menu.add_command(label="View/Edit", command=self.view_file)
        self.context_menu.add_command(label="Upload File", command=self.upload_file)
        self.context_menu.add_command(label="Upload ZIP", command=self.upload_zip)
        self.context_menu.add_command(label="Extract ZIP", command=self.extract_zip)

    def select_ini_file(self):
        """Ask the user to select an INI file and then edit it."""
        file_path = filedialog.askopenfilename(initialdir=self.current_path, title="Select INI File", filetypes=[("INI files", "*.ini")])
        if file_path:
            self.view_text_file(file_path)

    def select_directory(self):
        """Allow user to select a directory."""
        selected_directory = filedialog.askdirectory(initialdir=self.current_path, title="Select Directory")
        if selected_directory:
            self.current_path = selected_directory
            self.list_directory()

    def go_to_db(self):
        """Navigate to the db directory."""
        self.current_path = self.default_paths["db"]
        self.list_directory()

    def go_to_logs(self):
        """Navigate to the Logs directory."""
        self.current_path = self.default_paths["logs"]
        self.list_directory()

    def list_directory(self):
        """List directory contents."""
        self.path_label.config(text=self.current_path)
        self.listbox.delete(0, tk.END)
        try:
            self.original_items = sorted(os.listdir(self.current_path))
            for item in self.original_items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    item = f"[DIR] {item}"
                self.listbox.insert(tk.END, item)
            self.update_search_results()
        except FileNotFoundError:
            messagebox.showerror("Error", "The directory does not exist.")
        except PermissionError:
            messagebox.showerror("Error", "You do not have permission to access this directory.")

    def update_search_results(self, *args):
        """Update the search results based on the search query."""
        query = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        if query == "":
            for item in self.original_items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    item = f"[DIR] {item}"
                self.listbox.insert(tk.END, item)
        else:
            for item in self.original_items:
                if query in item.lower():
                    full_path = os.path.join(self.current_path, item)
                    if os.path.isdir(full_path):
                        item = f"[DIR] {item}"
                    self.listbox.insert(tk.END, item)

    def on_item_double_click(self, event):
        """Handle double-click on item."""
        selected_item = self.listbox.get(tk.ACTIVE)
        item_name = selected_item.replace("[DIR] ", "")
        new_path = os.path.join(self.current_path, item_name)
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.list_directory()
        else:
            self.view_file()

    def go_back(self):
        """Navigate to the parent directory."""
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir:
            self.current_path = parent_dir
            self.list_directory()

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        self.context_menu.post(event.x_root, event.y_root)

    def view_file(self):
        """View or edit the selected file."""
        selected_file = self.get_selected_file()
        if selected_file:
            file_path = os.path.join(self.current_path, selected_file)
            if os.path.isfile(file_path):
                if selected_file.lower().endswith('.db'):  # Assuming SQLite database file
                    self.view_database(file_path)
                else:
                    self.view_text_file(file_path)

    def view_text_file(self, file_path):
        """Open and view/edit a text file."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")
            return
        
        # Create a new window to edit the file
        editor = tk.Toplevel(self)
        editor.title(f"Editing {os.path.basename(file_path)}")
        editor.geometry("600x400")

        text_widget = tk.Text(editor, wrap=tk.WORD, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, content)
        text_widget.bind("<Control-s>", lambda event, fp=file_path: self.save_text_file(fp, text_widget.get("1.0", tk.END)))
        
        # Add a save button
        save_button = tk.Button(editor, text="Save", command=lambda: self.save_text_file(file_path, text_widget.get("1.0", tk.END)))
        save_button.pack(pady=5)

    def save_text_file(self, file_path, content):
        """Save changes to the text file."""
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            messagebox.showinfo("Success", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def get_selected_file(self):
        """Get the currently selected file from the listbox."""
        selection = self.listbox.get(tk.ACTIVE)
        if selection:
            return selection.replace("[DIR] ", "")
        return None

    def upload_file(self):
        """Upload a file to the current directory."""
        file_path = filedialog.askopenfilename(initialdir=self.current_path, title="Select File")
        if file_path:
            dest_path = os.path.join(self.current_path, os.path.basename(file_path))
            try:
                shutil.copy(file_path, dest_path)
                self.list_directory()
                messagebox.showinfo("Success", "File uploaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload file: {e}")

    def upload_zip(self):
        """Upload a ZIP file and extract it."""
        zip_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")], initialdir=self.current_path, title="Select ZIP File")
        if zip_path:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.current_path)
                self.list_directory()
                messagebox.showinfo("Success", "ZIP file extracted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract ZIP file: {e}")

    def extract_zip(self):
        """Extract a ZIP file."""
        zip_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")], initialdir=self.current_path, title="Select ZIP File")
        if zip_path:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    extract_path = filedialog.askdirectory(initialdir=self.current_path, title="Select Extract Directory")
                    if extract_path:
                        zip_ref.extractall(extract_path)
                        self.list_directory()
                        messagebox.showinfo("Success", "ZIP file extracted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract ZIP file: {e}")

    def view_database(self, db_path):
        """Open and view a SQLite database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            conn.close()

            tables_window = tk.Toplevel(self)
            tables_window.title(f"Database Tables: {os.path.basename(db_path)}")

            for idx, (table_name,) in enumerate(tables):
                table_button = tk.Button(tables_window, text=table_name, command=lambda tn=table_name: self.view_table(db_path, tn))
                table_button.pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open database: {e}")

    def view_table(self, db_path, table_name):
        """Open and view a table in the SQLite database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            rows = cursor.execute(f"SELECT * FROM {table_name};").fetchall()
            conn.close()

            table_window = tk.Toplevel(self)
            table_window.title(f"Table: {table_name}")

            text_widget = tk.Text(table_window, wrap=tk.WORD, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 12))
            text_widget.pack(fill=tk.BOTH, expand=True)

            for row in rows:
                text_widget.insert(tk.END, f"{row}\n")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to view table: {e}")

# Main application
root = tk.Tk()
root.title("Player Data Manager")
app = PlayerDataManager(root)
app.pack(fill=tk.BOTH, expand=True)
root.mainloop()