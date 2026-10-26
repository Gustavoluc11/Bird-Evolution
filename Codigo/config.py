import json


class Config:
    """Configurações salvas em config.json (volumes e música ligada/desligada)."""

    def __init__(self, pasta_projeto):
        self.caminho = pasta_projeto / "config.json"
        self.musica = 0.30  # volume da música (0 a 1)
        self.efeitos = 0.75  # volume dos efeitos (0 a 1)
        self.musica_ligada = True
        self.carregar()

    @staticmethod
    def _volume(valor, padrao):
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            return max(0.0, min(1.0, float(valor)))
        return padrao

    def carregar(self):
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return  # sem arquivo (ou arquivo quebrado): fica com os valores padrão
        if not isinstance(dados, dict):
            return
        self.musica = self._volume(dados.get("musica"), self.musica)
        self.efeitos = self._volume(dados.get("efeitos"), self.efeitos)
        self.musica_ligada = bool(dados.get("musica_ligada", True))

    def salvar(self):
        dados = {
            "musica": round(self.musica, 2),
            "efeitos": round(self.efeitos, 2),
            "musica_ligada": self.musica_ligada,
        }
        try:
            self.caminho.write_text(json.dumps(dados, indent=2), encoding="utf-8")
        except OSError:
            pass  # pasta somente leitura? o jogo segue normal, só não salva
