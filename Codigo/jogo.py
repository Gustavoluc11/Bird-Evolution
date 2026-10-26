import math
import random

import pygame

from Codigo import cursor
from Codigo.audio import Audio
from Codigo.config import Config
from Codigo.passaro import NIVEL_MAX, NOMES, Passaro

# ----------------------------------------------------------------------
# Configurações
# ----------------------------------------------------------------------
LARGURA = 960
ALTURA = 720

MAX_AVES = 14  # limite de aves no campo ao mesmo tempo
MOEDAS_INICIAIS = 30
CUSTO_BASE = 10  # preço do primeiro Pintinho
CRESCIMENTO_CUSTO = 1.09  # o preço sobe 9% a cada compra

# Área onde as aves podem ficar (esquerda, topo, largura, altura)
AREA = pygame.Rect(30, 100, LARGURA - 60, 540)
BOTAO = pygame.Rect(LARGURA // 2 - 195, 652, 390, 56)

COR_MOEDA = (255, 213, 74)
COR_TEXTO = (255, 255, 255)
COR_SOMBRA = (30, 40, 30)


class Jogo:
    def __init__(self, tela, pasta_projeto, audio=None):
        self.tela = tela
        pasta_av = pasta_projeto / "AV"

        # Fundo (já está no tamanho da janela)
        fundo = pygame.image.load(str(pasta_av / "Fundos" / "Fundo.jpg")).convert()
        if fundo.get_size() != (LARGURA, ALTURA):
            fundo = pygame.transform.smoothscale(fundo, (LARGURA, ALTURA))
        self.fundo = fundo

        Passaro.carregar_imagens(pasta_av / "Passaros")

        # Sons: normalmente vem pronto do main (compartilhado com o menu)
        if audio is None:
            audio = Audio(pasta_av / "Sons", Config(pasta_projeto))
            audio.iniciar_musica()
        self.audio = audio

        self.fonte_p = self._fonte(20)
        self.fonte_m = self._fonte(28)
        self.fonte_g = self._fonte(54)

        self.miniaturas, self.silhuetas = self._criar_miniaturas()

        self.aves = []
        self.arrastando = None
        self.moedas = MOEDAS_INICIAIS
        self.compras = 0
        self.descobertos = {1}
        self.tempo = 0.0
        self.particulas = []
        self.textos = []

        # Começa com 2 pintinhos para o jogador já poder fundir
        self._criar_ave(1)
        self._criar_ave(1)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    @staticmethod
    def _fonte(tamanho):
        return pygame.font.SysFont("segoeui,arial,dejavusans", tamanho, bold=True)

    def _criar_miniaturas(self):
        """Imagens pequenas para a barra de evolução (normal e escurecida)."""
        normais, escuras = {}, {}
        for nivel, img in Passaro.imagens.items():
            altura = 46
            largura = round(img.get_width() * altura / img.get_height())
            mini = pygame.transform.smoothscale(img, (largura, altura))
            sil = mini.copy()
            sil.fill((55, 60, 55, 255), special_flags=pygame.BLEND_RGBA_MULT)
            normais[nivel], escuras[nivel] = mini, sil
        return normais, escuras

    def _texto(self, fonte, texto, cor, pos, esquerda=False, alfa=255):
        """Desenha texto com sombra para ler bem em cima do cenário."""
        sombra = fonte.render(texto, True, COR_SOMBRA)
        principal = fonte.render(texto, True, cor)
        if alfa < 255:
            sombra.set_alpha(alfa)
            principal.set_alpha(alfa)
        rect = principal.get_rect()
        if esquerda:
            rect.midleft = pos
        else:
            rect.center = pos
        self.tela.blit(sombra, rect.move(2, 2))
        self.tela.blit(principal, rect)

    @property
    def custo(self):
        return round(CUSTO_BASE * CRESCIMENTO_CUSTO ** self.compras)

    def _limitar(self, ave):
        """Mantém a ave dentro da área de jogo."""
        meia_l, meia_a = ave.largura / 2, ave.altura / 2
        ave.x = max(AREA.left + meia_l, min(AREA.right - meia_l, ave.x))
        ave.y = max(AREA.top + meia_a, min(AREA.bottom - meia_a, ave.y))

    def _ordem_desenho(self):
        """Quem está mais embaixo na tela aparece na frente; a ave arrastada fica por cima."""
        return sorted(self.aves, key=lambda a: (a.arrastando, a.y))

    # ------------------------------------------------------------------
    # Criar / comprar aves
    # ------------------------------------------------------------------
    def _criar_ave(self, nivel, x=None, y=None):
        ave = Passaro(nivel, 0, 0)
        if x is None:
            for _ in range(40):  # tenta achar um lugar vazio
                ave.x = random.uniform(AREA.left + 60, AREA.right - 60)
                ave.y = random.uniform(AREA.top + 70, AREA.bottom - 70)
                if not any(ave.hitbox.colliderect(o.hitbox) for o in self.aves):
                    break
        else:
            ave.x, ave.y = x, y
        self._limitar(ave)
        self.aves.append(ave)
        return ave

    def comprar(self):
        # Sem aves e sem dinheiro? Ganha um pintinho de graça para não travar o jogo.
        if not self.aves and self.moedas < self.custo:
            self._criar_ave(1)
            return
        if len(self.aves) >= MAX_AVES:
            self._aviso("Campo cheio! Una algumas aves")
            return
        if self.moedas < self.custo:
            self._aviso("Moedas insuficientes")
            return
        self.moedas -= self.custo
        self.compras += 1
        ave = self._criar_ave(1)
        self._explosao(ave.x, ave.y, 8)
        self.audio.tocar_passaro(1)

    # ------------------------------------------------------------------
    # Mouse
    # ------------------------------------------------------------------
    def evento(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if BOTAO.collidepoint(ev.pos):
                self.comprar()
                return
            for ave in reversed(self._ordem_desenho()):  # a de cima primeiro
                if ave.rect.collidepoint(ev.pos):
                    ave.arrastando = True
                    ave.offset = (ave.x - ev.pos[0], ave.y - ev.pos[1])
                    self.arrastando = ave
                    break

        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            if self.arrastando:
                self._soltar()

        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
            self.comprar()


    def cancelar_arrasto(self):
        """Solta a ave sem fundir (usado ao voltar para o menu no meio de um arrasto)."""
        if self.arrastando:
            self.arrastando.arrastando = False
            self.arrastando = None
        for a in self.aves:
            a.destaque = False

    def _achar_alvo(self, ave):
        """Outra ave do mesmo nível que está encostando na ave arrastada."""
        if ave.nivel >= NIVEL_MAX:
            return None
        melhor, menor_dist = None, 1e9
        for outra in self.aves:
            if outra is ave or outra.nivel != ave.nivel:
                continue
            if ave.hitbox.colliderect(outra.hitbox):
                dist = math.hypot(ave.x - outra.x, ave.y - outra.y)
                if dist < menor_dist:
                    melhor, menor_dist = outra, dist
        return melhor

    def _soltar(self):
        ave = self.arrastando
        self.arrastando = None
        ave.arrastando = False
        alvo = self._achar_alvo(ave)
        for a in self.aves:
            a.destaque = False
        if alvo:
            self._fundir(ave, alvo)

    def _fundir(self, a, b):
        novo_nivel = a.nivel + 1
        x, y = b.x, b.y
        self.aves.remove(a)
        self.aves.remove(b)
        nova = self._criar_ave(novo_nivel, x, y)
        self._explosao(nova.x, nova.y, 22)
        self.audio.tocar("fundir")
        self.audio.tocar_passaro(novo_nivel)

        if novo_nivel not in self.descobertos:
            self.descobertos.add(novo_nivel)
            self.textos.append(
                dict(texto=f"Nova ave: {NOMES[novo_nivel]}!", x=LARGURA / 2, y=230,
                     vida=2.4, total=2.4, cor=COR_MOEDA, fonte=self.fonte_g, vy=-18)
            )
        else:
            self.textos.append(
                dict(texto=NOMES[novo_nivel], x=nova.x, y=nova.y - nova.altura / 2 - 6,
                     vida=1.1, total=1.1, cor=COR_TEXTO, fonte=self.fonte_m, vy=-40)
            )

    # ------------------------------------------------------------------
    # Efeitos
    # ------------------------------------------------------------------
    def _explosao(self, x, y, quantidade):
        cores = [(255, 240, 150), (255, 255, 255), (255, 200, 90), (190, 255, 160)]
        for _ in range(quantidade):
            ang = random.uniform(0, math.tau)
            vel = random.uniform(80, 240)
            self.particulas.append(
                dict(x=x, y=y, vx=math.cos(ang) * vel, vy=math.sin(ang) * vel - 60,
                     vida=0.7, total=0.7, raio=random.uniform(3, 7), cor=random.choice(cores))
            )

    def _aviso(self, msg):
        self.textos.append(
            dict(texto=msg, x=LARGURA / 2, y=620, vida=1.3, total=1.3,
                 cor=(255, 140, 120), fonte=self.fonte_m, vy=-25)
        )

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def atualizar(self, dt):
        self.tempo += dt
        mouse = pygame.mouse.get_pos()

        # Arrastar
        if self.arrastando:
            self.arrastando.x = mouse[0] + self.arrastando.offset[0]
            self.arrastando.y = mouse[1] + self.arrastando.offset[1]
            self._limitar(self.arrastando)

        # Brilho nas aves que podem se fundir
        for a in self.aves:
            a.destaque = False
        if self.arrastando:
            alvo = self._achar_alvo(self.arrastando)
            if alvo:
                self.arrastando.destaque = True
                alvo.destaque = True

        # Aves se empurram de leve para não ficarem empilhadas
        for i, a in enumerate(self.aves):
            for b in self.aves[i + 1:]:
                if a.arrastando or b.arrastando:
                    continue
                dx, dy = b.x - a.x, b.y - a.y
                dist = math.hypot(dx, dy)
                minimo = (a.largura + b.largura) * 0.40
                if dist < minimo:
                    if dist < 0.01:
                        dx, dy, dist = random.uniform(-1, 1), random.uniform(-1, 1), 1
                    empurrao = (minimo - dist) * 6 * dt
                    nx, ny = dx / dist, dy / dist
                    a.x -= nx * empurrao
                    a.y -= ny * empurrao
                    b.x += nx * empurrao
                    b.y += ny * empurrao
        for a in self.aves:
            if not a.arrastando:
                self._limitar(a)

        # Animações e renda
        for a in self.aves:
            a.atualizar(dt)
            ganho = a.atualizar_renda(dt)
            if ganho:
                self.moedas += ganho
                self.textos.append(
                    dict(texto=f"+{ganho}", x=a.x, y=a.y - a.altura / 2, vida=0.9, total=0.9,
                         cor=COR_MOEDA, fonte=self.fonte_p, vy=-45)
                )

        # Partículas e textos flutuantes
        for p in self.particulas:
            p["vida"] -= dt
            p["vy"] += 500 * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
        self.particulas = [p for p in self.particulas if p["vida"] > 0]

        for t in self.textos:
            t["vida"] -= dt
            t["y"] += t["vy"] * dt
        self.textos = [t for t in self.textos if t["vida"] > 0]

        # Cursor vira "mãozinha" sobre aves e botão
        cursor.definir(BOTAO.collidepoint(mouse) or any(a.rect.collidepoint(mouse) for a in self.aves))

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def desenhar(self):
        tela = self.tela
        tela.blit(self.fundo, (0, 0))

        for ave in self._ordem_desenho():
            ave.desenhar(tela, self.tempo)

        for p in self.particulas:
            frac = p["vida"] / p["total"]
            pygame.draw.circle(tela, p["cor"], (int(p["x"]), int(p["y"])), max(1, int(p["raio"] * frac)))

        self._desenhar_hud()
        self._desenhar_botao()
        self._texto(self.fonte_p, "ESC menu   F11 tela cheia   M música", COR_TEXTO,
                    (16, ALTURA - 20), esquerda=True, alfa=200)

        for t in self.textos:
            alfa = int(255 * min(1.0, t["vida"] / (t["total"] * 0.5)))
            self._texto(t["fonte"], t["texto"], t["cor"], (t["x"], t["y"]), alfa=alfa)

    def _painel(self, rect):
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 40, 25, 150), surf.get_rect(), border_radius=14)
        pygame.draw.rect(surf, (255, 255, 255, 60), surf.get_rect(), width=2, border_radius=14)
        self.tela.blit(surf, rect.topleft)

    def _desenhar_moeda(self, centro, raio=12):
        pygame.draw.circle(self.tela, (200, 140, 20), centro, raio)
        pygame.draw.circle(self.tela, COR_MOEDA, centro, raio - 2)
        pygame.draw.circle(self.tela, (255, 240, 170), (centro[0] - 3, centro[1] - 3), raio // 4)

    def _desenhar_hud(self):
        # Moedas (canto esquerdo)
        painel = pygame.Rect(16, 14, 190, 52)
        self._painel(painel)
        self._desenhar_moeda((painel.left + 28, painel.centery), 14)
        self._texto(self.fonte_m, f"{self.moedas:,}".replace(",", "."), COR_TEXTO,
                    (painel.left + 52, painel.centery), esquerda=True)

        # Barra de evolução (centro)
        largura_total = 6 * 54 + 5 * 22 + 28
        barra = pygame.Rect((LARGURA - largura_total) // 2, 10, largura_total, 64)
        self._painel(barra)
        x = barra.left + 14
        for nivel in range(1, NIVEL_MAX + 1):
            img = self.miniaturas[nivel] if nivel in self.descobertos else self.silhuetas[nivel]
            self.tela.blit(img, img.get_rect(midleft=(x, barra.centery)))
            x += 54
            if nivel < NIVEL_MAX:
                cx, cy = x + 11, barra.centery
                pygame.draw.polygon(self.tela, (255, 255, 255),
                                    [(cx - 4, cy - 7), (cx + 5, cy), (cx - 4, cy + 7)])
                x += 22

        # Contador de aves (canto direito)
        painel2 = pygame.Rect(LARGURA - 16 - 150, 14, 150, 52)
        self._painel(painel2)
        cor = (255, 150, 130) if len(self.aves) >= MAX_AVES else COR_TEXTO
        self._texto(self.fonte_m, f"Aves {len(self.aves)}/{MAX_AVES}", cor, painel2.center)

    def _desenhar_botao(self):
        pode = self.moedas >= self.custo and len(self.aves) < MAX_AVES
        mouse_sobre = BOTAO.collidepoint(pygame.mouse.get_pos())

        if pode:
            cor = (110, 205, 90) if not mouse_sobre else (135, 225, 110)
            borda = (60, 130, 50)
        else:
            cor = (140, 150, 140)
            borda = (90, 100, 90)

        rect = BOTAO.copy()
        if pode and mouse_sobre:
            rect.y -= 2
        pygame.draw.rect(self.tela, borda, rect.move(0, 5), border_radius=16)
        pygame.draw.rect(self.tela, cor, rect, border_radius=16)
        pygame.draw.rect(self.tela, (255, 255, 255), rect, width=2, border_radius=16)

        if len(self.aves) >= MAX_AVES:
            self._texto(self.fonte_m, "Campo cheio!", COR_TEXTO, rect.center)
        else:
            self._texto(self.fonte_m, "Comprar Pintinho", COR_TEXTO,
                        (rect.left + 28, rect.centery), esquerda=True)
            self._desenhar_moeda((rect.right - 108, rect.centery), 12)
            self._texto(self.fonte_m, f"{self.custo:,}".replace(",", "."), COR_TEXTO,
                        (rect.right - 88, rect.centery), esquerda=True)
