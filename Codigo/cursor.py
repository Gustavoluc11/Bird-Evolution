import pygame

_mao = False


def definir(mao):
    """Troca o cursor entre seta e mãozinha (só mexe quando muda)."""
    global _mao
    if mao == _mao:
        return
    _mao = mao
    try:
        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND if mao else pygame.SYSTEM_CURSOR_ARROW
        )
    except Exception:
        pass
