import logging
from telegram import InputFile
import aiohttp
import os
import tempfile

logger = logging.getLogger(__name__)

async def invia_immagine_compatibile_ios(bot, chat_id, image_url, caption):
    try:
        # Scarica l'immagine da URL in un file temporaneo
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    raise Exception(f"Errore download immagine: {resp.status}")
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(await resp.read())
                    tmp_file_path = tmp_file.name

        # Invia l'immagine come documento per compatibilità iOS
        with open(tmp_file_path, "rb") as img:
            await bot.send_document(chat_id=chat_id, document=InputFile(img), caption=caption, parse_mode="HTML")

        # Pulisce il file temporaneo
        os.remove(tmp_file_path)

    except Exception as e:
        logger.error(f"❌ Errore invio immagine iOS compatibile: {e}")
