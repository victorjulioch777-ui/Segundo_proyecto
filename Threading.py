import threading

class Threats:
    def __init__(self):
        self.lock = threading.Lock()
        self._detener = threading.Event()
        self._hilo = None

    def iniciar_hilo(self, objetivo):
        """
        Inicia el hilo secundario ejecutando el callable `objetivo`.
        """
        if self._hilo is not None and self._hilo.is_alive():
            return

        self._detener.clear()
        self._hilo = threading.Thread(target=objetivo, daemon=True)
        self._hilo.start()

    def detener_hilo(self):
        """
        Detiene el hilo secundario.
        """
        self._detener.set()
        if self._hilo is not None and self._hilo.is_alive():
            self._hilo.join(timeout=1)
