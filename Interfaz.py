import pygame
import sys

pygame.init()

ANCHO = 1000
ALTO = 800

pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
pygame.display.set_caption("Laberinto Dinámico")

reloj = pygame.time.Clock()

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
NARANJA = (255, 145, 0)
NARANJA_OSCURO = (200, 90, 0)
AZUL = (20, 130, 200)
AZUL_OSCURO = (10, 60, 100)
VERDE = (70, 200, 90)
VERDE_OSCURO = (40, 150, 60)
GRIS = (45, 45, 45)
GRIS_CLARO = (90, 90, 90)
ROJO = (200, 60, 60)

# Fuentes
fuente_titulo = pygame.font.SysFont("arialblack", 64)
fuente_subtitulo = pygame.font.SysFont("arialblack", 34)
fuente_boton = pygame.font.SysFont("arialblack", 30)
fuente_texto = pygame.font.SysFont("arial", 26)
fuente_texto_pequena = pygame.font.SysFont("arial", 22)

estado_pantalla = "menu"
tamano_mapa = 10
pantalla_completa = False
sonido_activado = True


class Boton:
    """
    Representa un botón interactivo dentro de la interfaz.
    """

    def __init__(self, x, y, ancho, alto, texto, color, color_hover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover

    def dibujar(self, superficie):
        """
        Dibuja el botón y cambia su color cuando el mouse está encima.
        """
        posicion_mouse = pygame.mouse.get_pos()

        if self.rect.collidepoint(posicion_mouse):
            color_actual = self.color_hover
        else:
            color_actual = self.color

        pygame.draw.rect(superficie, NEGRO, self.rect.inflate(10, 10), border_radius=15)
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=15)

        texto_render = fuente_boton.render(self.texto, True, BLANCO)
        texto_rect = texto_render.get_rect(center=self.rect.center)

        superficie.blit(texto_render, texto_rect)

    def fue_presionado(self, evento):
        """
        Retorna True si el botón fue presionado con clic izquierdo.
        """
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(evento.pos)
        return False


def dibujar_texto_con_sombra(superficie, texto, fuente, color, centro):
    """
    Dibuja texto con sombra para dar estilo de videojuego.
    """
    sombra = fuente.render(texto, True, NEGRO)
    principal = fuente.render(texto, True, color)

    rect_sombra = sombra.get_rect(center=(centro[0] + 4, centro[1] + 4))
    rect_principal = principal.get_rect(center=centro)

    superficie.blit(sombra, rect_sombra)
    superficie.blit(principal, rect_principal)


def dibujar_panel(superficie, x, y, ancho, alto, titulo):
    """
    Dibuja un panel para separar secciones dentro de configuración.
    """
    rect_panel = pygame.Rect(x, y, ancho, alto)

    pygame.draw.rect(superficie, NEGRO, rect_panel.inflate(8, 8), border_radius=18)
    pygame.draw.rect(superficie, GRIS_CLARO, rect_panel, border_radius=18)

    texto_titulo = fuente_subtitulo.render(titulo, True, BLANCO)
    superficie.blit(texto_titulo, (x + 25, y + 15))


def dibujar_fondo(superficie):
    """
    Dibuja un fondo simple con estilo de menú.
    """
    superficie.fill(AZUL_OSCURO)

    # Figuras decorativas tipo videojuego
    pygame.draw.circle(superficie, AZUL, (150, 120), 180)
    pygame.draw.circle(superficie, (15, 90, 150), (850, 680), 220)

    # Siluetas inferiores
    pygame.draw.rect(superficie, NEGRO, (0, 650, ANCHO, 150))
    pygame.draw.polygon(superficie, NEGRO, [(0, 650), (150, 500), (300, 650)])
    pygame.draw.polygon(superficie, NEGRO, [(250, 650), (430, 470), (600, 650)])
    pygame.draw.polygon(superficie, NEGRO, [(600, 650), (780, 480), (1000, 650)])


def dibujar_menu():
    """
    Dibuja la pantalla principal del menú.
    """
    dibujar_fondo(pantalla)

    dibujar_texto_con_sombra(
        pantalla,
        "LABERINTO",
        fuente_titulo,
        BLANCO,
        (ANCHO // 2, 120)
    )

    dibujar_texto_con_sombra(
        pantalla,
        "DINÁMICO",
        fuente_titulo,
        NARANJA,
        (ANCHO // 2, 190)
    )

    boton_iniciar.dibujar(pantalla)
    boton_configuracion.dibujar(pantalla)
    boton_salir.dibujar(pantalla)


def dibujar_configuracion():
    """
    Dibuja la pantalla de configuración con controles y sonido.
    """
    dibujar_fondo(pantalla)

    dibujar_texto_con_sombra(
        pantalla,
        "CONFIGURACIÓN",
        fuente_titulo,
        BLANCO,
        (ANCHO // 2, 80)
    )

    boton_volver.dibujar(pantalla)


# Botones del menú principal
boton_iniciar = Boton(330, 300, 340, 70, "INICIAR PARTIDA", NARANJA, NARANJA_OSCURO)
boton_configuracion = Boton(330, 400, 340, 70, "CONFIGURACIÓN", VERDE, VERDE_OSCURO)
boton_salir = Boton(330, 500, 340, 70, "SALIR", GRIS, (20, 20, 20))

# Botones de configuración
boton_volver = Boton(380, 660, 240, 70, "VOLVER", GRIS, (100, 100, 100))


def iniciar_interfaz():
    """
    Ejecuta el ciclo principal de la interfaz grafica.
    """
    global pantalla
    global pantalla_completa
    global estado_pantalla
    global sonido_activado

    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    pantalla_completa = not pantalla_completa

                    if pantalla_completa:
                        pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)

                elif evento.key == pygame.K_ESCAPE:
                    if estado_pantalla != "menu":
                        estado_pantalla = "menu"

            if estado_pantalla == "menu":
                if boton_iniciar.fue_presionado(evento):
                    print(f"Iniciando partida con mapa {tamano_mapa}x{tamano_mapa}")
                    estado_pantalla = "juego"

                elif boton_configuracion.fue_presionado(evento):
                    estado_pantalla = "configuracion"

                elif boton_salir.fue_presionado(evento):
                    ejecutando = False

            elif estado_pantalla == "configuracion":
                if boton_volver.fue_presionado(evento):
                    estado_pantalla = "menu"

        if estado_pantalla == "menu":
            dibujar_menu()

        elif estado_pantalla == "configuracion":
            dibujar_configuracion()

        elif estado_pantalla == "juego":
            pantalla.fill((25, 25, 25))

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
