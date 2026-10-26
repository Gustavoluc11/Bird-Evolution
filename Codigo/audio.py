import pygame

from Codigo.passaro import NOMES

EXTENSOES = (".wav", ".ogg", ".mp3")


class Audio:
    """Cuida da música de fundo e dos efeitos sonoros.

    Se o computador não tiver placa de som (ou faltar algum arquivo),
    o jogo continua funcionando normalmente, só sem o som.
    """

    def __init__(self, pasta_sons, config):
        self.pasta = pasta_sons
        self.config = config
        self.ativo = False
        self.efeitos = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.ativo = True
        except pygame.error:
            print("Aviso: sem dispositivo de áudio, o jogo vai rodar sem som.")
            return

        # Um efeito para cada ave (Pintinho.wav, Frango.wav, ...) + a fusão
        for nome in list(NOMES.values()) + ["fundir"]:
            arquivo = self._achar(nome)
            if arquivo:
                som = pygame.mixer.Sound(str(arquivo))
                som.set_volume(config.efeitos)
                self.efeitos[nome] = som

    @property
    def musica_ligada(self):
        return self.config.musica_ligada

    def _achar(self, nome):
        for ext in EXTENSOES:
            caminho = self.pasta / f"{nome}{ext}"
            if caminho.exists():
                return caminho
        return None

    # ------------------------------------------------------------------
    # Música
    # ------------------------------------------------------------------
    def iniciar_musica(self):
        if not self.ativo:
            return
        arquivo = self._achar("musica")
        if not arquivo:
            return
        try:
            pygame.mixer.music.load(str(arquivo))
            pygame.mixer.music.set_volume(self.config.musica)
            pygame.mixer.music.play(-1)  # -1 = repete para sempre
            if not self.config.musica_ligada:
                pygame.mixer.music.pause()
        except pygame.error:
            print("Aviso: não consegui tocar a música.")

    def alternar_musica(self):
        """Liga/desliga a música (tecla M)."""
        self.config.musica_ligada = not self.config.musica_ligada
        self.config.salvar()
        if not self.ativo:
            return
        if self.config.musica_ligada:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    # ------------------------------------------------------------------
    # Volumes (0 a 1)
    # ------------------------------------------------------------------
    def definir_volume_musica(self, valor):
        self.config.musica = max(0.0, min(1.0, valor))
        if self.ativo:
            pygame.mixer.music.set_volume(self.config.musica)

    def definir_volume_efeitos(self, valor):
        self.config.efeitos = max(0.0, min(1.0, valor))
        for som in self.efeitos.values():
            som.set_volume(self.config.efeitos)

    # ------------------------------------------------------------------
    # Efeitos
    # ------------------------------------------------------------------
    def tocar(self, nome):
        som = self.efeitos.get(nome)
        if som:
            som.play()

    def tocar_passaro(self, nivel):
        self.tocar(NOMES[nivel])
