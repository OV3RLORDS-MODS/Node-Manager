import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import threading

class Terminal(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.batch_file_path = None
        self.process = None
        self.running = False
        self.server_info = {
            "Name": "N/A",
            "IP": "N/A",
            "Port": "N/A",
            "Player Slots": "N/A"
        }
        self.server_info_labels = {}
        self.command_history = []
        self.history_index = -1
        self.command_suggestions = [
            "/setaccesslevel [player name] [level]",
            "/kick [player name]",
            "/ban [player name] [reason]",
            "/spawnitem [item] [quantity]"
        ]

        self.configure(bg='#000000')
        self.create_widgets()
        self.update_styles()

    def create_widgets(self):
        header_frame = tk.Frame(self, bg='#1e1e1e')
        header_frame.pack(pady=10, fill=tk.X)

        button_frame = tk.Frame(header_frame, bg='#1e1e1e')
        button_frame.pack(side=tk.TOP, fill=tk.X)

        self.select_button = tk.Button(button_frame, text="Select Batch File", command=self.select_batch_file, bg='#007ACC', fg='#FFFFFF', font=('Consolas', 12, 'bold'), relief=tk.RAISED, bd=3)
        self.select_button.grid(row=0, column=0, padx=5)

        self.start_button = tk.Button(button_frame, text="Start Server", command=self.start_server, bg='#00FF00', fg='#000000', font=('Consolas', 12, 'bold'), relief=tk.RAISED, bd=3, state=tk.DISABLED)
        self.start_button.grid(row=0, column=1, padx=5)

        self.restart_button = tk.Button(button_frame, text="Restart Server", command=self.restart_server, bg='#FFCC00', fg='#000000', font=('Consolas', 12, 'bold'), relief=tk.RAISED, bd=3, state=tk.DISABLED)
        self.restart_button.grid(row=0, column=2, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Server", command=self.stop_server, bg='#FF0000', fg='#FFFFFF', font=('Consolas', 12, 'bold'), relief=tk.RAISED, bd=3, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=3, padx=5)

        self.edit_db_button = tk.Button(button_frame, text="EDIT DB", command=self.edit_db, bg='#007ACC', fg='#FFFFFF', font=('Consolas', 12, 'bold'), relief=tk.RAISED, bd=3)
        self.edit_db_button.grid(row=0, column=4, padx=5)

        info_frame = tk.Frame(self, bg='#000000')
        info_frame.pack(pady=10, fill=tk.X)

        columns = ['Name', 'IP', 'Port', 'Player Slots']
        for idx, key in enumerate(columns):
            label = tk.Label(info_frame, text=f"{key}:", fg='#00FF00', bg='#000000', font=('Consolas', 12))
            label.grid(row=0, column=2 * idx, padx=10, pady=2, sticky=tk.W)
            value = tk.Label(info_frame, text=self.server_info[key], fg='#FFFFFF', bg='#000000', font=('Consolas', 12))
            value.grid(row=0, column=2 * idx + 1, padx=10, pady=2, sticky=tk.W)
            self.server_info_labels[key] = value

        self.console_frame = tk.Frame(self, bg='#000000')
        self.console_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.console_text = scrolledtext.ScrolledText(self.console_frame, height=20, wrap=tk.WORD, bg='#000000', fg='#00FF00', font=('Consolas', 12), state=tk.DISABLED)
        self.console_text.pack(fill=tk.BOTH, expand=True)

        self.command_entry_frame = tk.Frame(self, bg='#000000')
        self.command_entry_frame.pack(fill=tk.X, padx=10, pady=5)

        self.command_entry = tk.Entry(self.command_entry_frame, font=('Consolas', 12), bg='#1e1e1e', fg='#00FF00', insertbackground='white')
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.send_command)
        self.command_entry.bind("<Up>", self.handle_keypress)
        self.command_entry.bind("<Down>", self.handle_keypress)
        self.command_entry.bind("<KeyRelease>", self.show_suggestions)

        self.suggestion_listbox = tk.Listbox(self.command_entry_frame, bg='#1e1e1e', fg='#00FF00', font=('Consolas', 12), selectbackground='#007ACC', height=5)
        self.suggestion_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.suggestion_listbox.bind("<Double-1>", self.select_suggestion)

    def update_styles(self):
        self.configure(bg='#000000')
        self.console_text.config(bg='#000000', fg='#00FF00')
        self.command_entry.config(bg='#1e1e1e', fg='#00FF00', insertbackground='white')
        self.suggestion_listbox.config(bg='#1e1e1e', fg='#00FF00')

    def select_batch_file(self):
        self.batch_file_path = filedialog.askopenfilename(
            title="Select Batch File",
            filetypes=[("Batch files", "*.bat"), ("All files", "*.*")]
        )

        if self.batch_file_path:
            self.start_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)

    def start_server(self):
        if self.batch_file_path:
            try:
                self.process = subprocess.Popen(
                    [self.batch_file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    shell=True
                )
                self.running = True
                self.start_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, "Server started...\n")
                self.console_text.config(state=tk.DISABLED)
                self.read_output()
                self.update_server_info()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server: {e}")

    def restart_server(self):
        if self.process:
            self.stop_server()
        self.start_server()

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process.wait()  # Ensures the process is fully terminated
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.console_text.config(state=tk.NORMAL)
            self.console_text.insert(tk.END, "Server stopped.\n")
            self.console_text.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Warning", "No server is running.")

    def send_command(self, event=None):
        command = self.command_entry.get()
        if command and self.process:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, f"> {command}\n")
                self.console_text.config(state=tk.DISABLED)
                self.command_entry.delete(0, tk.END)
                self.command_history.append(command)
                self.history_index = len(self.command_history)
                self.suggestion_listbox.place_forget()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send command: {e}")

    def read_output(self):
        if self.process:
            def stream_output():
                for line in iter(self.process.stdout.readline, ''):
                    self.console_text.config(state=tk.NORMAL)
                    self.console_text.insert(tk.END, line)
                    self.console_text.yview(tk.END)
                    self.console_text.config(state=tk.DISABLED)

                if self.process.stderr:
                    for line in iter(self.process.stderr.readline, ''):
                        self.console_text.config(state=tk.NORMAL)
                        self.console_text.insert(tk.END, line)
                        self.console_text.yview(tk.END)
                        self.console_text.config(state=tk.DISABLED)

            threading.Thread(target=stream_output, daemon=True).start()

    def update_server_info(self):
        # Dummy update; replace with actual logic to get server info
        self.server_info['Name'] = "My Server"
        self.server_info['IP'] = "127.0.0.1"
        self.server_info['Port'] = "8080"
        self.server_info['Player Slots'] = "20"

        for key, label in self.server_info_labels.items():
            label.config(text=self.server_info[key])

    def handle_keypress(self, event):
        if event.keysym == "Up":
            if self.history_index > 0:
                self.history_index -= 1
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, self.command_history[self.history_index])
        elif event.keysym == "Down":
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, self.command_history[self.history_index])
            else:
                self.command_entry.delete(0, tk.END)
                self.history_index = len(self.command_history)

    def show_suggestions(self, event=None):
        query = self.command_entry.get()
        self.suggestion_listbox.delete(0, tk.END)

        if query:
            for command in self.command_suggestions:
                if command.startswith(query):
                    self.suggestion_listbox.insert(tk.END, command)

            if self.suggestion_listbox.size() > 0:
                self.suggestion_listbox.place(x=self.command_entry.winfo_x(), y=self.command_entry.winfo_y() - self.suggestion_listbox.winfo_height())
            else:
                self.suggestion_listbox.place_forget()
        else:
            self.suggestion_listbox.place_forget()

    def select_suggestion(self, event=None):
        selected_command = self.suggestion_listbox.get(tk.ACTIVE)
        if selected_command:
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, selected_command)
            self.suggestion_listbox.place_forget()
            self.send_command()

    def edit_db(self):
        # Placeholder method to be implemented in terminal_edit_db.py
        subprocess.run(["python", "terminal_edit_db.py"])

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Server Terminal")
    terminal = Terminal(root)
    terminal.pack(fill="both", expand=True)
    root.mainloop()