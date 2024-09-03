import tkinter as tk
import webbrowser

class Donations(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.configure(bg="#1E1E2E")  # Background color

        # Create a label to guide the user
        label = tk.Label(self, text="Support us by making a donation!", bg="#1E1E2E", fg="white", font=("Segoe UI", 14, "bold"))
        label.pack(pady=20)

        # Donation button
        donate_button = tk.Button(self, text="Donate Now", command=self.open_donation_link, bg="#7289DA", fg="white", font=("Segoe UI", 12, "bold"))
        donate_button.pack(pady=20)

    def open_donation_link(self):
        url = "https://buymeacoffee.com/dale123evex"  # Replace with your actual donation link
        webbrowser.open(url)