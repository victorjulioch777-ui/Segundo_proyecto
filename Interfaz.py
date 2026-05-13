import pygame

from Config import (
    CELDA_OBSTACULO,
    COLOR_BOMBA,
    COLOR_FONDO,
    COLOR_JUGADOR,
    COLOR_MONEDA_ESPECIAL,
    COLOR_MONEDA_NORMAL,
    COLOR_PASO_FANTASMA,
    COLOR_TEXTO,
    TAMANO_CELDA_GUI,
    TAMANOS_MAPA,
    TIPO_BOMBA,
    TIPO_MONEDA_ESPECIAL,
    TIPO_MONEDA_NORMAL,
    TIPO_PASO_FANTASMA,
)
from Juego import Juego
from Puntajes import guardar_puntaje, obtener_puntajes


ANCHO = 1000
ALTO = 800

ventana = None
pantalla = None
reloj = None
fuente_titulo = None
fuente_subtitulo = None
fuente_boton = None
fuente_texto = None
fuente_texto_pequena = None
escala_lienzo = (1, 1)
desplazamiento_lienzo = (0, 0)

estado_pantalla = "menu"
tamano_mapa = None
tipo_mapa = None
pantalla_completa = False
juego_actual = None
mapa_actual = None
jugador = None
mensaje_juego = ""
pasos_fantasma = 0
paso_fantasma_activo = False
bombas_disponibles = 0
ultimo_desplazamiento = 0
control_en_edicion = None
mensaje_configuracion = "Haz clic en CAMBIAR y luego presiona una tecla."

CONTROLES = {
    "arriba": {"nombre": "Mover arriba", "tecla": pygame.K_w},
    "abajo": {"nombre": "Mover abajo", "tecla": pygame.K_s},
    "izquierda": {"nombre": "Mover izquierda", "tecla": pygame.K_a},
    "derecha": {"nombre": "Mover derecha", "tecla": pygame.K_d},
    "bomba": {"nombre": "Usar bomba", "tecla": pygame.K_1},
    "fantasma": {"nombre": "Usar paso fantasma", "tecla": pygame.K_2},
}


def color_hex(valor):
    return pygame.Color(valor)


def calcular_transformacion_lienzo():
    """
    Calcula la escala del lienzo virtual dentro de la ventana.
    Usa escalas independientes en X e Y para llenar toda la ventana.
    """
    if ventana is None:
        return (1, 1), (0, 0)

    ancho_ventana, alto_ventana = ventana.get_size()
    if ancho_ventana <= 0 or alto_ventana <= 0:
        return (1, 1), (0, 0)

    escala_x = ancho_ventana / ANCHO
    escala_y = alto_ventana / ALTO

    return (escala_x, escala_y), (0, 0)


def posicion_en_lienzo(posicion):
    """
    Convierte una posicion de la ventana real a coordenadas del lienzo virtual.
    """
    escala, desplazamiento = calcular_transformacion_lienzo()
    x = (posicion[0] - desplazamiento[0]) / escala[0]
    y = (posicion[1] - desplazamiento[1]) / escala[1]
    return x, y


def obtener_posicion_mouse_lienzo():
    """
    Retorna la posicion del mouse en el sistema de coordenadas de 1000x800.
    """
    return posicion_en_lienzo(pygame.mouse.get_pos())


def presentar_pantalla():
    """
    Escala el lienzo virtual para llenar toda la ventana.
    """
    global escala_lienzo
    global desplazamiento_lienzo

    escala_lienzo, desplazamiento_lienzo = calcular_transformacion_lienzo()
    ancho_ventana, alto_ventana = ventana.get_size()

    superficie_escalada = pygame.transform.smoothscale(pantalla, (ancho_ventana, alto_ventana))
    ventana.blit(superficie_escalada, (0, 0))


BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
NARANJA = (255, 145, 0)
NARANJA_OSCURO = (200, 90, 0)
VERDE = (70, 200, 90)
VERDE_OSCURO = (40, 150, 60)
GRIS = (45, 45, 45)
GRIS_CLARO = (90, 90, 90)
ROJO = (200, 60, 60)
AMARILLO = (245, 205, 90)
CELESTE = (120, 220, 255)
CAFE = (145, 90, 45)
MARRON = (115, 65, 35)

ESTILOS_MAPA = {
    "piedra": {
        "nombre": "MAPA PIEDRA",
        "piso": (105, 105, 115),
        "muro": (55, 55, 65),
        "bloque": (165, 75, 45),
        "borde": (35, 35, 40),
    },
    "arena": {
        "nombre": "MAPA ARENA",
        "piso": (230, 188, 95),
        "muro": (62, 150, 70),
        "bloque": (150, 95, 45),
        "borde": (65, 95, 45),
    },
    "hielo": {
        "nombre": "MAPA HIELO",
        "piso": (165, 230, 245),
        "muro": (80, 170, 220),
        "bloque": (155, 95, 45),
        "borde": (45, 110, 155),
    },
}


class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_hover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover

    def dibujar(self, superficie):
        posicion_mouse = obtener_posicion_mouse_lienzo()
        color_actual = self.color_hover if self.rect.collidepoint(posicion_mouse) else self.color

        pygame.draw.rect(superficie, NEGRO, self.rect.inflate(10, 10), border_radius=15)
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=15)

        texto_render = fuente_boton.render(self.texto, True, BLANCO)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        superficie.blit(texto_render, texto_rect)

    def fue_presionado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(posicion_en_lienzo(evento.pos))
        return False


def inicializar_pygame():
    global ventana
    global pantalla
    global reloj
    global fuente_titulo
    global fuente_subtitulo
    global fuente_boton
    global fuente_texto
    global fuente_texto_pequena

    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
    pantalla = pygame.Surface((ANCHO, ALTO))
    pygame.display.set_caption("Laberinto Dinamico")
    reloj = pygame.time.Clock()

    fuente_titulo = pygame.font.SysFont("arialblack", 64)
    fuente_subtitulo = pygame.font.SysFont("arialblack", 34)
    fuente_boton = pygame.font.SysFont("arialblack", 28)
    fuente_texto = pygame.font.SysFont("arial", 26)
    fuente_texto_pequena = pygame.font.SysFont("arial", 22)


boton_iniciar = None
boton_configuracion = None
boton_puntajes = None
boton_salir = None
boton_volver = None
botones_tamano = []
tarjetas_mapa = []
botones_controles = {}


def crear_botones():
    """
    Instancia los botones despues de inicializar Pygame para evitar
    usar objetos de Pygame antes de que el modulo este listo.
    """
    global boton_iniciar
    global boton_configuracion
    global boton_puntajes
    global boton_salir
    global boton_volver
    global botones_tamano
    global tarjetas_mapa
    global botones_controles

    boton_iniciar = Boton(330, 300, 340, 70, "INICIAR PARTIDA", NARANJA, NARANJA_OSCURO)
    boton_configuracion = Boton(330, 400, 340, 70, "CONFIGURACION", VERDE, VERDE_OSCURO)
    boton_puntajes = Boton(330, 500, 340, 70, "PUNTAJES", GRIS_CLARO, GRIS)
    boton_salir = Boton(330, 600, 340, 70, "SALIR", GRIS, (20, 20, 20))
    boton_volver = Boton(380, 660, 240, 70, "VOLVER", GRIS, (100, 100, 100))
    botones_tamano = [
        Boton(240 + indice * 190, 330, 150, 70, f"{tamano} x {tamano}", NARANJA, NARANJA_OSCURO)
        for indice, tamano in enumerate(TAMANOS_MAPA)
    ]
    tarjetas_mapa = [
        {"tipo": "piedra", "rect": pygame.Rect(70, 245, 260, 330)},
        {"tipo": "arena", "rect": pygame.Rect(370, 245, 260, 330)},
        {"tipo": "hielo", "rect": pygame.Rect(670, 245, 260, 330)},
    ]
    botones_controles = {
        "arriba": Boton(680, 210, 190, 48, "CAMBIAR", NARANJA, NARANJA_OSCURO),
        "abajo": Boton(680, 280, 190, 48, "CAMBIAR", NARANJA, NARANJA_OSCURO),
        "izquierda": Boton(680, 350, 190, 48, "CAMBIAR", NARANJA, NARANJA_OSCURO),
        "derecha": Boton(680, 420, 190, 48, "CAMBIAR", NARANJA, NARANJA_OSCURO),
        "bomba": Boton(680, 490, 190, 48, "CAMBIAR", NARANJA, NARANJA_OSCURO),
        "fantasma": Boton(680, 560, 190, 48, "CAMBIAR", NARANJA, NARANJA_OSCURO),
    }


