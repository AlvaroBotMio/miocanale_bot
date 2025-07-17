# pyright: reportMissingImports=false
import asyncio 
import logging
import re
import json
import os
import schedule
import time
import mimetypes
from PIL import Image

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from keep_alive import keep_alive

API_ID = 24446664
API_HASH = "ab898a2a8a40dc57ddc2094b5057bcb5"
BOT_TOKEN = "8064617865:AAEkgjMlpjiRuqLOTU4SoOUtLV7EIzpTUqU"
SESSION_NAME = "sessione"

CHANNEL_DEST = "@Promo_e_Sconti_Amazon_Temu"
CHANNEL_SOURCES = [
    "@PrezziSpaziali",
    "@offertazze",
    "@meritasconti",
    "@ScontiOffertelFacileRisparmio"
]
AMAZON_TRACKING_ID = "consigliere-21"
FILE_POSTED = "posted_messages.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if os.path.exists(FILE_POSTED):
    with open(FILE_POSTED, "r") as f:
        posted_messages = set(json.load(f))
else:
    posted_messages = set()

def save_posted_messages():
    with open(FILE_POSTED, "w") as f:
        json.dump(list(posted_messages), f)

def sostituisci_tracking_amazon(text):
    return re.sub(
        r"(https://www\.amazon\.it/[^\s]+)",
        lambda m: m.group(1).split('?')[0] + f"?tag={AMAZON_TRACKING_ID}",
        text
    )

def rimuovi_link(text):
    return re.sub(r'https?://\S+', '', text)

def ripulisci_emoticon(text):
    return text.replace("👉", "").replace("👈", "").replace("🤏", "")

def crea_caption(descrizione):
    return (
        f"{ripulisci_emoticon(descrizione.strip())}\n\n"
        "#Amazon\n\n"
        "OFFERTA A TEMPO!\n\n"
        "Venduto da Offerte lampo Amazon Store e spedito da Amazon"
    )

def crea_pulsantiera(link_amazon):
    keyboard = [
        [InlineKeyboardButton("🔵 VEDI LINK AMAZON", url=link_amazon)],
        [
            InlineKeyboardButton("YouTube", url="https://youtube.com/@creeperrambo?feature=shared"),
            InlineKeyboardButton("TikTok", url="https://www.tiktok.com/@rambocreeperr")
        ],
        [
            InlineKeyboardButton("💥👉🏻 Altro canale Telegram 👈🏻💥", url="https://t.me/Promo_e_Sconti_Amazon_Temu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def fetch_and_forward():
    messaggi_inviati = 0
    max_messaggi = 3
    bot = Bot(token=BOT_TOKEN)

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await client.start()

        try:
            await client.get_entity(CHANNEL_DEST)
            logging.info(f"✅ Il bot è membro del canale {CHANNEL_DEST}")
        except Exception as e:
            logging.error(f"❌ Il bot NON è membro del canale {CHANNEL_DEST}: {e}")
            return

        for source_channel in CHANNEL_SOURCES:
            logging.info(f"📥 Recupero messaggi da {source_channel}...")

            try:
                await client.get_entity(source_channel)
                logging.info(f"✅ L'utente Telethon può accedere a {source_channel}")
            except Exception as e:
                logging.error(f"❌ L'utente NON può accedere a {source_channel}: {e}")
                continue

            try:
                result = await client(GetHistoryRequest(
                    peer=source_channel,
                    limit=15,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                for message in reversed(result.messages):
                    if messaggi_inviati >= max_messaggi:
                        break

                    if not message.message or str(message.id) in posted_messages:
                        continue

                    testo = message.message
                    testo_modificato = sostituisci_tracking_amazon(testo)

                    match_link = re.search(r"(https://www\.amazon\.it/[^\s]+)", testo_modificato)
                    link_amazon = match_link.group(1) if match_link else "https://www.amazon.it/"

                    descrizione = rimuovi_link(testo_modificato)
                    caption = crea_caption(descrizione)
                    reply_markup = crea_pulsantiera(link_amazon)

                    try:
                        photo_obj = None
                        if message.media and hasattr(message.media, 'photo'):
                            photo_obj = message.media
                        elif hasattr(message.media, 'webpage') and hasattr(message.media.webpage, 'photo'):
                            photo_obj = message.media.webpage.photo
                            logging.info(f"📸 Immagine presa da webpage.photo")

                        if photo_obj:
                            file_path = await client.download_media(photo_obj)
                            try:
                                image = Image.open(file_path).convert("RGB")
                                jpeg_path = file_path + ".jpg"
                                image.save(jpeg_path, "JPEG")

                                with open(jpeg_path, 'rb') as photo:
                                    await asyncio.to_thread(bot.send_photo,
                                                            chat_id=CHANNEL_DEST,
                                                            photo=photo,
                                                            caption=caption[:1024],
                                                            reply_markup=reply_markup,
                                                            parse_mode='HTML',
                                                            disable_notification=True)
                                messaggi_inviati += 1
                            except Exception as e_photo:
                                logging.warning(f"⚠️ send_photo fallito: {e_photo}. Provo con send_document.")
                                try:
                                    mime_type, _ = mimetypes.guess_type(file_path)
                                    with open(file_path, 'rb') as doc:
                                        await asyncio.to_thread(bot.send_document,
                                                                chat_id=CHANNEL_DEST,
                                                                document=doc,
                                                                caption=caption[:1024],
                                                                reply_markup=reply_markup,
                                                                parse_mode='HTML',
                                                                disable_notification=True)
                                    messaggi_inviati += 1
                                except Exception as e_doc:
                                    logging.error(f"❌ Errore invio immagine come documento: {e_doc}")
                        else:
                            if message.media:
                                logging.warning(f"⚠️ Messaggio {message.id} ha media ma non è photo: {type(message.media)}")
                            else:
                                logging.info(f"ℹ️ Messaggio {message.id} senza media.")

                            await asyncio.to_thread(bot.send_message,
                                                    chat_id=CHANNEL_DEST,
                                                    text=caption,
                                                    reply_markup=reply_markup)
                            messaggi_inviati += 1

                        logging.info(f"✅ Inviato da {source_channel}: {link_amazon}")
                        posted_messages.add(str(message.id))
                        save_posted_messages()

                    except Exception as e:
                        logging.error(f"❌ Errore invio messaggio da {source_channel}: {e}")

            except Exception as e:
                logging.error(f"❌ Errore recupero da {source_channel}: {e}")

def job():
    asyncio.run(fetch_and_forward())

def start_bot():
    logging.info("🤖 Bot avviato. CTRL+C per uscire.")
    job()
    schedule.every(10).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    keep_alive()
    start_bot()
