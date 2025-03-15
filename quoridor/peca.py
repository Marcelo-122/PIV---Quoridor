import pygame
from .constantes import LACUNA_TAMANHO, RED

class Peça:
    def __init__(self, linha, coluna, cor):
        self.linha = linha
        self.coluna = coluna
        self.cor = cor

        self.x = 0
        self.y = 0
        self.calcula_pos()

    def calcula_pos(self):
        self.x = LACUNA_TAMANHO * self.coluna + LACUNA_TAMANHO // 2
        self.y = LACUNA_TAMANHO * self.linha + LACUNA_TAMANHO // 2

    def desenha(self, win):
        pygame.draw.circle(win, RED, (self.x, self.y ), 20)

    def __repr__(self):
        return str(self.cor)
    