def nombre_tecla(tecla):
    """
    Devuelve el nombre visible de una tecla de pygame.
    """
    nombre = pygame.key.name(tecla).upper()
    if nombre == "SPACE":
        return "ESPACIO"
    if nombre == "RETURN":
        return "ENTER"
    if nombre.startswith("[") and nombre.endswith("]"):
        return nombre[1:-1]
    return nombre


def resumen_controles_juego():
    """
    Construye el texto de controles usando las teclas configuradas.
    """
    return (
        f"Mover: {nombre_tecla(CONTROLES['arriba']['tecla'])}/"
        f"{nombre_tecla(CONTROLES['abajo']['tecla'])}/"
        f"{nombre_tecla(CONTROLES['izquierda']['tecla'])}/"
        f"{nombre_tecla(CONTROLES['derecha']['tecla'])}  "
        f"Bomba: {nombre_tecla(CONTROLES['bomba']['tecla'])}  "
        f"Fantasma: {nombre_tecla(CONTROLES['fantasma']['tecla'])}"
    )


def dibujar_texto_con_sombra(superficie, texto, fuente, color, centro):
    sombra = fuente.render(texto, True, NEGRO)
    principal = fuente.render(texto, True, color)
    superficie.blit(sombra, sombra.get_rect(center=(centro[0] + 4, centro[1] + 4)))
    superficie.blit(principal, principal.get_rect(center=centro))


def dibujar_fondo(superficie):
    superficie.fill(color_hex(COLOR_FONDO))
    pygame.draw.circle(superficie, (20, 130, 200), (150, 120), 180)
    pygame.draw.circle(superficie, (15, 90, 150), (850, 680), 220)
    pygame.draw.polygon(superficie, NEGRO, [(0, 650), (150, 500), (300, 650)])
    pygame.draw.polygon(superficie, NEGRO, [(250, 650), (430, 470), (600, 650)])
    pygame.draw.polygon(superficie, NEGRO, [(600, 650), (780, 480), (1000, 650)])


