import os

# Nombre del directorio donde se guardarán los puntajes
DIRECTORIO_DATOS = "datos"

# Rutas completas a los archivos de puntajes, según el tamaño del mapa
RUTAS_PUNTAJES = {
    10: os.path.join(DIRECTORIO_DATOS, "top_10x10.txt"),
    20: os.path.join(DIRECTORIO_DATOS, "top_20x20.txt"),
    30: os.path.join(DIRECTORIO_DATOS, "top_30x30.txt")
}


def guardar_puntaje(tamano_mapa, puntaje):
    """
    Guarda el puntaje y conserva los mejores cinco por tamano de mapa.
    """
    os.makedirs(DIRECTORIO_DATOS, exist_ok=True)

    puntajes = obtener_puntajes(tamano_mapa)
    puntajes.append(puntaje)
    puntajes = sorted(puntajes, reverse=True)[:5]

    with open(RUTAS_PUNTAJES[tamano_mapa], "w", encoding="utf-8") as archivo:
        for valor in puntajes:
            archivo.write(f"{valor}\n")


def obtener_puntajes(tamano_mapa):
    """
    Lee los puntajes guardados para el tamano seleccionado.
    """
    ruta = RUTAS_PUNTAJES.get(tamano_mapa)
    if ruta is None or not os.path.exists(ruta):
        return []

    puntajes = []
    with open(ruta, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea.isdigit():
                puntajes.append(int(linea))

    return sorted(puntajes, reverse=True)
