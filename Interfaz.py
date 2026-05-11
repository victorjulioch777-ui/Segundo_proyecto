import pygame

from Config import (
    CELDA_LIBRE,
    CELDA_OBSTACULO,
    COLOR_BOMBA,
    COLOR_CELDA_LIBRE,
    COLOR_FONDO,
    COLOR_JUGADOR,
    COLOR_MONEDA_ESPECIAL,
    COLOR_MONEDA_NORMAL,
    COLOR_OBSTACULO,
    COLOR_PASO_FANTASMA,
    COLOR_TEXTO,
    TAMANO_CELDA_GUI,
    TAMANOS_MAPA,
)
from Jugador import Jugador
from Mapa import Mapa, TIPO_MONEDA_ESPECIAL, TIPO_MONEDA_NORMAL
from Puntajes import guardar_puntaje, obtener_puntajes
from Utilidades import TIPO_BOMBA, TIPO_PASO_FANTASMA


ANCHO = 1000
ALTO = 800

pantalla = None
reloj = None
fuente_titulo = None
fuente_subtitulo = None
fuente_boton = None
fuente_texto = None
fuente_texto_pequena = None

estado_pantalla = "menu"
tamano_mapa = TAMANOS_MAPA[0]
pantalla_completa = False
sonido_activado = True
mapa_actual = None
jugador = None
mensaje_juego = ""
pasos_fantasma = 0
paso_fantasma_activo = False
bombas_disponibles = 0
ultimo_desplazamiento = 0


def color_hex(valor):
    return pygame.Color(valor)


BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
NARANJA = (255, 145, 0)
NARANJA_OSCURO = (200, 90, 0)
VERDE = (70, 200, 90)
VERDE_OSCURO = (40, 150, 60)
GRIS = (45, 45, 45)
GRIS_CLARO = (90, 90, 90)
ROJO = (200, 60, 60)


class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_hover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover

    def dibujar(self, superficie):
        posicion_mouse = pygame.mouse.get_pos()
        color_actual = self.color_hover if self.rect.collidepoint(posicion_mouse) else self.color

        pygame.draw.rect(superficie, NEGRO, self.rect.inflate(10, 10), border_radius=15)
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=15)

        texto_render = fuente_boton.render(self.texto, True, BLANCO)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        superficie.blit(texto_render, texto_rect)

    def fue_presionado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(evento.pos)
        return False


def inicializar_pygame():
    global pantalla
    global reloj
    global fuente_titulo
    global fuente_subtitulo
    global fuente_boton
    global fuente_texto
    global fuente_texto_pequena

    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
    pygame.display.set_caption("Laberinto Dinamico")
    reloj = pygame.time.Clock()

    fuente_titulo = pygame.font.SysFont("arialblack", 64)
    fuente_subtitulo = pygame.font.SysFont("arialblack", 34)
    fuente_boton = pygame.font.SysFont("arialblack", 28)
    fuente_texto = pygame.font.SysFont("arial", 26)
    fuente_texto_pequena = pygame.font.SysFont("arial", 22)


boton_iniciar = Boton(330, 300, 340, 70, "INICIAR PARTIDA", NARANJA, NARANJA_OSCURO)
boton_configuracion = Boton(330, 400, 340, 70, "CONFIGURACION", VERDE, VERDE_OSCURO)
boton_puntajes = Boton(330, 500, 340, 70, "PUNTAJES", GRIS_CLARO, GRIS)
boton_salir = Boton(330, 600, 340, 70, "SALIR", GRIS, (20, 20, 20))
boton_volver = Boton(380, 660, 240, 70, "VOLVER", GRIS, (100, 100, 100))
botones_tamano = [
    Boton(240 + indice * 190, 330, 150, 70, f"{tamano} x {tamano}", NARANJA, NARANJA_OSCURO)
    for indice, tamano in enumerate(TAMANOS_MAPA)
]


def dibujar_texto_con_sombra(superficie, texto, fuente, color, centro):
    sombra = fuente.render(texto, True, NEGRO)
    principal = fuente.render(texto, True, color)
    superficie.blit(sombra, sombra.get_rect(center=(centro[0] + 4, centro[1] + 4)))
    superficie.blit(principal, principal.get_rect(center=centro))


def dibujar_fondo(superficie):
    superficie.fill(color_hex(COLOR_FONDO))
    pygame.draw.circle(superficie, (20, 130, 200), (150, 120), 180)
    pygame.draw.circle(superficie, (15, 90, 150), (850, 680), 220)
    pygame.draw.rect(superficie, NEGRO, (0, 650, ANCHO, 150))
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
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "CONFIGURACION", fuente_titulo, BLANCO, (ANCHO // 2, 110))

    texto = fuente_subtitulo.render("Tamano del mapa", True, BLANCO)
    pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, 260)))

    for indice, boton in enumerate(botones_tamano):
        boton.color = VERDE if TAMANOS_MAPA[indice] == tamano_mapa else NARANJA
        boton.color_hover = VERDE_OSCURO if TAMANOS_MAPA[indice] == tamano_mapa else NARANJA_OSCURO
        boton.dibujar(pantalla)

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

        for indice, puntaje in enumerate(puntajes[:5], start=1):
            texto = fuente_texto.render(f"{indice}. {puntaje}", True, BLANCO)
            pantalla.blit(texto, texto.get_rect(center=(x, 270 + indice * 38)))

        x += 310

    boton_volver.dibujar(pantalla)


