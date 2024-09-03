import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import psutil
import threading
import time
import re

class Terminal(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.batch_file_path = None
        self.process = None
        self.console_output = []
        self.configure(bg='#2e2e2e')
        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self, bg='#2e2e2e')
        header_frame.pack(pady=10, fill=tk.X)

        button_frame = tk.Frame(header_frame, bg='#2e2e2e')
        button_frame.pack(side=tk.LEFT, padx=10)

        # Modern Button Class
        class ModernButton(tk.Button):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.config(
                    relief='flat',
                    bg='#444444',
                    fg='#00FF00',
                    font=('Arial', 10, 'bold'),
                    borderwidth=1,
                    highlightbackground='#00FF00'
                )
                self.bind("<Enter>", self.on_hover)
                self.bind("<Leave>", self.on_leave)
                self.bind("<Button-1>", self.on_click)
                self.original_bg = self.cget('background')
                self.hover_bg = '#555555'
                self.click_bg = '#666666'
                self.original_fg = self.cget('foreground')
                self.hover_fg = '#FFFFFF'

            def on_hover(self, event):
                self.config(bg=self.hover_bg, fg=self.hover_fg)

            def on_leave(self, event):
                self.config(bg=self.original_bg, fg=self.original_fg)

            def on_click(self, event):
                self.config(bg=self.click_bg)

        # Buttons
        self.select_button = ModernButton(button_frame, text="Select Batch", command=self.select_batch_file, width=12, height=2)
        self.select_button.grid(row=0, column=0, padx=5)

        self.start_button = ModernButton(button_frame, text="Start Server", command=self.start_server, width=12, height=2)
        self.start_button.grid(row=0, column=1, padx=5)

        self.restart_button = ModernButton(button_frame, text="Restart Server", command=self.restart_server, width=12, height=2)
        self.restart_button.grid(row=0, column=2, padx=5)

        self.stop_button = ModernButton(button_frame, text="Stop Server", command=self.stop_server, width=12, height=2)
        self.stop_button.grid(row=0, column=3, padx=5)

        # Search Box
        search_frame = tk.Frame(header_frame, bg='#2e2e2e')
        search_frame.pack(side=tk.RIGHT, padx=10)

        self.search_entry = tk.Entry(search_frame, font=('Arial', 10), bg='#333333', fg='#00FF00', borderwidth=1, relief='flat')
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_console)

        self.search_button = ModernButton(search_frame, text="Search", command=self.filter_console, width=8, height=1)
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Console Output
        self.console_frame = tk.Frame(self, bg='#2e2e2e')
        self.console_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(self.console_frame, height=15, wrap=tk.WORD, bg='#000000', fg='#00FF00',
                                    font=('Consolas', 10), state=tk.DISABLED)
        self.console_text.pack(fill=tk.BOTH, expand=True)

    def select_batch_file(self):
        self.batch_file_path = filedialog.askopenfilename(
            title="Select Batch File",
            filetypes=[("Batch files", "*.bat"), ("All files", "*.*")]
        )

        if self.batch_file_path:
            self.start_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)

    def start_server(self):
        if self.batch_file_path and self.process is None:
            try:
                self.process = subprocess.Popen(
                    [self.batch_file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    shell=True
                )
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, "Server started...\n")
                self.console_text.config(state=tk.DISABLED)
                self.read_output()
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.restart_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server: {e}")

    def stop_server(self):
        if self.process:
            try:
                parent_pid = self.process.pid
                parent = psutil.Process(parent_pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                self.process.wait()  # Wait for process to terminate
                
                # Allow some time for graceful shutdown
                time.sleep(5)
                if parent.is_running():
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
                
                self.process = None
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.DISABLED)
                self.console_text.config(state=tk.NORMAL)
                self.console_text.insert(tk.END, "Server stopped.\n")
                self.console_text.config(state=tk.DISABLED)
            except psutil.NoSuchProcess as e:
                messagebox.showerror("Error", f"Process not found: {e}")
            except psutil.AccessDenied as e:
                messagebox.showerror("Error", f"Access denied: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop server: {e}")
        else:
            messagebox.showwarning("Warning", "No server is running.")

    def restart_server(self):
        if self.process:
            self.stop_server()
            # Wait for the stop operation to complete before starting the server again
            time.sleep(2)  # You may adjust the sleep duration based on your needs
        self.start_server()

    def read_output(self):
        if self.process:
            def stream_output():
                for line in iter(self.process.stdout.readline, ''):
                    self.console_output.append(line)
                    self.console_text.config(state=tk.NORMAL)
                    self.console_text.insert(tk.END, line)
                    self.console_text.yview(tk.END)
                    self.console_text.config(state=tk.DISABLED)
                for line in iter(self.process.stderr.readline, ''):
                    self.console_output.append(line)
                    self.console_text.config(state=tk.NORMAL)
                    self.console_text.insert(tk.END, line)
                    self.console_text.yview(tk.END)
                    self.console_text.config(state=tk.DISABLED)

            threading.Thread(target=stream_output, daemon=True).start()

    def filter_console(self, event=None):
        search_text = self.search_entry.get()
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete('1.0', tk.END)
        filtered_output = [line for line in self.console_output if re.search(search_text, line, re.IGNORECASE)]
        self.console_text.insert(tk.END, ''.join(filtered_output))
        self.console_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Server Terminal")
    terminal = Terminal(root)
    terminal.pack(fill="both", expand=True)
    root.mainloop()