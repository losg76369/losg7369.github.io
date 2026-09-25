import os
import re
import urllib.request

BASE = "https://iptv-org.github.io/iptv"

CATEGORIAS = {
    "peliculas": "movies",
    "entretenimiento": "entertainment",
    "kids": "kids",
    "documentales": "documentary",
    "musica": "music",
    "noticias": "news",
    "deportes": "sports",
    "ciencia": "science",
    "viajes": "travel",
    "animacion": "animation",
    "comedia": "comedy",
    "cocina": "cooking",
    "cultura": "culture",
    "educacion": "education",
    "familia": "family",
    "series": "series",
    "clima": "weather",
}


def descargar(url):
    print("Descargando:", url)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=60) as respuesta:
        contenido = respuesta.read().decode("utf-8")

    print("Descargados:", len(contenido), "caracteres")
    return contenido


def obtener_ids(texto):
    ids = set()

    for linea in texto.splitlines():
        if linea.startswith("#EXTINF:"):
            match = re.search(r'tvg-id="([^"]+)"', linea)

            if match:
                ids.add(match.group(1))

    return ids


os.makedirs("playlists", exist_ok=True)

print("=== DESCARGANDO LISTA ESPAÑOLA ===")

espanol = descargar(
    f"{BASE}/languages/spa.m3u"
)

ids_espanol = obtener_ids(espanol)

print("Canales españoles encontrados:", len(ids_espanol))


for nombre, categoria in CATEGORIAS.items():

    print()
    print("================================")
    print("Categoría:", nombre)
    print("================================")

    url = f"{BASE}/categories/{categoria}.m3u"

    contenido = descargar(url)

    lineas = contenido.splitlines()

    salida = ["#EXTM3U"]

    incluidos = 0

    i = 0

    while i < len(lineas):

        linea = lineas[i]

        if linea.startswith("#EXTINF:"):

            match = re.search(r'tvg-id="([^"]+)"', linea)

            if match and match.group(1) in ids_espanol:

                salida.append(linea)

                if i + 1 < len(lineas):
                    salida.append(lineas[i + 1])

                incluidos += 1

                i += 2
                continue

        i += 1

    archivo = f"playlists/{nombre}-es.m3u"

    with open(archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(salida) + "\n")

    print("Canales incluidos:", incluidos)
    print("Archivo creado:", archivo)


print()
print("=== TERMINADO ===")

print("Archivos generados:")

for archivo in os.listdir("playlists"):
    print("-", archivo)
