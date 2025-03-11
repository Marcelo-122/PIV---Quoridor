import pygame
from .constantes import WHITE, BLACK, LINHAS, COLUNAS, LACUNA_TAMANHO

class Tabuleiro:
    def __init__(self,):
        self.tabuleiro = []

    def desenha_grid(self,win):
        win.fill(WHITE)
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                pygame.draw.rect(win, BLACK, (linha*LACUNA_TAMANHO, coluna*LACUNA_TAMANHO,LACUNA_TAMANHO,LACUNA_TAMANHO), 2)

    def cria_tabuleiro():
        pass