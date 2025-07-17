from telethon.sync import TelegramClient

API_ID = 24446664
API_HASH = "ab898a2a8a40dc57ddc2094b5057bcb5"
SESSION_NAME = "sessione"

if __name__ == "__main__":
    with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        # Usa il titolo o username del tuo canale privato!
        entity = client.get_entity("AlvaroParola_bot")
        print(f"✅ ID del canale: {entity.id}")
