import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser  # Import to handle opening URLs
from terminal import Terminal
from file_manager import FileManager
from mod_manager import ModManager
from player_management import PlayerManagement
from discord_tools import DiscordTools
from info import Info
from game_settings import GameSettings
from system import System
from mods import Mods

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Node Manager - Game Server Manager V1.0.2")
        self.configure(bg="#1E1E2E")  # Dark background, almost black-blue

        # Define styling variables
        self.primary_bg = "#1E1E2E"  # Dark background
        self.button_color = "#7289DA"  # Purple color for buttons
        self.hover_color = "#5A6EAD"  # Darker purple for hover effect
        self.font_style = ("Segoe UI", 10)  # Font styling
        self.button_font = ("Segoe UI", 10, "bold")  # Bold font for buttons
        self.console_font = ("Consolas", 10)  # Monospace font for terminal
        self.button_style = "flat"
        self.button_radius = 5

        # Initialize API Keys (Remove if no longer needed)
        self.steam_api_key = "YOUR_STEAM_API_KEY"
        self.gsm_api_key = "RRC85N74DWOKD2SZFUBPDS6WPELZJHC"
        self.app_secret = "test123"

        # Main Layout
        main_frame = tk.Frame(self, bg=self.primary_bg)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar
        self.sidebar_frame = tk.Frame(main_frame, bg=self.primary_bg, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Create sidebar widgets
        self.create_sidebar_widgets()

        # Main Content Area (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create and add tabs
        self.create_tabs()

        # Initialize with Terminal Tab
        self.show_terminal_tab()

        # Add the menu bar
        self.create_menu_bar()

    def create_sidebar_widgets(self):
        # Header Logo Label in Sidebar
        logo_label = tk.Label(self.sidebar_frame, text="Node Manager", bg=self.primary_bg, fg=self.button_color, font=("Segoe UI", 16, "bold"))
        logo_label.pack(pady=(10, 5))

        subtitle_label = tk.Label(self.sidebar_frame, text="v1.0.2", bg=self.primary_bg, fg="#FFFFFF", font=self.font_style)
        subtitle_label.pack(pady=(0, 20))

        # Sidebar buttons
        buttons = {
            "Terminal": self.show_terminal_tab,
            "Info": self.show_info_tab,
            "Discord": self.open_discord_invite,
            "Update": self.open_github_repo,
            "Donate": self.open_donation_page
        }

        for text, command in buttons.items():
            self.create_sidebar_button(text, command)

    def create_sidebar_button(self, text, command):
        button = tk.Button(self.sidebar_frame, text=text, command=command, bg=self.button_color, fg="#FFFFFF",
                           font=self.button_font, width=20, relief="flat", borderwidth=0, pady=5, padx=5)
        button.pack(pady=5, padx=5, fill=tk.X)
        button.bind("<Enter>", lambda e, b=button: b.config(bg=self.hover_color))
        button.bind("<Leave>", lambda e, b=button: b.config(bg=self.button_color))

    def create_tabs(self):
        self.terminal_tab = Terminal(self.notebook, bg="#121212")  # Darker background for terminal
        self.file_manager_tab = FileManager(self.notebook)
        self.mod_manager_tab = Mods(self.notebook, self.steam_api_key)
        self.player_management_tab = PlayerManagement(self.notebook)
        self.discord_tools_tab = DiscordTools(self.notebook)
        self.info_tab = Info(self.notebook)

        self.system_tab = System(self.notebook)

        self.notebook.add(self.terminal_tab, text="Terminal")
        self.notebook.add(self.file_manager_tab, text="File Manager")
        self.notebook.add(self.mod_manager_tab, text="Mods Manager")
        self.notebook.add(self.player_management_tab, text="Player Manager")
        self.notebook.add(self.discord_tools_tab, text="Discord Tools")
        self.notebook.add(self.system_tab, text="System")

    def create_menu_bar(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New", command=lambda: messagebox.showinfo("New", "New File Created"))
        file_menu.add_command(label="Open", command=lambda: messagebox.showinfo("Open", "File Opened"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Node Manager - Game Server Manager V1.0.0"))

    def show_terminal_tab(self):
        self.notebook.select(self.terminal_tab)

    def show_info_tab(self):
        self.notebook.select(self.info_tab)

    def open_discord_invite(self):
        url = "https://discord.gg/W94eKGbP9Q"
        webbrowser.open(url)

    def open_github_repo(self):
        url = "https://github.com/OV3RLORDS-MODS/Node-Manager"
        webbrowser.open(url)

    def open_donation_page(self):
        url = "https://buymeacoffee.com/dale123evex"  # Replace with your actual donation page URL
        webbrowser.open(url)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()