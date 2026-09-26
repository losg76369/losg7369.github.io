import json
import urllib.request
from pathlib import Path

API_BASE = "https://iptv-org.github.io/api"

CATEGORIES = {
    "movies": "Películas",
    "entertainment": "Entretenimiento",
    "kids": "Kids",
    "documentary": "Documentales",
    "music": "Música",
    "news": "Noticias",
    "sports": "Deportes",
    "science": "Ciencia",
    "travel": "Viajes",
    "animation": "Animación",
    "comedy": "Comedia",
    "cooking": "Cocina",
    "culture": "Cultura",
    "education": "Educación",
    "family": "Familia",
    "series": "Series",
    "weather": "Clima"
}

PLAYLIST_DIR = Path("playlists")


def download_json(filename):
    url = f"{API_BASE}/{filename}"

    print(f"Descargando {url}...")

    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def clean_text(text):
    if text is None:
        return ""

    return str(text).replace("\n", " ").replace("\r", " ").strip()


print("Descargando datos de IPTV-org...")

channels = download_json("channels.json")
streams = download_json("streams.json")

print(f"Canales recibidos: {len(channels)}")
print(f"Streams recibidos: {len(streams)}")

# ---------------------------------------------------------
# Crear índice de streams por ID de canal
# ---------------------------------------------------------

streams_by_channel = {}

for stream in streams:
    channel_id = stream.get("channel")

    if not channel_id:
        continue

    url = stream.get("url")

    if not url:
        continue

    streams_by_channel.setdefault(channel_id, []).append(stream)


# ---------------------------------------------------------
# Filtrar canales que tengan español
# ---------------------------------------------------------

spanish_channels = []

for channel in channels:

    languages = channel.get("languages", [])

    if "spa" not in languages:
        continue

    categories = channel.get("categories", [])

    if not categories:
        continue

    if not channel.get("id"):
        continue

    if channel["id"] not in streams_by_channel:
        continue

    spanish_channels.append(channel)


print(f"Canales en español con stream: {len(spanish_channels)}")


# ---------------------------------------------------------
# Crear directorio
# ---------------------------------------------------------

PLAYLIST_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Crear una M3U por categoría
# ---------------------------------------------------------

for category_id, category_name in CATEGORIES.items():

    entries = []

    for channel in spanish_channels:

        categories = channel.get("categories", [])

        if category_id not in categories:
            continue

        channel_id = channel["id"]
        channel_name = clean_text(channel.get("name", channel_id))

        logo = clean_text(channel.get("logo", ""))

        for stream in streams_by_channel.get(channel_id, []):

            stream_url = clean_text(stream.get("url", ""))

            if not stream_url:
                continue

            title = clean_text(stream.get("title", ""))

            if title:
                display_name = f"{channel_name} - {title}"
            else:
                display_name = channel_name

            line = f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{channel_name}"'

            if logo:
                line += f' tvg-logo="{logo}"'

            line += f' group-title="{category_name}",{display_name}'

            entries.append(line)
            entries.append(stream_url)

    output_file = PLAYLIST_DIR / f"{category_id}-es.m3u"

    with open(output_file, "w", encoding="utf-8") as file:

        file.write("#EXTM3U\n")

        for entry in entries:
            file.write(entry + "\n")

    print(
        f"{category_name}: "
        f"{len(entries) // 2} streams -> {output_file}"
    )


print("======================================")
print("Generación terminada.")
print("======================================")
