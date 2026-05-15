from Threading import Threats
import time
from Config import (
    DISMINUCION_TIEMPO,
    INTERVALO_APARICION_ELEMENTOS,
    INTERVALO_AUMENTO_DIFICULTAD,
    INTERVALO_DESPLAZAMIENTO_INICIAL,
    MINIMO_INTERVALO_DESPLAZAMIENTO,
    TIEMPO_VIDA_PODER,
    TIPO_BOMBA,
    TIPO_MONEDA_ESPECIAL,
    TIPO_MONEDA_NORMAL,
    TIPO_PASO_FANTASMA,
)
from Jugador import Jugador
from Mapa import Mapa

INTERVALO_DESPLAZAMIENTO_AMIGABLE = 2.0
MINIMO_BOMBAS_VISIBLES = 2
MINIMO_FANTASMAS_VISIBLES = 2

class Juego:
    """
    Controla la partida y toda la lógica central del juego.

    Esta clase administra el estado del jugador, el mapa y los elementos en pantalla.
    El desplazamiento automático del mapa, la aparición periódica de elementos y el
    aumento progresivo de la dificultad se ejecutan de manera concurrente mediante
    un hilo secundario para asi no bloquear la interfaz gráfica.
    """

    def __init__(self, tamano_mapa, tipo_mapa, porcentaje_obstaculos=0.60, dificultad="medio"):
        self.tamano_mapa = tamano_mapa
        self.tipo_mapa = tipo_mapa
        self.dificultad = dificultad
        self.mapa = Mapa(tamano_mapa, porcentaje_obstaculos)
        self.jugador = Jugador(fila=tamano_mapa - 1, columna=tamano_mapa // 2, mapa=self.mapa)
        self.bombas = 2
        self.pasos_fantasma = 2
        self.mensaje = f"Mapa {tipo_mapa}. Tienes 2 bombas y 2 pasos fantasma."
        self.perdio = False
        self.pausado = False
        self.puntaje_guardado = False

        self.intervalo_desplazamiento = max(
            INTERVALO_DESPLAZAMIENTO_INICIAL,
            INTERVALO_DESPLAZAMIENTO_AMIGABLE,
        )
        self.ultimo_desplazamiento = time.monotonic()
        self.ultimo_elemento = time.monotonic() - INTERVALO_APARICION_ELEMENTOS
        self.ultimo_aumento_dificultad = time.monotonic()
        self._hilo = Threats()



    def iniciar_hilo(self):
        """
        Arranca el hilo secundario con el bucle automatico de la partida.
        """
        self._hilo.iniciar_hilo(self.bucle_automatico)

    def detener_hilo(self):
        """
        Detiene el hilo secundario.
        """
        self._hilo.detener_hilo()

    def bucle_automatico(self):
        """
        Ciclo de vida secundario que corre de fondo durante toda la partida.
        Se encarga de evaluar constantemente si es necesario aplicar un desplazamiento
        del mapa, aumentar la dificultad del juego o gestionar los elementos temporales.
        """
        tiempo_anterior = time.monotonic()
        while not self._hilo._detener.is_set():
            tiempo_actual = time.monotonic()
            delta = tiempo_actual - tiempo_anterior
            tiempo_anterior = tiempo_actual
            with self._hilo.lock:
                if self.pausado:
                    self.ultimo_aumento_dificultad += delta
                    self.ultimo_elemento += delta
                    self.ultimo_desplazamiento += delta
                elif not self.perdio:
                    self._actualizar_dificultad(tiempo_actual)
                    self._actualizar_elementos(tiempo_actual)
                    self._actualizar_desplazamiento(tiempo_actual)

            time.sleep(0.05)

    def _actualizar_dificultad(self, tiempo_actual):
        """
        Acelera el juego progresivamente. Cada intervalo de tiempo configurado,
        reduce el tiempo de espera entre desplazamientos del mapa, asegurando
        que nunca sea menor al mínimo establecido.lock
        """
        tiempo_transcurrido = tiempo_actual - self.ultimo_aumento_dificultad
        if tiempo_transcurrido < INTERVALO_AUMENTO_DIFICULTAD:
            return

        self.intervalo_desplazamiento = max(
            MINIMO_INTERVALO_DESPLAZAMIENTO,
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
            self._asegurar_MinimoBombas(tiempo_actual, posicion_jugador)
            self._asegurar_MinimoFantasmas(tiempo_actual, posicion_jugador)
            self.mapa.agregar_elemento_aleatorio(tiempo_actual, posicion_jugador)
            self.ultimo_elemento = tiempo_actual

    def _asegurar_MinimoBombas(self, tiempo_actual, posicion_jugador):
        """
        Mantiene bombas y pasos fantasma apareciendo durante toda la partida.
        """
        while self.mapa.contar_elementos(TIPO_BOMBA) < MINIMO_BOMBAS_VISIBLES:
            if self.mapa.agregar_elemento(TIPO_BOMBA, tiempo_actual, posicion_jugador) is None:
                break
    
    
    def _asegurar_MinimoFantasmas(self, tiempo_actual, posicion_jugador):
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
        with self._hilo.lock:
            if self.perdio or self.pausado:
                return

            if self.jugador.mover(cambio_fila, cambio_columna):
                self.recoger_elemento_actual()
                return

            self.jugador.direccion = (cambio_fila, cambio_columna)
            self.mensaje = "No puedes moverte ahi."

    def activar_paso_fantasma(self):
        """
        Permite al jugador saltar un obstáculo en la dirección en la que mira,
        siempre que la celda posterior al obstáculo esté libre.
        """
        with self._hilo.lock:
            if self.perdio or self.pausado:
                return
            if self.pasos_fantasma <= 0:
                self.mensaje = "No tienes pasos fantasma disponibles."
                return

            dir_f, dir_c = self.jugador.direccion
            f_obs = self.jugador.fila + dir_f
            c_obs = self.jugador.columna + dir_c
            f_dest = f_obs + dir_f
            c_dest = c_obs + dir_c

            # 1. Verificar que al frente haya un obstáculo
            if not self.verificar_colision_frontal(f_obs=f_obs, c_obs=c_obs):
                return

            # 2. Verificar que la celda de destino esté libre
            self.verificar_destino_libre(f_dest=f_dest, c_dest=c_dest)
                
    def verificar_colision_frontal(self, f_obs, c_obs):
        if not self._esta_dentro(f_obs, c_obs): 
            self.mensaje = "No hay obstáculo dentro del mapa en esa dirección."
            return False
        
        if self.mapa.es_posicion_valida(f_obs, c_obs):
            self.mensaje = "Debes estas frente a un obstáculo para usar el paso fantasma."    
            return False
        
        return True
    def verificar_destino_libre(self, f_dest, c_dest):
        
            if self._esta_dentro(f_dest, c_dest) and self.mapa.es_posicion_valida(f_dest, c_dest):
                self.pasos_fantasma -= 1
                self.jugador.fila = f_dest
                self.jugador.columna = c_dest
                self.recoger_elemento_actual()
                self.mensaje = "¡Atravesaste el obstáculo con éxito!"
            else:
                self.mensaje = "No hay espacio libre después del obstáculo."

    def lanzar_bomba(self):
        """
        Destruye un obstaculo en la direccion actual del jugador.
        """
        with self._hilo.lock:
            if self.perdio or self.pausado:
                return
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
        with self._hilo.lock:
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
                "pausado": self.pausado,
                "intervalo": self.intervalo_desplazamiento,
                "direccion": self.jugador.direccion,
                "dificultad": self.dificultad,
            }

    def _esta_dentro(self, fila, columna):
        """
        Indica si una coordenada esta dentro de la matriz.
        """
        return 0 <= fila < self.mapa.tamano and 0 <= columna < self.mapa.tamano