def dibujar_perdiste():
    dibujar_fondo(pantalla)
    dibujar_texto_con_sombra(pantalla, "PERDISTE", fuente_titulo, BLANCO, (ANCHO // 2, 170))

    texto = fuente_subtitulo.render("El mapa elimino la fila donde estabas.", True, NARANJA)
    pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, 300)))

    puntaje = 0 if jugador is None else jugador.puntaje
    texto_puntaje = fuente_subtitulo.render(f"Puntaje final: {puntaje}", True, BLANCO)
    pantalla.blit(texto_puntaje, texto_puntaje.get_rect(center=(ANCHO // 2, 370)))

    boton_volver.dibujar(pantalla)


def iniciar_partida():
    global estado_pantalla
    global mapa_actual
    global jugador
    global mensaje_juego
    global pasos_fantasma
    global paso_fantasma_activo
    global bombas_disponibles
    global ultimo_desplazamiento

    mapa_actual = Mapa(tamano_mapa)
    jugador = Jugador(tamano_mapa - 1, tamano_mapa // 2)
    pasos_fantasma = 0
    paso_fantasma_activo = False
    bombas_disponibles = 0
    ultimo_desplazamiento = pygame.time.get_ticks()
    mensaje_juego = "Flechas/WASD para moverte. Q usa fantasma. E usa bomba."
    estado_pantalla = "juego"


def manejar_movimiento(tecla):
    movimientos = {
        pygame.K_UP: (-1, 0),
        pygame.K_w: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_s: (1, 0),
        pygame.K_LEFT: (0, -1),
        pygame.K_a: (0, -1),
        pygame.K_RIGHT: (0, 1),
        pygame.K_d: (0, 1),
    }

    if tecla in movimientos:
        cambio_fila, cambio_columna = movimientos[tecla]
        mover_jugador(cambio_fila, cambio_columna)
    elif tecla == pygame.K_q:
        activar_paso_fantasma()
    elif tecla == pygame.K_e:
        lanzar_bomba()


def mover_jugador(cambio_fila, cambio_columna):
    global paso_fantasma_activo
    global mensaje_juego

    nueva_fila = jugador.fila + cambio_fila
    nueva_columna = jugador.columna + cambio_columna

    if jugador.mover(cambio_fila, cambio_columna, mapa_actual):
        aplicar_elemento()
        return

    if paso_fantasma_activo and 0 <= nueva_fila < mapa_actual.tamano and 0 <= nueva_columna < mapa_actual.tamano:
        jugador.fila = nueva_fila
        jugador.columna = nueva_columna
        paso_fantasma_activo = False
        mensaje_juego = "Atravesaste una pared con paso fantasma."
        aplicar_elemento()
    else:
        mensaje_juego = "No puedes moverte ahi."


def activar_paso_fantasma():
    global pasos_fantasma
    global paso_fantasma_activo
    global mensaje_juego

    if pasos_fantasma > 0:
        pasos_fantasma -= 1
        paso_fantasma_activo = True
        mensaje_juego = "Paso fantasma activo para tu siguiente movimiento."
    else:
        mensaje_juego = "No tienes paso fantasma disponible."


def lanzar_bomba():
    global bombas_disponibles
    global mensaje_juego

    if bombas_disponibles <= 0:
        mensaje_juego = "No tienes bombas disponibles."
        return

    bombas_disponibles -= 1
    celdas_destruidas = 0
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for cambio_fila, cambio_columna in direcciones:
        fila = jugador.fila + cambio_fila
        columna = jugador.columna + cambio_columna
        if 0 <= fila < mapa_actual.tamano and 0 <= columna < mapa_actual.tamano:
            if mapa_actual.celdas[fila][columna] == CELDA_OBSTACULO:
                mapa_actual.celdas[fila][columna] = CELDA_LIBRE
                celdas_destruidas += 1

    mensaje_juego = f"Bomba usada. Paredes destruidas: {celdas_destruidas}."


def aplicar_elemento():
    global mensaje_juego
    global pasos_fantasma
    global bombas_disponibles

    tipo = mapa_actual.recoger_elemento(jugador)
    if tipo == TIPO_MONEDA_NORMAL:
        mensaje_juego = "Moneda normal: +5 puntos."
    elif tipo == TIPO_MONEDA_ESPECIAL:
        mensaje_juego = "Moneda especial: +10 puntos."
    elif tipo == TIPO_BOMBA:
        bombas_disponibles += 1
        mensaje_juego = "Bomba recogida. Presiona E para usarla."
    elif tipo == TIPO_PASO_FANTASMA:
        pasos_fantasma += 1
        mensaje_juego = "Paso fantasma recogido. Presiona Q para activarlo."


def dibujar_juego():
    pantalla.fill((25, 25, 25))

    tamano_celda = min(TAMANO_CELDA_GUI, 560 // tamano_mapa)
    ancho_mapa = tamano_celda * tamano_mapa
    inicio_x = (ANCHO - ancho_mapa) // 2
    inicio_y = 105

    titulo = fuente_subtitulo.render(f"Mapa {tamano_mapa} x {tamano_mapa}", True, color_hex(COLOR_TEXTO))
    pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 45)))

    puntaje = fuente_texto.render(f"Puntaje: {jugador.puntaje}", True, color_hex(COLOR_TEXTO))
    pantalla.blit(puntaje, (60, 50))

    poderes = fuente_texto.render(f"Bombas: {bombas_disponibles}  Fantasma: {pasos_fantasma}", True, color_hex(COLOR_TEXTO))
    pantalla.blit(poderes, (60, 82))

    for fila in range(mapa_actual.tamano):
        for columna in range(mapa_actual.tamano):
            x = inicio_x + columna * tamano_celda
            y = inicio_y + fila * tamano_celda
            rect = pygame.Rect(x, y, tamano_celda - 1, tamano_celda - 1)
            color = COLOR_OBSTACULO if mapa_actual.celdas[fila][columna] == CELDA_OBSTACULO else COLOR_CELDA_LIBRE
            pygame.draw.rect(pantalla, color_hex(color), rect)

    for (fila, columna), tipo in mapa_actual.elementos.items():
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

    jugador_rect = pygame.Rect(
        inicio_x + jugador.columna * tamano_celda + 4,
        inicio_y + jugador.fila * tamano_celda + 4,
        tamano_celda - 8,
        tamano_celda - 8,
    )
    pygame.draw.rect(pantalla, color_hex(COLOR_JUGADOR), jugador_rect, border_radius=6)

    texto_mensaje = fuente_texto_pequena.render(mensaje_juego, True, BLANCO)
    pantalla.blit(texto_mensaje, texto_mensaje.get_rect(center=(ANCHO // 2, 720)))


def cambiar_pantalla_completa():
    global pantalla
    global pantalla_completa

    pantalla_completa = not pantalla_completa
    if pantalla_completa:
        pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)


def manejar_evento(evento):
    global estado_pantalla
    global tamano_mapa

    if evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_F11:
            cambiar_pantalla_completa()
        elif evento.key == pygame.K_ESCAPE:
            if estado_pantalla == "juego" and jugador is not None:
                guardar_puntaje(tamano_mapa, jugador.puntaje)
            estado_pantalla = "menu"
        elif estado_pantalla == "juego":
            manejar_movimiento(evento.key)

    if estado_pantalla == "menu":
        if boton_iniciar.fue_presionado(evento):
            iniciar_partida()
        elif boton_configuracion.fue_presionado(evento):
            estado_pantalla = "configuracion"
        elif boton_puntajes.fue_presionado(evento):
            estado_pantalla = "puntajes"
        elif boton_salir.fue_presionado(evento):
            return False

    elif estado_pantalla == "configuracion":
        for indice, boton in enumerate(botones_tamano):
            if boton.fue_presionado(evento):
                tamano_mapa = TAMANOS_MAPA[indice]
        if boton_volver.fue_presionado(evento):
            estado_pantalla = "menu"

    elif estado_pantalla == "puntajes":
        if boton_volver.fue_presionado(evento):
            estado_pantalla = "menu"

    elif estado_pantalla == "perdiste":
        if boton_volver.fue_presionado(evento):
            estado_pantalla = "menu"

    return True


def iniciar_interfaz():
    global estado_pantalla
    global mensaje_juego
    global ultimo_desplazamiento
    
    inicializar_pygame()
    ejecutando = True

    intervalo_desplazamiento = 2000

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                if estado_pantalla == "juego" and jugador is not None:
                    guardar_puntaje(tamano_mapa, jugador.puntaje)
                ejecutando = False
            else:
                ejecutando = manejar_evento(evento)

        if estado_pantalla == "menu":
            dibujar_menu()
        elif estado_pantalla == "configuracion":
            dibujar_configuracion()
        elif estado_pantalla == "puntajes":
            dibujar_puntajes()
        elif estado_pantalla == "perdiste":
            dibujar_perdiste()
        elif estado_pantalla == "juego":
            tiempo_actual = pygame.time.get_ticks()

            if tiempo_actual - ultimo_desplazamiento >= intervalo_desplazamiento:
                if jugador.fila == mapa_actual.tamano - 1:
                    guardar_puntaje(tamano_mapa, jugador.puntaje)
                    mensaje_juego = "Perdiste. El mapa elimino la fila donde estabas."
                    estado_pantalla = "perdiste"
                else:
                    mapa_actual.desplazar()
                    jugador.fila += 1

                ultimo_desplazamiento = tiempo_actual

            if estado_pantalla == "juego":
                dibujar_juego()


        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
