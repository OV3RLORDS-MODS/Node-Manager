import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, colorchooser
import subprocess
import threading
import json
import os
import psutil
import datetime

class Terminal(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.batch_file_path = None
        self.process = None
        self.running = False
        self.booting_up = False
        self.server_info = {
            "IP": "N/A",
            "Port": "N/A",
            "Player Slots": "N/A",
            "CPU Usage": "N/A",
            "Memory Usage": "N/A",
            "Last Crash": "N/A",
            "Last Closed": "N/A",
            "Last Restart": "N/A"
        }
        self.server_info_labels = {}
        self.command_history = []
        self.history_index = -1
        self.text_color = '#00FF00'  # Default text color
        self.bg_color = '#1E1E1E'    # Default background color

        self.configure(bg=self.bg_color)
        self.create_widgets()
        self.update_styles()

        # Load last used batch file and command history
        self.load_last_batch_file()
        self.load_command_history()

    def create_widgets(self):
        # Header Frame
        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(pady=10, fill=tk.X)

        # Buttons in Header
        button_frame = tk.Frame(header_frame, bg=self.bg_color)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        self.select_button = tk.Button(
            button_frame, text="Select Batch File", command=self.select_batch_file,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.select_button.grid(row=0, column=0, padx=5)

        self.start_button = tk.Button(
            button_frame, text="Start Server", command=self.start_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.start_button.grid(row=0, column=1, padx=5)

        self.restart_button = tk.Button(
            button_frame, text="Restart Server", command=self.restart_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.restart_button.grid(row=0, column=2, padx=5)

        self.stop_button = tk.Button(
            button_frame, text="Stop Server", command=self.stop_server,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2', state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=3, padx=5)

        self.edit_db_button = tk.Button(
            button_frame, text="EDIT DB", command=self.edit_db,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.edit_db_button.grid(row=0, column=4, padx=5)

        self.color_button = tk.Button(
            button_frame, text="Change Text Color", command=self.change_text_color,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.color_button.grid(row=0, column=5, padx=5)

        self.bg_color_button = tk.Button(
            button_frame, text="Change Background Color", command=self.change_background_color,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.bg_color_button.grid(row=0, column=6, padx=5)

        # Console Frame
        self.console_frame = tk.Frame(self, bg=self.bg_color)
        self.console_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.console_text = scrolledtext.ScrolledText(
            self.console_frame, height=20, wrap=tk.WORD,
            bg=self.bg_color, fg=self.text_color, font=('Consolas', 12), state=tk.DISABLED
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)

        # Command Entry and Execute Button
        self.command_box_frame = tk.Frame(self, bg=self.bg_color)
        self.command_box_frame.pack(fill=tk.X, padx=10, pady=5)

        self.command_entry = tk.Entry(
            self.command_box_frame, font=('Consolas', 12),
            bg='#2E2E2E', fg=self.text_color, insertbackground='white'
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.send_command)

        self.execute_button = tk.Button(
            self.command_box_frame, text="Execute", command=self.send_command,
            bg='#2E2E2E', fg=self.text_color, font=('Consolas', 12), relief='flat', cursor='hand2'
        )
        self.execute_button.pack(side=tk.RIGHT, padx=5)

        # Server Info and Status Frame at the bottom
        bottom_frame = tk.Frame(self, bg=self.bg_color, bd=2, relief='solid')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.status_indicator = tk.Canvas(bottom_frame, width=20, height=20, bg=self.bg_color, highlightthickness=0)
        self.status_indicator.grid(row=0, column=0, padx=10)

        self.status_text = tk.Label(
            bottom_frame, text="Offline", fg='#FF0000', bg=self.bg_color, font=('Consolas', 12)
        )
        self.status_text.grid(row=0, column=1, padx=(5, 10))

        # Server Info Labels
        server_info_labels = [
            "IP", "Port", "Player Slots", "CPU Usage", "Memory Usage",
            "Last Crash", "Last Closed", "Last Restart"
        ]
        for idx, key in enumerate(server_info_labels):
            label = tk.Label(
                bottom_frame, text=f"{key}:", fg=self.text_color, bg=self.bg_color, font=('Consolas', 12, 'bold')
            )
            label.grid(row=0, column=2 + 2 * idx, padx=(10, 2), pady=5, sticky=tk.W)
            value = tk.Label(
                bottom_frame, text=self.server_info[key], fg=self.text_color, bg=self.bg_color, font=('Consolas', 12)
            )
            value.grid(row=0, column=2 + 2 * idx + 1, padx=(2, 10), pady=5, sticky=tk.W)
            self.server_info_labels[key] = value

    def update_styles(self):
        self.configure(bg=self.bg_color)
        self.console_text.config(bg=self.bg_color, fg=self.text_color)
        self.command_entry.config(bg='#2E2E2E', fg=self.text_color, insertbackground='white')
        self.execute_button.config(bg='#2E2E2E', fg=self.text_color)
        self.status_text.config(bg=self.bg_color, fg=self.text_color)
        self.status_indicator.config(bg=self.bg_color)
        for label in self.server_info_labels.values():
            label.config(bg=self.bg_color, fg=self.text_color)

    def select_batch_file(self):
        self.batch_file_path = filedialog.askopenfilename(
            title="Select Batch File",
            filetypes=[("Batch files", "*.bat"), ("All files", "*.*")]
        )
        if self.batch_file_path:
            self.start_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.save_last_batch_file()

    def start_server(self):
        if not self.batch_file_path:
            messagebox.showwarning("Warning", "No batch file selected.")
            return

        if not self.running:
            try:
                self.booting_up = True
                self.process = subprocess.Popen(
                    [self.batch_file_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True, text=True
                )
                self.running = True
                self.booting_up = False
                self.start_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, "Server started.\n")
                self.console_text.config(state=tk.DISABLED)
                self.update_status_indicator()
                self.read_output()
                self.update_server_info()
                self.periodic_update()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server: {e}")

    def restart_server(self):
        if self.running:
            self.stop_server()
            # Wait a short while to ensure the server has fully stopped
            self.after(2000, self.start_server)
        else:
            messagebox.showwarning("Warning", "Server is not running.")

    def stop_server(self):
        if self.running:
            try:
                self.process.terminate()  # Request termination of the process
                self.process.wait(timeout=10)  # Wait for the process to terminate
                self.running = False
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, "Server stopped.\n")
                self.console_text.config(state=tk.DISABLED)
                self.start_button.config(state=tk.NORMAL)
                self.restart_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
                self.update_status_indicator()
                self.save_server_info("Last Closed")
            except subprocess.TimeoutExpired:
                self.process.kill()  # Force kill if process doesn't terminate in time
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, "Server process killed.\n")
                self.console_text.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Warning", "Server is not running.")

    def read_output(self):
        if self.process is not None:
            def enqueue_output(out, console):
                for line in iter(out.readline, b''):
                    console.config(state=tk.NORMAL)
                    console.insert(tk.END, line)
                    console.config(state=tk.DISABLED)
                    console.yview(tk.END)
                out.close()

            threading.Thread(target=enqueue_output, args=(self.process.stdout, self.console_text)).start()

    def send_command(self, event=None):
        if self.running:
            command = self.command_entry.get()
            if command:
                try:
                    self.process.stdin.write(command + "\n")
                    self.process.stdin.flush()
                    self.console_text.config(state=tk.NORMAL)
                    self.console_text.insert(tk.END, f"> {command}\n")
                    self.console_text.config(state=tk.DISABLED)
                    self.command_entry.delete(0, tk.END)
                    # Update command history
                    self.command_history.append(command)
                    self.history_index = len(self.command_history) - 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send command: {e}")
        else:
            messagebox.showwarning("Warning", "Server is not running.")

    def update_status_indicator(self):
        if self.running:
            self.status_indicator.create_oval(2, 2, 18, 18, fill="green")
            self.status_text.config(text="Online", fg="green")
        else:
            self.status_indicator.create_oval(2, 2, 18, 18, fill="red")
            self.status_text.config(text="Offline", fg="red")

    def update_server_info(self):
        self.server_info["IP"] = "127.0.0.1"  # Example data
        self.server_info["Port"] = "25565"   # Example data
        self.server_info["Player Slots"] = "20"  # Example data
        self.server_info["CPU Usage"] = f"{psutil.cpu_percent()}%"
        self.server_info["Memory Usage"] = f"{psutil.virtual_memory().percent}%"
        for key, label in self.server_info_labels.items():
            label.config(text=self.server_info[key])

    def save_server_info(self, key):
        self.server_info[key] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("server_info.json", "w") as file:
            json.dump(self.server_info, file)

    def periodic_update(self):
        if self.running:
            self.update_server_info()
            self.after(5000, self.periodic_update)

    def load_last_batch_file(self):
        if os.path.exists("last_batch_file.txt"):
            with open("last_batch_file.txt", "r") as file:
                self.batch_file_path = file.read().strip()
            if self.batch_file_path:
                self.start_button.config(state=tk.NORMAL)

    def save_last_batch_file(self):
        with open("last_batch_file.txt", "w") as file:
            file.write(self.batch_file_path)

    def load_command_history(self):
        if os.path.exists("command_history.json"):
            with open("command_history.json", "r") as file:
                self.command_history = json.load(file)

    def save_command_history(self):
        try:
            with open("command_history.json", "w") as file:
                json.dump(self.command_history, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save command history: {str(e)}")

    def change_text_color(self):
        color = colorchooser.askcolor(title="Choose text color")
        if color[1]:
            self.text_color = color[1]
            self.update_styles()

    def change_background_color(self):
        color = colorchooser.askcolor(title="Choose background color")
        if color[1]:
            self.bg_color = color[1]
            self.update_styles()

    def edit_db(self):
        # Placeholder for edit DB functionality
        messagebox.showinfo("Info", "Edit DB functionality goes here.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Server Control Panel")
    Terminal(root).pack(fill="both", expand=True)
    root.mainloop()