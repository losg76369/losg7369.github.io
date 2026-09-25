import re
import urllib.request
from pathlib import Path

BASE = "https://iptv-org.github.io/iptv"

CATEGORIES = {
    "movies": "peliculas-es.m3u",
    "entertainment": "entretenimiento-es.m3u",
    "kids": "kids-es.m3u",
    "documentary": "documentales-es.m3u",
    "music": "musica-es.m3u",
    "news": "noticias-es.m3u",
    "sports": "deportes-es.m3u",
    "science": "ciencia-es.m3u",
    "travel": "viajes-es.m3u",
    "animation": "animacion-es.m3u",
    "comedy": "comedia-es.m3u",
    "cooking": "cocina-es.m3u",
    "culture": "cultura-es.m3u",
    "education": "educacion-es.m3u",
    "family": "familia-es.m3u",
    "series": "series-es.m3u",
    "weather": "clima-es.m3u"
}

OUTPUT = Path("playlists")
OUTPUT.mkdir(exist_ok=True)


def download(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_m3u(text):
    entries = []

    lines = text.splitlines()

    for i in range(len(lines)):
        line = lines[i].strip()

        if not line.startswith("#EXTINF:"):
            continue

        if i + 1 >= len(lines):
            continue

        stream_url = lines[i + 1].strip()

        if not stream_url or stream_url.startswith("#"):
            continue

        match = re.search(r'tvg-id="([^"]*)"', line)

        if not match:
            continue

        tvg_id = match.group(1)

        entries.append({
            "id": tvg_id,
            "info": line,
            "url": stream_url
        })

    return entries


print("Descargando lista de canales en español...")

spanish_url = f"{BASE}/languages/spa.m3u"
spanish_playlist = download(spanish_url)

spanish_entries = parse_m3u(spanish_playlist)

spanish_ids = {
    entry["id"]
    for entry in spanish_entries
    if entry["id"]
}

print("Canales identificados como español:", len(spanish_ids))


for category, filename in CATEGORIES.items():

    print()
    print("Procesando:", category)

    category_url = f"{BASE}/categories/{category}.m3u"

    try:
        category_playlist = download(category_url)
    except Exception as error:
        print("No se pudo descargar:", error)
        continue

    category_entries = parse_m3u(category_playlist)

    selected = []
    already_added = set()

    for entry in category_entries:

        if entry["id"] not in spanish_ids:
            continue

        unique_key = (
            entry["id"],
            entry["url"]
        )

        if unique_key in already_added:
            continue

        already_added.add(unique_key)
        selected.append(entry)

    output = [
        "#EXTM3U"
    ]

    for entry in selected:
        output.append(entry["info"])
        output.append(entry["url"])

    output.append("")

    output_file = OUTPUT / filename

    output_file.write_text(
        "\n".join(output),
        encoding="utf-8"
    )

    print(
        "Canales encontrados:",
        len(selected),
        "->",
        output_file
    )

print()
print("Proceso terminado.")
