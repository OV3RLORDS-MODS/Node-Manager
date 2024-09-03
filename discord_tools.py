import tkinter as tk
from tkinter import messagebox
import requests

class DiscordTools(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(bg="#1E1E1E")
        self.create_widgets()

    def create_widgets(self):
        # Webhook Frame
        webhook_frame = tk.Frame(self, bg="#1E1E1E")
        webhook_frame.pack(fill=tk.X, padx=10, pady=10)

        self.webhook_label = tk.Label(webhook_frame, text="Discord Webhook URL:", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 12))
        self.webhook_label.pack(side=tk.LEFT, padx=5)

        self.webhook_entry = tk.Entry(webhook_frame, bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        self.webhook_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bot Name Frame
        bot_name_frame = tk.Frame(self, bg="#1E1E1E")
        bot_name_frame.pack(fill=tk.X, padx=10, pady=5)

        self.bot_name_label = tk.Label(bot_name_frame, text="Bot Username:", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 12))
        self.bot_name_label.pack(side=tk.LEFT, padx=5)

        self.bot_name_entry = tk.Entry(bot_name_frame, bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        self.bot_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.bot_name_entry.insert(0, "Custom Bot")  # Default bot name

        # Enter Message Frame
        message_frame = tk.Frame(self, bg="#1E1E1E")
        message_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.message_label = tk.Label(message_frame, text="Enter Message:", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 12))
        self.message_label.pack(pady=5)

        self.message_title_label = tk.Label(message_frame, text="Title:", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_title_label.pack(anchor=tk.W, padx=5)
        self.message_title_entry = tk.Entry(message_frame, bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        self.message_title_entry.pack(fill=tk.X, padx=5, pady=5)

        self.message_description_label = tk.Label(message_frame, text="Description:", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_description_label.pack(anchor=tk.W, padx=5)
        self.message_description_text = tk.Text(message_frame, bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12), wrap=tk.WORD, height=5)
        self.message_description_text.pack(fill=tk.X, padx=5, pady=5)

        self.message_image_label = tk.Label(message_frame, text="Image URL:", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_image_label.pack(anchor=tk.W, padx=5)
        self.message_image_entry = tk.Entry(message_frame, bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        self.message_image_entry.pack(fill=tk.X, padx=5, pady=5)

        self.message_footer_label = tk.Label(message_frame, text="Footer:", bg="#1E1E1E", fg="#FFFFFF", font=("Segoe UI", 10))
        self.message_footer_label.pack(anchor=tk.W, padx=5)
        self.message_footer_entry = tk.Entry(message_frame, bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        self.message_footer_entry.pack(fill=tk.X, padx=5, pady=5)

        # Buttons Frame
        buttons_frame = tk.Frame(self, bg="#1E1E1E")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        self.send_custom_message_button = tk.Button(buttons_frame, text="Send Custom Message", command=self.send_custom_message, bg="#4CAF50", fg="#FFFFFF", font=("Segoe UI", 12))
        self.send_custom_message_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.start_button = tk.Button(buttons_frame, text="Send Start Message", command=self.send_start_message, bg="#4CAF50", fg="#FFFFFF", font=("Segoe UI", 12))
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = tk.Button(buttons_frame, text="Send Stop Message", command=self.send_stop_message, bg="#FF9800", fg="#FFFFFF", font=("Segoe UI", 12))
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.restart_button = tk.Button(buttons_frame, text="Send Restart Message", command=self.send_restart_message, bg="#03A9F4", fg="#FFFFFF", font=("Segoe UI", 12))
        self.restart_button.pack(side=tk.LEFT, padx=5, pady=5)

    def send_webhook(self, title, description, image_url=None, footer=None, bot_name=None):
        """Send a message to the Discord webhook URL with optional embed details."""
        webhook_url = self.webhook_entry.get()
        if not webhook_url:
            messagebox.showwarning("No Webhook URL", "Please enter a valid Discord webhook URL.")
            return

        bot_name = bot_name or "Custom Bot"  # Default bot name

        embed = {
            "title": title,
            "description": description,
            "color": 0xFF0000,  # Red color
            "image": {"url": image_url} if image_url else {},
            "footer": {"text": footer} if footer else {}
        }

        data = {
            "username": bot_name,
            "embeds": [embed]
        }

        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204:
                messagebox.showinfo("Success", "Message sent successfully.")
            else:
                messagebox.showerror("Error", f"Failed to send message: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def send_start_message(self):
        """Send a Project Zomboid themed start message."""
        title = "🧟‍♂️ **Project Zomboid: The Apocalypse Begins!** 🧟‍♀️"
        description = "The Project Zomboid server is coming online. Grab your weapons, stock up on supplies, and prepare for the chaos. The zombie horde is about to unleash its fury on the survivors. Will you make it through the first night?"
        image_url = "https://example.com/start_image.png"  # Replace with an engaging image URL
        footer = "Survival is just the beginning. Stay sharp out there!"
        bot_name = self.bot_name_entry.get()

        self.send_webhook(title, description, image_url, footer, bot_name)

    def send_stop_message(self):
        """Send a Project Zomboid themed stop message."""
        title = "🛑 **Project Zomboid: Server Down** 🛑"
        description = "The Project Zomboid server has been shut down. Take this moment to regroup and strategize. The undead are relentless, and every second counts. Prepare for the next encounter with the zombie apocalypse!"
        image_url = "https://example.com/stop_image.png"  # Replace with a relevant image URL
        footer = "The dead may rest, but the struggle continues."
        bot_name = self.bot_name_entry.get()

        self.send_webhook(title, description, image_url, footer, bot_name)

    def send_restart_message(self):
        """Send a Project Zomboid themed restart message."""
        title = "🔄 **Project Zomboid: Server Restarting** 🔄"
        description = "The Project Zomboid server is undergoing a restart. We’re fine-tuning the chaos to bring you an even more intense experience. Restock, regroup, and get ready – the undead will be waiting for you when we’re back!"
        image_url = "https://example.com/restart_image.png"  # Replace with a dynamic image URL
        footer = "Prepare yourself. The next round of chaos is on the horizon."
        bot_name = self.bot_name_entry.get()

        self.send_webhook(title, description, image_url, footer, bot_name)

    def send_custom_message(self):
        """Send a custom message to the webhook."""
        title = self.message_title_entry.get()
        description = self.message_description_text.get("1.0", tk.END).strip()
        image_url = self.message_image_entry.get()
        footer = self.message_footer_entry.get()
        bot_name = self.bot_name_entry.get()

        self.send_webhook(title, description, image_url, footer, bot_name)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Discord Webhook Sender")
    root.geometry("600x500")
    app = DiscordTools(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()