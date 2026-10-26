from pathlib import Path

import pygame

from Codigo.audio import Audio
from Codigo.config import Config
from Codigo.jogo import ALTURA, LARGURA, Jogo
from Codigo.menu import Configuracoes, Menu

# Inicializa o Pygame
pygame.init()

# SCALED: o jogo continua em 960x720 e é esticado para a tela (sem distorcer)
# quando entra em tela cheia. O mouse é ajustado automaticamente.
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED)
pygame.display.set_caption("Bird Evolution")

relogio = pygame.time.Clock()

# Pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parent

# Configurações salvas + som (compartilhados por todas as telas)
config = Config(pasta_projeto)
audio = Audio(pasta_projeto / "AV" / "Sons", config)
audio.iniciar_musica()

# As três telas do jogo
menu = Menu(tela, pasta_projeto, audio)
ajustes = Configuracoes(tela, pasta_projeto, audio)
jogo = Jogo(tela, pasta_projeto, audio)

estado = "menu"  # "menu", "config" ou "jogo"
jogo_iniciado = False
tela_cheia = False


def alternar_tela_cheia():
    global tela_cheia
    try:
        pygame.display.toggle_fullscreen()
        tela_cheia = not tela_cheia
    except pygame.error:
        print("Aviso: não consegui alternar a tela cheia.")


def ir_para(novo_estado):
    global estado
    if estado == "jogo":
        jogo.cancelar_arrasto()  # se saiu no meio de um arrasto, solta a ave
    estado = novo_estado


rodando = True
while rodando:
    # Tempo entre frames (em segundos), limitado para evitar saltos
    dt = min(relogio.tick(60) / 1000, 0.05)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
            alternar_tela_cheia()

        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_m:
            audio.alternar_musica()

        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if estado in ("jogo", "config"):
                ir_para("menu")
            elif estado == "menu" and jogo_iniciado:
                ir_para("jogo")

        elif estado == "menu":
            acao = menu.evento(evento)
            if acao == "jogar":
                jogo_iniciado = True
                menu.jogo_em_andamento = True
                ir_para("jogo")
            elif acao == "config":
                ir_para("config")
            elif acao == "sair":
                rodando = False

        elif estado == "config":
            acao = ajustes.evento(evento)
            if acao == "voltar":
                ir_para("menu")
            elif acao == "tela_cheia":
                alternar_tela_cheia()

        else:
            jogo.evento(evento)

    # Atualiza e desenha só a tela atual
    if estado == "menu":
        menu.atualizar(dt)
        menu.desenhar()
    elif estado == "config":
        ajustes.tela_cheia = tela_cheia
        ajustes.atualizar(dt)
        ajustes.desenhar()
    else:
        jogo.atualizar(dt)
        jogo.desenhar()

    pygame.display.flip()

pygame.quit()
