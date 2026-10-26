"""Peças visuais reutilizadas pelo menu e pelas configurações."""
import random

import pygame

COR_TEXTO = (255, 255, 255)
COR_SOMBRA = (30, 40, 30)


def fonte(tamanho, titulo=False):
    nomes = "segoeui,arial,dejavusans"
    if titulo:
        nomes = "arialroundedmtbold,comicsansms," + nomes
    return pygame.font.SysFont(nomes, tamanho, bold=True)


def texto(tela, fnt, txt, cor, pos, esquerda=False, direita=False, alfa=255):
    """Texto com sombrinha. Por padrão fica centralizado em pos."""
    sombra = fnt.render(txt, True, COR_SOMBRA)
    principal = fnt.render(txt, True, cor)
    if alfa < 255:
        sombra.set_alpha(alfa)
        principal.set_alpha(alfa)
    rect = principal.get_rect()
    if esquerda:
        rect.midleft = pos
    elif direita:
        rect.midright = pos
    else:
        rect.center = pos
    tela.blit(sombra, rect.move(2, 2))
    tela.blit(principal, rect)
    return rect


def painel(tela, rect, alfa=150):
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surf, (20, 40, 25, alfa), surf.get_rect(), border_radius=14)
    pygame.draw.rect(surf, (255, 255, 255, 60), surf.get_rect(), width=2, border_radius=14)
    tela.blit(surf, rect.topleft)


def texto_contorno(fnt, txt, cor, contornos):
    """Texto grande com contorno grosso. contornos = [(cor, raio), ...] do maior ao menor."""
    raio_max = max(r for _, r in contornos)
    base = fnt.render(txt, True, cor)
    w, h = base.get_size()
    surf = pygame.Surface((w + 2 * raio_max, h + 2 * raio_max), pygame.SRCALPHA)
    for cor_c, raio in contornos:
        molde = fnt.render(txt, True, cor_c)
        for dx in range(-raio, raio + 1):
            for dy in range(-raio, raio + 1):
                if dx * dx + dy * dy <= raio * raio:
                    surf.blit(molde, (raio_max + dx, raio_max + dy))
    surf.blit(base, (raio_max, raio_max))
    return surf


def placa_madeira(largura, altura, raio=18):
    """Placa de madeira com tábuas, veios e pregos (criada uma vez só)."""
    rnd = random.Random(largura * 7 + altura)
    surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.rect(surf, (96, 58, 26), surf.get_rect(), border_radius=raio)

    interior = surf.get_rect().inflate(-10, -10)
    madeira = pygame.Surface(interior.size, pygame.SRCALPHA)
    n = max(2, altura // 46)
    esp = interior.height / n
    for i in range(n):
        y0 = round(i * esp)
        y1 = round((i + 1) * esp)
        tom = rnd.randint(-9, 9)
        pygame.draw.rect(madeira, (184 + tom, 120 + tom, 62 + tom // 2),
                         (0, y0, interior.width, y1 - y0))
        pygame.draw.line(madeira, (214, 156, 92), (0, y0 + 2), (interior.width, y0 + 2), 2)
        for _ in range(7):  # veios da madeira
            vx = rnd.randint(0, interior.width - 40)
            vy = rnd.randint(y0 + 8, max(y0 + 9, y1 - 8))
            pygame.draw.line(madeira, (150, 96, 48),
                             (vx, vy), (vx + rnd.randint(25, 110), vy), 1)
        pygame.draw.line(madeira, (116, 72, 34), (0, y1 - 1), (interior.width, y1 - 1), 3)

    molde = pygame.Surface(interior.size, pygame.SRCALPHA)
    pygame.draw.rect(molde, (255, 255, 255, 255), molde.get_rect(), border_radius=raio - 4)
    madeira.blit(molde, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(madeira, interior.topleft)

    for px, py in ((16, 16), (largura - 16, 16), (16, altura - 16), (largura - 16, altura - 16)):
        pygame.draw.circle(surf, (70, 45, 22), (px, py), 6)
        pygame.draw.circle(surf, (205, 175, 125), (px - 1, py - 1), 3)
    return surf


def botao_madeira(tela, rect, txt, fnt, hover=False, pressionado=False):
    cor = (224, 160, 85) if hover else (200, 135, 65)
    rect = rect.copy()
    if pressionado:
        rect.y += 4
    elif hover:
        rect.y -= 2
    pygame.draw.rect(tela, (80, 48, 20), rect.move(0, 6), border_radius=16)
    pygame.draw.rect(tela, cor, rect, border_radius=16)
    pygame.draw.line(tela, (244, 200, 135), (rect.left + 14, rect.top + 5),
                     (rect.right - 14, rect.top + 5), 3)
    pygame.draw.rect(tela, (110, 68, 32), rect, width=3, border_radius=16)
    texto(tela, fnt, txt, COR_TEXTO, rect.center)
