import threading
import time

from Config import (
    DISMINUCION_TIEMPO,
    INTERVALO_APARICION_ELEMENTOS,
    INTERVALO_AUMENTO_DIFICULTAD,
    INTERVALO_DESPLAZAMIENTO_INICIAL,
    TIEMPO_VIDA_PODER,
    TIPO_BOMBA,
    TIPO_MONEDA_ESPECIAL,
    TIPO_MONEDA_NORMAL,
    TIPO_PASO_FANTASMA,
)
from Jugador import Jugador
from Mapa import Mapa


INTERVALO_DESPLAZAMIENTO_AMIGABLE = 5.0
MINIMO_BOMBAS_VISIBLES = 2
MINIMO_FANTASMAS_VISIBLES = 2


class Juego:
    """
    Controla la partida y la logica que no pertenece a la interfaz.

    El desplazamiento automatico del mapa, la aparicion de elementos y el
    aumento de dificultad se ejecutan desde un hilo secundario.
    """

    def __init__(self, tamano_mapa, tipo_mapa):
        self.tamano_mapa = tamano_mapa
        self.tipo_mapa = tipo_mapa
        self.mapa = Mapa(tamano_mapa)
        self.jugador = Jugador(tamano_mapa - 1, tamano_mapa // 2)
        self.bombas = 5
        self.pasos_fantasma = 5
        self.paso_fantasma_activo = False
        self.mensaje = f"Mapa {tipo_mapa}. Tienes 5 bombas y 5 pasos fantasma."
        self.perdio = False
        self.puntaje_guardado = False

        self.intervalo_desplazamiento = max(
            INTERVALO_DESPLAZAMIENTO_INICIAL,
            INTERVALO_DESPLAZAMIENTO_AMIGABLE,
        )
        self.ultimo_desplazamiento = time.monotonic()
        self.ultimo_elemento = time.monotonic() - INTERVALO_APARICION_ELEMENTOS
        self.ultimo_aumento_dificultad = time.monotonic()

        self.lock = threading.Lock()
        self._detener = threading.Event()
        self._hilo = None

    def iniciar_hilo(self):
        """
        Inicia el hilo secundario del desplazamiento automatico.
        """
        if self._hilo is not None and self._hilo.is_alive():
            return

        self._hilo = threading.Thread(target=self._bucle_automatico, daemon=True)
        self._hilo.start()

    def detener_hilo(self):
        """
        Detiene el hilo secundario.
        """
        self._detener.set()
        if self._hilo is not None and self._hilo.is_alive():
            self._hilo.join(timeout=1)

    def _bucle_automatico(self):
        """
        Ejecuta desplazamiento, dificultad y elementos temporales.
        """
        while not self._detener.is_set():
            tiempo_actual = time.monotonic()
            with self.lock:
                if not self.perdio:
                    self._actualizar_dificultad(tiempo_actual)
                    self._actualizar_elementos(tiempo_actual)
                    self._actualizar_desplazamiento(tiempo_actual)

            time.sleep(0.05)

    def _actualizar_dificultad(self, tiempo_actual):
        """
        Acelera el desplazamiento cada intervalo definido.
        """
        tiempo_transcurrido = tiempo_actual - self.ultimo_aumento_dificultad
        if tiempo_transcurrido < INTERVALO_AUMENTO_DIFICULTAD:
            return

        self.intervalo_desplazamiento = max(
            1.8,
            self.intervalo_desplazamiento - DISMINUCION_TIEMPO,
        )
        self.ultimo_aumento_dificultad = tiempo_actual

    def _actualizar_elementos(self, tiempo_actual):
        """
        Agrega elementos cada 5 segundos y elimina los que vencen a los 10.
        """
        self.mapa.eliminar_elementos_expirados(tiempo_actual, TIEMPO_VIDA_PODER)

        if tiempo_actual - self.ultimo_elemento >= INTERVALO_APARICION_ELEMENTOS:
            posicion_jugador = (self.jugador.fila, self.jugador.columna)
            self._asegurar_recursos(tiempo_actual, posicion_jugador)
            self.mapa.agregar_elemento_aleatorio(tiempo_actual, posicion_jugador)
            self.ultimo_elemento = tiempo_actual

    def _asegurar_recursos(self, tiempo_actual, posicion_jugador):
        """
        Mantiene bombas y pasos fantasma apareciendo durante toda la partida.
        """
        while self.mapa.contar_elementos(TIPO_BOMBA) < MINIMO_BOMBAS_VISIBLES:
            if self.mapa.agregar_elemento(TIPO_BOMBA, tiempo_actual, posicion_jugador) is None:
                break

        while self.mapa.contar_elementos(TIPO_PASO_FANTASMA) < MINIMO_FANTASMAS_VISIBLES:
            if self.mapa.agregar_elemento(TIPO_PASO_FANTASMA, tiempo_actual, posicion_jugador) is None:
                break

    def _actualizar_desplazamiento(self, tiempo_actual):
        """
        Desplaza el mapa cuando se cumple el intervalo actual.
        """
        if tiempo_actual - self.ultimo_desplazamiento < self.intervalo_desplazamiento:
            return

        if self.jugador.fila == self.mapa.tamano - 1:
            self.perdio = True
            self.mensaje = "Perdiste. El mapa elimino la fila donde estabas."
        else:
            self.mapa.desplazar()
            self.jugador.fila += 1
            self.recoger_elemento_actual()

        self.ultimo_desplazamiento = tiempo_actual

    def mover_jugador(self, cambio_fila, cambio_columna):
        """
        Mueve al jugador o aplica paso fantasma si esta activo.
        """
        with self.lock:
            if self.perdio:
                return

            nueva_fila = self.jugador.fila + cambio_fila
            nueva_columna = self.jugador.columna + cambio_columna

            if self.jugador.mover(cambio_fila, cambio_columna, self.mapa):
                self.recoger_elemento_actual()
                return

            self.jugador.direccion = (cambio_fila, cambio_columna)
            if self.paso_fantasma_activo and self._esta_dentro(nueva_fila, nueva_columna):
                self.jugador.fila = nueva_fila
                self.jugador.columna = nueva_columna
                self.paso_fantasma_activo = False
                self.mensaje = "Atravesaste un obstaculo con paso fantasma."
                self.recoger_elemento_actual()
            else:
                self.mensaje = "No puedes moverte ahi."

    def activar_paso_fantasma(self):
        """
        Activa un paso fantasma para atravesar un unico obstaculo.
        """
        with self.lock:
            if self.pasos_fantasma <= 0:
                self.mensaje = "No tienes pasos fantasma disponibles."
                return

            self.pasos_fantasma -= 1
            self.paso_fantasma_activo = True
            self.mensaje = "Paso fantasma activo para el siguiente obstaculo."

    def lanzar_bomba(self):
        """
        Destruye un obstaculo en la direccion actual del jugador.
        """
        with self.lock:
            if self.bombas <= 0:
                self.mensaje = "No tienes bombas disponibles."
                return

            self.bombas -= 1
            destruido = self.mapa.destruir_obstaculo(
                self.jugador.fila,
                self.jugador.columna,
                self.jugador.direccion,
            )

            if destruido:
                self.mensaje = "Bomba usada. Obstaculo destruido."
            else:
                self.mensaje = "Bomba usada, pero no habia obstaculo en esa direccion."

    def recoger_elemento_actual(self):
        """
        Aplica el elemento que se encuentre bajo el jugador.
        """
        tipo = self.mapa.recoger_elemento(self.jugador)
        if tipo == TIPO_MONEDA_NORMAL:
            self.mensaje = "Moneda normal: +5 puntos."
        elif tipo == TIPO_MONEDA_ESPECIAL:
            self.mensaje = "Moneda especial: +10 puntos."
        elif tipo == TIPO_BOMBA:
            self.bombas += 1
            self.mensaje = "Bomba recogida. Presiona 1 para usarla."
        elif tipo == TIPO_PASO_FANTASMA:
            self.pasos_fantasma += 1
            self.mensaje = "Paso fantasma recogido. Presiona 2 para activarlo."

    def obtener_datos_interfaz(self):
        """
        Retorna una copia simple del estado que la interfaz necesita dibujar.
        """
        with self.lock:
            return {
                "celdas": [fila[:] for fila in self.mapa.celdas],
                "elementos": self.mapa.obtener_elementos_visibles(),
                "jugador_fila": self.jugador.fila,
                "jugador_columna": self.jugador.columna,
                "puntaje": self.jugador.puntaje,
                "bombas": self.bombas,
                "pasos_fantasma": self.pasos_fantasma,
                "mensaje": self.mensaje,
                "perdio": self.perdio,
                "intervalo": self.intervalo_desplazamiento,
                "direccion": self.jugador.direccion,
            }

    def _esta_dentro(self, fila, columna):
        """
        Indica si una coordenada esta dentro de la matriz.
        """
        return 0 <= fila < self.mapa.tamano and 0 <= columna < self.mapa.tamano
