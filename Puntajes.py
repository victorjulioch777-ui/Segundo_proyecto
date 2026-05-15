import os

# Nombre del directorio donde se guardarán los puntajes
DIRECTORIO_DATOS = "datos"

def obtener_ruta_puntajes(dificultad, tamano_mapa):
    """
    Construye la ruta del archivo combinando dificultad y tamaño.
    """
    return os.path.join(DIRECTORIO_DATOS, f"{dificultad}_{tamano_mapa}x{tamano_mapa}.txt")


def guardar_puntaje(dificultad, tamano_mapa, puntaje):
    """
    Guarda el puntaje y conserva los mejores veinte por dificultad y tamaño del mapa.
    """
    os.makedirs(DIRECTORIO_DATOS, exist_ok=True)

    puntajes = obtener_puntajes(dificultad, tamano_mapa)
    puntajes.append(puntaje)
    puntajes = sorted(puntajes, reverse=True)[:20]

    ruta = obtener_ruta_puntajes(dificultad, tamano_mapa)
    with open(ruta, "w", encoding="utf-8") as archivo:
        for valor in puntajes:
            archivo.write(f"{valor}\n")


def obtener_puntajes(dificultad, tamano_mapa):
    """
    Lee los puntajes guardados para la dificultad y tamano seleccionados.
    """
    ruta = obtener_ruta_puntajes(dificultad, tamano_mapa)
    if not os.path.exists(ruta):
        return []

    puntajes = []
    with open(ruta, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue
            try:
                puntajes.append(int(linea))
            except ValueError:
                continue

    return sorted(puntajes, reverse=True)
