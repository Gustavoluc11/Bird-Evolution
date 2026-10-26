import math
import random

import pygame

# ----------------------------------------------------------------------
# Dados de cada nível
# ----------------------------------------------------------------------
NIVEL_MAX = 6

NOMES = {
    1: "Pintinho",
    2: "Frango",
    3: "Ganso",
    4: "Tucano",
    5: "Avestruz",
    6: "Harpia",
}

ARQUIVOS = {
    1: "Pintinho-Lv1.png",
    2: "Frango-Lv2.png",
    3: "Ganso-Lv3.png",
    4: "Tucano-Lv4.png",
    5: "Avestruz-Lv5.png",
    6: "Harpia-Lv6.png",
}

# Altura (em pixels) de cada ave na tela: quanto maior o nível, maior a ave
ALTURAS = {1: 80, 2: 92, 3: 104, 4: 116, 5: 132, 6: 136}

# Moedas que cada ave gera a cada ciclo de renda
RENDA = {1: 1, 2: 3, 3: 8, 4: 20, 5: 50, 6: 120}

TEMPO_RENDA = 4.0  # segundos entre cada pagamento de moedas


class Passaro:
    imagens = {}  # cache: nível -> Surface

    # ------------------------------------------------------------------
    @classmethod
    def carregar_imagens(cls, pasta_passaros):
        """Carrega e redimensiona as imagens uma única vez."""
        if cls.imagens:
            return
        for nivel, arquivo in ARQUIVOS.items():
            img = pygame.image.load(str(pasta_passaros / arquivo)).convert_alpha()
            altura = ALTURAS[nivel]
            largura = round(img.get_width() * altura / img.get_height())
            cls.imagens[nivel] = pygame.transform.smoothscale(img, (largura, altura))

    # ------------------------------------------------------------------
    def __init__(self, nivel, x, y, pop=True):
        self.nivel = nivel
        self.x = float(x)  # centro da ave
        self.y = float(y)
        self.imagem = Passaro.imagens[nivel]
        self.largura, self.altura = self.imagem.get_size()

        self.arrastando = False
        self.offset = (0, 0)
        self.destaque = False  # fica True quando outra ave igual está por cima

        self.fase = random.uniform(0, math.tau)  # para a ave "respirar" diferente das outras
        self.tempo_pop = 0.35 if pop else 0.0  # animação de surgimento
        self.timer_renda = random.uniform(0, TEMPO_RENDA)

    # ------------------------------------------------------------------
    @property
    def rect(self):
        r = pygame.Rect(0, 0, self.largura, self.altura)
        r.center = (round(self.x), round(self.y))
        return r

    @property
    def hitbox(self):
        """Área de colisão um pouco menor que a imagem (fica mais justo)."""
        return self.rect.inflate(-self.largura * 0.3, -self.altura * 0.15)

    @property
    def nome(self):
        return NOMES[self.nivel]

    # ------------------------------------------------------------------
    def atualizar(self, dt):
        if self.tempo_pop > 0:
            self.tempo_pop = max(0.0, self.tempo_pop - dt)

    def atualizar_renda(self, dt):
        """Retorna as moedas geradas neste frame (0 na maioria das vezes)."""
        self.timer_renda += dt
        if self.timer_renda >= TEMPO_RENDA:
            self.timer_renda -= TEMPO_RENDA
            return RENDA[self.nivel]
        return 0

    # ------------------------------------------------------------------
    def desenhar(self, tela, tempo):
        escala = 1.0
        if self.tempo_pop > 0:
            # começa grande e "assenta" até o tamanho normal
            progresso = 1 - self.tempo_pop / 0.35
            escala = 1.0 + 0.45 * math.sin(progresso * math.pi) * (1 - progresso * 0.5)
        if self.arrastando:
            escala *= 1.12

        # Respiração: sobe e desce de leve
        balanco = 0 if self.arrastando else math.sin(tempo * 3 + self.fase) * 2.5
        levantar = -12 if self.arrastando else 0

        # Sombra no chão
        sombra_w = int(self.largura * 0.7 * (0.85 if self.arrastando else 1))
        sombra = pygame.Surface((sombra_w, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 70), sombra.get_rect())
        tela.blit(sombra, sombra.get_rect(center=(self.x, self.y + self.altura / 2 - 4)))

        # Brilho quando dá para fundir
        if self.destaque:
            raio = int(max(self.largura, self.altura) * 0.62)
            brilho = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            pulso = 90 + int(50 * math.sin(tempo * 10))
            pygame.draw.circle(brilho, (255, 240, 120, pulso), (raio, raio), raio)
            tela.blit(brilho, brilho.get_rect(center=(self.x, self.y + levantar)))

        img = self.imagem
        if abs(escala - 1.0) > 0.01:
            img = pygame.transform.smoothscale(
                img, (int(self.largura * escala), int(self.altura * escala))
            )
        tela.blit(img, img.get_rect(center=(self.x, self.y + balanco + levantar)))
