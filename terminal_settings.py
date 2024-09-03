# terminal.settings.py

import requests
import json

# Settings storage
settings_file = 'settings.json'

def load_settings():
    if not os.path.exists(settings_file):
        return {"discord_webhook_url": None, "discord_channel_id": None}
    
    with open(settings_file, 'r') as f:
        return json.load(f)

def save_settings(discord_webhook_url=None, discord_channel_id=None):
    settings = load_settings()
    if discord_webhook_url is not None:
        settings["discord_webhook_url"] = discord_webhook_url
    if discord_channel_id is not None:
        settings["discord_channel_id"] = discord_channel_id
    with open(settings_file, 'w') as f:
        json.dump(settings, f)

def send_discord_message(message):
    settings = load_settings()
    webhook_url = settings.get("discord_webhook_url")
    if webhook_url:
        payload = {
            "content": message,
            "embeds": [{"description": f"Channel ID: {settings.get('discord_channel_id')}", "color": 5814783}]
        }
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code != 204:
                print(f"Failed to send message: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending message: {e}")