def dibujar_menu():
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "LABERINTO", fuente_titulo, BLANCO, (ANCHO // 2, 120))
    dibujar_texto_con_sombra(pantalla, "DINAMICO", fuente_titulo, NARANJA, (ANCHO // 2, 190))
    boton_iniciar.dibujar(pantalla)
    boton_configuracion.dibujar(pantalla)
    boton_puntajes.dibujar(pantalla)
    boton_salir.dibujar(pantalla)


def dibujar_configuracion():
    """
    Dibuja la pantalla de configuracion de controles.
    """
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "CONFIGURACION", fuente_titulo, BLANCO, (ANCHO // 2, 95))

    titulo = fuente_subtitulo.render("Controles", True, NARANJA)
    pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 170)))

    for indice, accion in enumerate(CONTROLES):
        y = 210 + indice * 70
        rect_fila = pygame.Rect(130, y - 8, 760, 62)
        color_fila = GRIS_CLARO if accion == control_en_edicion else GRIS

        pygame.draw.rect(pantalla, NEGRO, rect_fila.inflate(8, 8), border_radius=12)
        pygame.draw.rect(pantalla, color_fila, rect_fila, border_radius=12)

        nombre = fuente_texto.render(CONTROLES[accion]["nombre"], True, BLANCO)
        pantalla.blit(nombre, (160, y + 8))

        tecla = fuente_boton.render(nombre_tecla(CONTROLES[accion]["tecla"]), True, AMARILLO)
        pantalla.blit(tecla, tecla.get_rect(center=(560, y + 23)))

        boton = botones_controles[accion]
        boton.color = VERDE if accion == control_en_edicion else NARANJA
        boton.color_hover = VERDE_OSCURO if accion == control_en_edicion else NARANJA_OSCURO
        boton.dibujar(pantalla)

    mensaje = fuente_texto_pequena.render(mensaje_configuracion, True, BLANCO)
    pantalla.blit(mensaje, mensaje.get_rect(center=(ANCHO // 2, 635)))
    boton_volver.dibujar(pantalla)


def dibujar_seleccion_tamano():
    """
    Dibuja la pantalla donde el usuario escoge 10x10, 20x20 o 30x30.
    """
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "SELECCIONA EL TAMANO", fuente_titulo, BLANCO, (ANCHO // 2, 145))

    texto = fuente_texto.render("Elige el tamano del laberinto antes de escoger el estilo.", True, BLANCO)
    pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, 235)))

    for indice, boton in enumerate(botones_tamano):
        boton.color = VERDE if TAMANOS_MAPA[indice] == tamano_mapa else NARANJA
        boton.color_hover = VERDE_OSCURO if TAMANOS_MAPA[indice] == tamano_mapa else NARANJA_OSCURO
        boton.dibujar(pantalla)

    boton_volver.dibujar(pantalla)


def dibujar_preview_mapa(superficie, rect, tipo):
    """
    Dibuja una mini representacion visual del estilo de mapa.
    """
    estilo = ESTILOS_MAPA[tipo]
    preview = pygame.Rect(rect.x + 28, rect.y + 94, rect.width - 56, 150)
    celda = min(preview.width // 6, preview.height // 5)
    patron_bloques = {(0, 1), (1, 4), (2, 2), (3, 5), (4, 0), (5, 3)}
    patron_muros = {(0, 0), (0, 5), (2, 0), (2, 5), (5, 0), (5, 5)}

    pygame.draw.rect(superficie, NEGRO, preview.inflate(8, 8), border_radius=8)

    for fila in range(5):
        for columna in range(6):
            x = preview.x + columna * celda
            y = preview.y + fila * celda
            celda_rect = pygame.Rect(x, y, celda - 2, celda - 2)

            color = estilo["piso"]
            if (fila, columna) in patron_muros:
                color = estilo["muro"]
            elif (fila, columna) in patron_bloques:
                color = estilo["bloque"]

            pygame.draw.rect(superficie, color, celda_rect, border_radius=4)
            pygame.draw.rect(superficie, estilo["borde"], celda_rect, 2, border_radius=4)


def dibujar_seleccion_mapa():
    """
    Dibuja la pantalla donde el usuario escoge el estilo visual del mapa.
    """
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "SELECCIONA EL MAPA", fuente_titulo, BLANCO, (ANCHO // 2, 105))

    texto_tamano = fuente_texto.render(f"Tamano seleccionado: {tamano_mapa} x {tamano_mapa}", True, BLANCO)
    pantalla.blit(texto_tamano, texto_tamano.get_rect(center=(ANCHO // 2, 178)))

    posicion_mouse = obtener_posicion_mouse_lienzo()
    for tarjeta in tarjetas_mapa:
        tipo = tarjeta["tipo"]
        rect = tarjeta["rect"]
        estilo = ESTILOS_MAPA[tipo]
        esta_encima = rect.collidepoint(posicion_mouse)
        color_fondo = estilo["muro"] if esta_encima else estilo["piso"]

        pygame.draw.rect(pantalla, NEGRO, rect.inflate(12, 12), border_radius=18)
        pygame.draw.rect(pantalla, color_fondo, rect, border_radius=18)
        pygame.draw.rect(pantalla, estilo["borde"], rect, 5, border_radius=18)

        nombre = fuente_boton.render(estilo["nombre"], True, BLANCO)
        sombra = fuente_boton.render(estilo["nombre"], True, NEGRO)
        pantalla.blit(sombra, sombra.get_rect(center=(rect.centerx + 3, rect.y + 50)))
        pantalla.blit(nombre, nombre.get_rect(center=(rect.centerx, rect.y + 47)))

        dibujar_preview_mapa(pantalla, rect, tipo)

        texto = fuente_texto_pequena.render("CLIC PARA JUGAR", True, BLANCO)
        pantalla.blit(texto, texto.get_rect(center=(rect.centerx, rect.bottom - 45)))

    boton_volver.dibujar(pantalla)


def dibujar_puntajes():
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "PUNTAJES", fuente_titulo, BLANCO, (ANCHO // 2, 110))

    x = 190
    for tamano in TAMANOS_MAPA:
        titulo = fuente_subtitulo.render(f"{tamano} x {tamano}", True, NARANJA)
        pantalla.blit(titulo, titulo.get_rect(center=(x, 230)))

        puntajes = obtener_puntajes(tamano)
        if not puntajes:
            puntajes = [0]

        for indice, puntaje in enumerate(puntajes[:10], start=1):
            texto = fuente_texto_pequena.render(f"{indice}. {puntaje}", True, BLANCO)
            pantalla.blit(texto, texto.get_rect(center=(x, 260 + indice * 32)))

        x += 310

    boton_volver.dibujar(pantalla)


def dibujar_perdiste():
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "PERDISTE", fuente_titulo, BLANCO, (ANCHO // 2, 95))

    texto = fuente_subtitulo.render("El mapa elimino la fila donde estabas.", True, NARANJA)
    pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, 170)))

    puntaje = 0
    if juego_actual is not None:
        puntaje = juego_actual.obtener_datos_interfaz()["puntaje"]
    texto_puntaje = fuente_subtitulo.render(f"Puntaje final: {puntaje}", True, BLANCO)
    pantalla.blit(texto_puntaje, texto_puntaje.get_rect(center=(ANCHO // 2, 225)))

    titulo_top = fuente_subtitulo.render("Top 20 historico", True, NARANJA)
    pantalla.blit(titulo_top, titulo_top.get_rect(center=(ANCHO // 2, 285)))

    puntajes = obtener_puntajes(tamano_mapa)[:20]
    columnas = [330, 670]
    for indice, valor in enumerate(puntajes, start=1):
        columna = 0 if indice <= 10 else 1
        fila = indice if indice <= 10 else indice - 10
        texto_top = fuente_texto_pequena.render(f"{indice:02d}. {valor}", True, BLANCO)
        pantalla.blit(texto_top, texto_top.get_rect(center=(columnas[columna], 310 + fila * 28)))

    boton_volver.dibujar(pantalla)


def iniciar_partida():
    global estado_pantalla
    global juego_actual
    global mapa_actual
    global jugador
    global mensaje_juego
    global pasos_fantasma
    global paso_fantasma_activo
    global bombas_disponibles
    global ultimo_desplazamiento

    if juego_actual is not None:
        juego_actual.detener_hilo()

    juego_actual = Juego(tamano_mapa, tipo_mapa)
    mapa_actual = juego_actual.mapa
    jugador = juego_actual.jugador
    pasos_fantasma = juego_actual.pasos_fantasma
    paso_fantasma_activo = False
    bombas_disponibles = juego_actual.bombas
    ultimo_desplazamiento = pygame.time.get_ticks()
    mensaje_juego = juego_actual.mensaje
    juego_actual.iniciar_hilo()
    estado_pantalla = "juego"


def manejar_movimiento(tecla):
    """
    Traduce la tecla configurada a una accion de la partida.
    """
    if juego_actual is None:
        return

    movimientos = {
        CONTROLES["arriba"]["tecla"]: (-1, 0),
        CONTROLES["abajo"]["tecla"]: (1, 0),
        CONTROLES["izquierda"]["tecla"]: (0, -1),
        CONTROLES["derecha"]["tecla"]: (0, 1),
    }

    if tecla in movimientos:
        cambio_fila, cambio_columna = movimientos[tecla]
        juego_actual.mover_jugador(cambio_fila, cambio_columna)
    elif tecla == CONTROLES["bomba"]["tecla"]:
        juego_actual.lanzar_bomba()
    elif tecla == CONTROLES["fantasma"]["tecla"]:
        juego_actual.activar_paso_fantasma()


def dibujar_juego():
    """
    Dibuja el estado actual de la partida usando una copia del objeto Juego.
    """
    if juego_actual is None:
        return

    datos = juego_actual.obtener_datos_interfaz()
    estilo = ESTILOS_MAPA.get(tipo_mapa, ESTILOS_MAPA["piedra"])
    pantalla.fill(estilo["borde"])

    tamano_celda = min(TAMANO_CELDA_GUI, 560 // tamano_mapa)
    ancho_mapa = tamano_celda * tamano_mapa
    inicio_x = (ANCHO - ancho_mapa) // 2
    inicio_y = 105

    titulo = fuente_subtitulo.render(
        f"{estilo['nombre']}  {tamano_mapa} x {tamano_mapa}",
        True,
        color_hex(COLOR_TEXTO),
    )
    pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 45)))

    puntaje = fuente_texto.render(f"Puntaje: {datos['puntaje']}", True, color_hex(COLOR_TEXTO))
    pantalla.blit(puntaje, (60, 50))

    poderes = fuente_texto.render(
        f"Bombas: {datos['bombas']}  Fantasma: {datos['pasos_fantasma']}",
        True,
        color_hex(COLOR_TEXTO),
    )
    pantalla.blit(poderes, (60, 82))



    for fila in range(tamano_mapa):
        for columna in range(tamano_mapa):
            x = inicio_x + columna * tamano_celda
            y = inicio_y + fila * tamano_celda
            rect = pygame.Rect(x, y, tamano_celda - 1, tamano_celda - 1)
            color = estilo["muro"] if datos["celdas"][fila][columna] == CELDA_OBSTACULO else estilo["piso"]
            pygame.draw.rect(pantalla, color, rect)
            pygame.draw.rect(pantalla, estilo["borde"], rect, 1)

    for (fila, columna), tipo in datos["elementos"].items():
        centro = (
            inicio_x + columna * tamano_celda + tamano_celda // 2,
            inicio_y + fila * tamano_celda + tamano_celda // 2,
        )
        radio = max(4, tamano_celda // 4)
        color = {
            TIPO_MONEDA_NORMAL: COLOR_MONEDA_NORMAL,
            TIPO_MONEDA_ESPECIAL: COLOR_MONEDA_ESPECIAL,
            TIPO_BOMBA: COLOR_BOMBA,
            TIPO_PASO_FANTASMA: COLOR_PASO_FANTASMA,
        }.get(tipo, COLOR_MONEDA_NORMAL)
        pygame.draw.circle(pantalla, color_hex(color), centro, radio)

    # Dibujar al jugador como rectangulo con flecha de direccion
    jugador_x = inicio_x + datos["jugador_columna"] * tamano_celda + 4
    jugador_y = inicio_y + datos["jugador_fila"] * tamano_celda + 4
    jugador_ancho = tamano_celda - 8
    jugador_alto = tamano_celda - 8
    jugador_rect = pygame.Rect(jugador_x, jugador_y, jugador_ancho, jugador_alto)
    pygame.draw.rect(pantalla, color_hex(COLOR_JUGADOR), jugador_rect, border_radius=6)

    # Flecha que indica la direccion actual del jugador
    centro_x = jugador_x + jugador_ancho // 2
    centro_y = jugador_y + jugador_alto // 2
    flecha = max(5, tamano_celda // 5)
    dir_fila = datos.get("direccion", (-1, 0))[0]
    dir_col = datos.get("direccion", (-1, 0))[1]

    if dir_fila == -1 and dir_col == 0:       # Arriba
        puntos = [
            (centro_x, centro_y - flecha),
            (centro_x - flecha, centro_y + flecha // 2),
            (centro_x + flecha, centro_y + flecha // 2),
        ]
    elif dir_fila == 1 and dir_col == 0:      # Abajo
        puntos = [
            (centro_x, centro_y + flecha),
            (centro_x - flecha, centro_y - flecha // 2),
            (centro_x + flecha, centro_y - flecha // 2),
        ]
    elif dir_fila == 0 and dir_col == -1:     # Izquierda
        puntos = [
            (centro_x - flecha, centro_y),
            (centro_x + flecha // 2, centro_y - flecha),
            (centro_x + flecha // 2, centro_y + flecha),
        ]
    else:                                      # Derecha
        puntos = [
            (centro_x + flecha, centro_y),
            (centro_x - flecha // 2, centro_y - flecha),
            (centro_x - flecha // 2, centro_y + flecha),
        ]

    pygame.draw.polygon(pantalla, BLANCO, puntos)

    texto_mensaje = fuente_texto_pequena.render(datos["mensaje"], True, BLANCO)
    pantalla.blit(texto_mensaje, texto_mensaje.get_rect(center=(ANCHO // 2, 720)))

    texto_controles = fuente_texto_pequena.render(resumen_controles_juego(), True, BLANCO)
    pantalla.blit(texto_controles, texto_controles.get_rect(center=(ANCHO // 2, 752)))

    dificultad = fuente_texto_pequena.render(
        f"Desplazamiento: {datos['intervalo']:.1f}s",
        True,
        color_hex(COLOR_TEXTO),
    )
    pantalla.blit(dificultad, dificultad.get_rect(center=(ANCHO // 2, 784)))


def cambiar_pantalla_completa():
    global ventana
    global pantalla_completa

    pantalla_completa = not pantalla_completa
    if pantalla_completa:
        ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)


def finalizar_partida(ir_a_perdiste=False):
    """
    Detiene la partida actual y guarda el puntaje una unica vez.
    """
    global estado_pantalla

    if juego_actual is not None:
        datos = juego_actual.obtener_datos_interfaz()
        if not juego_actual.puntaje_guardado and tamano_mapa is not None:
            guardar_puntaje(tamano_mapa, datos["puntaje"])
            juego_actual.puntaje_guardado = True
        juego_actual.detener_hilo()

    estado_pantalla = "perdiste" if ir_a_perdiste else "menu"


def asignar_control(accion, tecla):
    """
    Cambia la tecla de una accion si no esta repetida.
    """
    global mensaje_configuracion

    for otra_accion, datos in CONTROLES.items():
        if otra_accion != accion and datos["tecla"] == tecla:
            mensaje_configuracion = f"La tecla {nombre_tecla(tecla)} ya esta en uso."
            return False

    CONTROLES[accion]["tecla"] = tecla
    mensaje_configuracion = f"{CONTROLES[accion]['nombre']} ahora usa {nombre_tecla(tecla)}."
    return True


def manejar_edicion_control(tecla):
    """
    Atiende la tecla presionada cuando se esta editando un control.
    """
    global control_en_edicion
    global mensaje_configuracion

    if control_en_edicion is None:
        return False

    if tecla == pygame.K_ESCAPE:
        control_en_edicion = None
        mensaje_configuracion = "Cambio cancelado."
        return True

    if asignar_control(control_en_edicion, tecla):
        control_en_edicion = None

    return True


def manejar_evento(evento):
    global ventana
    global estado_pantalla
    global tamano_mapa
    global tipo_mapa
    global control_en_edicion
    global mensaje_configuracion

    if evento.type == pygame.VIDEORESIZE and not pantalla_completa:
        ventana = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
        return True

    if evento.type == pygame.KEYDOWN:
        if estado_pantalla == "configuracion" and manejar_edicion_control(evento.key):
            return True

        if evento.key == pygame.K_F11:
            cambiar_pantalla_completa()
        elif evento.key == pygame.K_ESCAPE:
            if estado_pantalla == "juego" and jugador is not None:
                finalizar_partida(False)
            elif estado_pantalla == "seleccion_mapa":
                estado_pantalla = "seleccion_tamano"
            else:
                estado_pantalla = "menu"
        elif estado_pantalla == "juego":
            manejar_movimiento(evento.key)

    if estado_pantalla == "menu":
        if boton_iniciar.fue_presionado(evento):
            tamano_mapa = None
            tipo_mapa = None
            estado_pantalla = "seleccion_tamano"
        elif boton_configuracion.fue_presionado(evento):
            estado_pantalla = "configuracion"
        elif boton_puntajes.fue_presionado(evento):
            estado_pantalla = "puntajes"
        elif boton_salir.fue_presionado(evento):
            return False

    elif estado_pantalla == "seleccion_tamano":
        for indice, boton in enumerate(botones_tamano):
            if boton.fue_presionado(evento):
                tamano_mapa = TAMANOS_MAPA[indice]
                tipo_mapa = None
                estado_pantalla = "seleccion_mapa"

        if boton_volver.fue_presionado(evento):
            estado_pantalla = "menu"

    elif estado_pantalla == "seleccion_mapa":
        if boton_volver.fue_presionado(evento):
            estado_pantalla = "seleccion_tamano"
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for tarjeta in tarjetas_mapa:
                if tarjeta["rect"].collidepoint(posicion_en_lienzo(evento.pos)):
                    tipo_mapa = tarjeta["tipo"]
                    iniciar_partida()
                    break

    elif estado_pantalla == "configuracion":
        for accion, boton in botones_controles.items():
            if boton.fue_presionado(evento):
                control_en_edicion = accion
                mensaje_configuracion = f"Presiona una tecla para: {CONTROLES[accion]['nombre']}."

        if boton_volver.fue_presionado(evento):
            control_en_edicion = None
            estado_pantalla = "menu"

    elif estado_pantalla == "puntajes":
        if boton_volver.fue_presionado(evento):
            estado_pantalla = "menu"

    elif estado_pantalla == "perdiste":
        if boton_volver.fue_presionado(evento):
            if juego_actual is not None:
                juego_actual.detener_hilo()
            estado_pantalla = "menu"

    return True


def iniciar_interfaz():
    global estado_pantalla
    global mensaje_juego
    global ultimo_desplazamiento

    inicializar_pygame()
    crear_botones()
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                if estado_pantalla == "juego":
                    finalizar_partida(False)
                ejecutando = False
            else:
                ejecutando = manejar_evento(evento)

        if estado_pantalla == "menu":
            dibujar_menu()
        elif estado_pantalla == "seleccion_tamano":
            dibujar_seleccion_tamano()
        elif estado_pantalla == "seleccion_mapa":
            dibujar_seleccion_mapa()
        elif estado_pantalla == "configuracion":
            dibujar_configuracion()
        elif estado_pantalla == "puntajes":
            dibujar_puntajes()
        elif estado_pantalla == "perdiste":
            dibujar_perdiste()
        elif estado_pantalla == "juego":
            if juego_actual is not None and juego_actual.obtener_datos_interfaz()["perdio"]:
                finalizar_partida(True)
                dibujar_perdiste()
            else:
                dibujar_juego()

        presentar_pantalla()
        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
