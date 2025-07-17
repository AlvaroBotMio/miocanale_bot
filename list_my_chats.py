from telethon.sync import TelegramClient

API_ID = 24446664
API_HASH = "ab898a2a8a40dc57ddc2094b5057bcb5"
SESSION_NAME = "sessione"

with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
    dialogs = client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel:
            print(f"{dialog.name} → {dialog.id}")
