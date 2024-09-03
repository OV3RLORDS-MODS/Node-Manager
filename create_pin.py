import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import time

PIN_FILE = "pin.txt"
INACTIVITY_TIMEOUT = 300  # 5 minutes in seconds

class PinManager:
    def __init__(self, root):
        self.root = root
        self.last_activity_time = time.time()

        # Styling variables
        self.bg_color = "#2E2E2E"
        self.fg_color = "#FFFFFF"
        self.highlight_color = "#4CAF50"

        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Bind key and mouse events to reset the inactivity timer
        self.root.bind_all("<Key>", self.reset_timer)
        self.root.bind_all("<Motion>", self.reset_timer)

        # Start the inactivity check loop
        self.root.after(1000, self.check_inactivity)

        # If PIN file doesn't exist, prompt the user to create a new PIN
        if not os.path.exists(PIN_FILE):
            self.create_pin()

    def create_pin(self):
        """Prompt the user to create a new 4-digit PIN."""
        while True:
            pin = simpledialog.askstring("Create PIN", "Enter a new 4-digit PIN:", show="*", initialvalue="", parent=self.root)
            if pin and len(pin) == 4 and pin.isdigit():
                with open(PIN_FILE, "w") as f:
                    f.write(pin)
                messagebox.showinfo("PIN Created", "Your PIN has been created successfully.", parent=self.root)
                break
            else:
                messagebox.showerror("Invalid PIN", "Please enter a valid 4-digit number.", parent=self.root)

    def verify_pin(self):
        """Prompt the user to enter their PIN for verification."""
        if not os.path.exists(PIN_FILE):
            messagebox.showerror("Error", "No PIN set. Please restart the application.", parent=self.root)
            self.root.quit()
            return False

        with open(PIN_FILE, "r") as f:
            stored_pin = f.read().strip()

        while True:
            pin = simpledialog.askstring("Enter PIN", "Please enter your 4-digit PIN to continue:", show="*", initialvalue="", parent=self.root)
            if pin == stored_pin:
                self.last_activity_time = time.time()
                return True
            else:
                retry = messagebox.askretrycancel("Incorrect PIN", "The PIN you entered is incorrect. Would you like to try again?", parent=self.root)
                if not retry:
                    self.root.quit()
                    return False

    def check_inactivity(self):
        """Check for user inactivity and prompt for PIN if the timeout is reached."""
        if time.time() - self.last_activity_time > INACTIVITY_TIMEOUT:
            if not self.verify_pin():
                return  # Stop further checks if PIN verification fails

        self.root.after(1000, self.check_inactivity)

    def reset_timer(self, event=None):
        """Reset the inactivity timer."""
        self.last_activity_time = time.time()

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    PinManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()