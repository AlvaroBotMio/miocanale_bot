import re

def estrai_link_amazon(testo: str) -> str | None:
    pattern = r"(https?://(?:www\.)?amazon\.[a-z]{2,3}(?:\.[a-z]{2})?/[^\s]+)"
    match = re.search(pattern, testo)
    return match.group(1) if match else None

def converti_link_amazon(link: str) -> str:
    # Sostituisci con il tuo tag affiliato, se ne hai uno
    tag_affiliato = "tagmio-21"
    if "tag=" in link:
        link = re.sub(r"tag=[^&]+", f"tag={tag_affiliato}", link)
    elif "?" in link:
        link += f"&tag={tag_affiliato}"
    else:
        link += f"?tag={tag_affiliato}"
    return link

def deduplica(testo: str) -> str:
    # Rimuove spazi multipli e tag duplicati (versione base)
    testo = re.sub(r"\s+", " ", testo).strip()
    return testo
