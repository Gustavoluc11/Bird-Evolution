import math

import pygame

from Codigo import cursor, ui
from Codigo.jogo import ALTURA, LARGURA
from Codigo.passaro import Passaro

CREDITO = "Criado por: Gustavo Gomes"


def _carregar_fundo(pasta_projeto):
    fundo = pygame.image.load(str(pasta_projeto / "AV" / "Fundos" / "Fundo.jpg")).convert()
    if fundo.get_size() != (LARGURA, ALTURA):
        fundo = pygame.transform.smoothscale(fundo, (LARGURA, ALTURA))
    return fundo


class Menu:
    """Tela inicial: Começar jogo, Configurações e Sair."""

    def __init__(self, tela, pasta_projeto, audio):
        self.tela = tela
        self.audio = audio
        self.fundo = _carregar_fundo(pasta_projeto)
        Passaro.carregar_imagens(pasta_projeto / "AV" / "Passaros")

        self.f_botao = ui.fonte(30)
        self.f_credito = ui.fonte(19)
        self.f_pequena = ui.fonte(18)

        self.jogo_em_andamento = False  # vira "Continuar" depois que o jogo começou
        self.tempo = 0.0
        self.pressionado = None

        self.placa = self._criar_placa()
        self.botoes = {}
        for i, id_botao in enumerate(("jogar", "config", "sair")):
            self.botoes[id_botao] = pygame.Rect(LARGURA // 2 - 170, 265 + i * 84, 340, 64)

        # Aves decorativas embaixo (clique nelas para ouvir o som!)
        self.aves = []
        for nivel, x in zip(range(1, 7), (115, 270, 425, 585, 745, 880)):
            ave = Passaro(nivel, x, 0, pop=False)
            base_y = 696 - ave.altura / 2
            ave.y = base_y
            self.aves.append(dict(ave=ave, base_y=base_y, salto=None))

    # ------------------------------------------------------------------
    def _criar_placa(self):
        """Placa de madeira com o título 'BIRD EVOLUTION'."""
        fonte_bird = ui.fonte(70, titulo=True)
        fonte_evo = ui.fonte(54, titulo=True)
        bird = ui.texto_contorno(fonte_bird, "BIRD", (120, 200, 240),
                                 [(( 70, 40, 15), 7), ((255, 255, 255), 4)])
        evo = ui.texto_contorno(fonte_evo, "EVOLUTION", (255, 204, 70),
                                [((70, 40, 15), 7), ((255, 255, 255), 4)])
        largura = max(bird.get_width(), evo.get_width()) + 70
        largura = max(largura, 400)
        altura = bird.get_height() + evo.get_height() - 18 + 34
        placa = ui.placa_madeira(largura, altura)
        placa.blit(bird, bird.get_rect(midtop=(largura // 2, 12)))
        placa.blit(evo, evo.get_rect(midtop=(largura // 2, 12 + bird.get_height() - 18)))
        return placa

    # ------------------------------------------------------------------
    def _rotulo(self, id_botao):
        if id_botao == "jogar":
            return "Continuar" if self.jogo_em_andamento else "Começar jogo"
        return {"config": "Configurações", "sair": "Sair"}[id_botao]

    def _botao_em(self, pos):
        for id_botao, rect in self.botoes.items():
            if rect.collidepoint(pos):
                return id_botao
        return None

    def _ave_em(self, pos):
        for item in reversed(self.aves):
            if item["ave"].rect.collidepoint(pos):
                return item
        return None

    # ------------------------------------------------------------------
    def evento(self, ev):
        """Retorna 'jogar', 'config', 'sair' ou None."""
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.pressionado = self._botao_em(ev.pos)
            if not self.pressionado:
                item = self._ave_em(ev.pos)
                if item:
                    item["salto"] = 0.0
                    self.audio.tocar_passaro(item["ave"].nivel)

        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            pressionado, self.pressionado = self.pressionado, None
            alvo = self._botao_em(ev.pos)
            return alvo if alvo and alvo == pressionado else None
        return None

    # ------------------------------------------------------------------
    def atualizar(self, dt):
        self.tempo += dt
        for item in self.aves:
            if item["salto"] is not None:
                item["salto"] += dt
                p = item["salto"] / 0.45
                if p >= 1:
                    item["salto"] = None
                    item["ave"].y = item["base_y"]
                else:
                    item["ave"].y = item["base_y"] - 55 * math.sin(p * math.pi)

        mouse = pygame.mouse.get_pos()
        cursor.definir(self._botao_em(mouse) is not None or self._ave_em(mouse) is not None)

    # ------------------------------------------------------------------
    def desenhar(self):
        tela = self.tela
        tela.blit(self.fundo, (0, 0))

        # Aves decorativas
        for item in self.aves:
            item["ave"].desenhar(tela, self.tempo)

        # Placa pendurada por cordas, balançando de leve
        x = (LARGURA - self.placa.get_width()) // 2
        topo = 62 + math.sin(self.tempo * 1.6) * 3
        for cx in (x + 58, x + self.placa.get_width() - 58):
            pygame.draw.line(tela, (95, 62, 30), (cx, 0), (cx, topo + 12), 9)
            pygame.draw.line(tela, (205, 165, 105), (cx, 0), (cx, topo + 12), 5)
        tela.blit(self.placa, (x, topo))

        # Botões
        mouse = pygame.mouse.get_pos()
        for id_botao, rect in self.botoes.items():
            ui.botao_madeira(tela, rect, self._rotulo(id_botao), self.f_botao,
                             hover=rect.collidepoint(mouse),
                             pressionado=(self.pressionado == id_botao))

        ui.texto(tela, self.f_pequena, "Versão Demo", (255, 255, 255),
                 (LARGURA // 2, 524), alfa=220)

        # Crédito no canto superior direito
        largura_txt = self.f_credito.size(CREDITO)[0]
        painel = pygame.Rect(0, 14, largura_txt + 30, 40)
        painel.right = LARGURA - 16
        ui.painel(tela, painel)
        ui.texto(tela, self.f_credito, CREDITO, (255, 255, 255), painel.center)


class Slider:
    def __init__(self, rect, valor):
        self.rect = rect
        self.valor = valor
        self.arrastando = False

    def area_clique(self):
        return self.rect.inflate(30, 40)

    def mover_para(self, x):
        self.valor = max(0.0, min(1.0, (x - self.rect.left) / self.rect.width))

    def desenhar(self, tela):
        r = self.rect
        pygame.draw.rect(tela, (70, 45, 22), r.inflate(6, 6), border_radius=10)
        pygame.draw.rect(tela, (110, 80, 50), r, border_radius=8)
        cheio = pygame.Rect(r.left, r.top, round(r.width * self.valor), r.height)
        if cheio.width > 0:
            pygame.draw.rect(tela, (120, 200, 90), cheio, border_radius=8)
        cx = r.left + round(r.width * self.valor)
        pygame.draw.circle(tela, (90, 55, 25), (cx, r.centery + 2), 17)
        pygame.draw.circle(tela, (255, 240, 205), (cx, r.centery), 16)
        pygame.draw.circle(tela, (110, 68, 32), (cx, r.centery), 16, 3)


class Configuracoes:
    """Volume da música, volume dos efeitos, tela cheia e voltar."""

    def __init__(self, tela, pasta_projeto, audio):
        self.tela = tela
        self.audio = audio
        self.fundo = _carregar_fundo(pasta_projeto)
        self.tela_cheia = False  # o main atualiza isto

        self.f_titulo = ui.fonte(46, titulo=True)
        self.f_texto = ui.fonte(26)
        self.f_botao = ui.fonte(28)
        self.f_pequena = ui.fonte(18)

        self.tempo = 0.0
        self.pressionado = None

        self.painel_rect = pygame.Rect(0, 0, 520, 540)
        self.painel_rect.center = (LARGURA // 2, 372)
        self.placa = ui.placa_madeira(*self.painel_rect.size, raio=22)
        self.titulo = ui.texto_contorno(self.f_titulo, "Configurações", (255, 204, 70),
                                        [((70, 40, 15), 5), ((255, 255, 255), 3)])

        cx = LARGURA // 2
        topo = self.painel_rect.top
        self.slider_musica = Slider(pygame.Rect(cx - 190, topo + 190, 380, 16), audio.config.musica)
        self.slider_efeitos = Slider(pygame.Rect(cx - 190, topo + 290, 380, 16), audio.config.efeitos)
        self.botoes = {
            "tela_cheia": pygame.Rect(cx - 170, topo + 358, 340, 56),
            "voltar": pygame.Rect(cx - 170, topo + 436, 340, 56),
        }

    # ------------------------------------------------------------------
    def _botao_em(self, pos):
        for id_botao, rect in self.botoes.items():
            if rect.collidepoint(pos):
                return id_botao
        return None

    def evento(self, ev):
        """Retorna 'voltar', 'tela_cheia' ou None."""
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.pressionado = self._botao_em(ev.pos)
            for slider in (self.slider_musica, self.slider_efeitos):
                if slider.area_clique().collidepoint(ev.pos):
                    slider.arrastando = True
                    slider.mover_para(ev.pos[0])
                    self._aplicar()
                    break

        elif ev.type == pygame.MOUSEMOTION:
            for slider in (self.slider_musica, self.slider_efeitos):
                if slider.arrastando:
                    slider.mover_para(ev.pos[0])
                    self._aplicar()

        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            for slider in (self.slider_musica, self.slider_efeitos):
                if slider.arrastando:
                    slider.arrastando = False
                    self.audio.config.salvar()
                    if slider is self.slider_efeitos:
                        self.audio.tocar_passaro(1)  # amostra para ouvir o volume
            acao = None
            alvo = self._botao_em(ev.pos)
            if alvo and alvo == self.pressionado:
                acao = alvo
            self.pressionado = None
            return acao
        return None

    def _aplicar(self):
        self.audio.definir_volume_musica(self.slider_musica.valor)
        self.audio.definir_volume_efeitos(self.slider_efeitos.valor)

    # ------------------------------------------------------------------
    def atualizar(self, dt):
        self.tempo += dt
        mouse = pygame.mouse.get_pos()
        sobre = (self._botao_em(mouse) is not None
                 or any(s.area_clique().collidepoint(mouse)
                        for s in (self.slider_musica, self.slider_efeitos)))
        cursor.definir(sobre)

    def desenhar(self):
        tela = self.tela
        tela.blit(self.fundo, (0, 0))
        tela.blit(self.placa, self.painel_rect.topleft)
        tela.blit(self.titulo, self.titulo.get_rect(center=(LARGURA // 2, self.painel_rect.top + 70)))

        cx = LARGURA // 2
        for slider, nome, dy in ((self.slider_musica, "Música", 150), (self.slider_efeitos, "Efeitos", 250)):
            y = self.painel_rect.top + dy
            ui.texto(tela, self.f_texto, nome, (255, 255, 255), (cx - 190, y), esquerda=True)
            ui.texto(tela, self.f_texto, f"{round(slider.valor * 100)}%", (255, 230, 150),
                     (cx + 190, y), direita=True)
            slider.desenhar(tela)

        mouse = pygame.mouse.get_pos()
        rotulos = {
            "tela_cheia": f"Tela cheia: {'Ligada' if self.tela_cheia else 'Desligada'}",
            "voltar": "Voltar",
        }
        for id_botao, rect in self.botoes.items():
            ui.botao_madeira(tela, rect, rotulos[id_botao], self.f_botao,
                             hover=rect.collidepoint(mouse),
                             pressionado=(self.pressionado == id_botao))

        ui.texto(tela, self.f_pequena, "F11 tela cheia  •  M música  •  ESC voltar",
                 (255, 245, 220), (cx, self.painel_rect.bottom - 24))
