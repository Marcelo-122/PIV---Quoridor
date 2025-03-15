import pygame
from .constantes import WHITE, BLACK, LINHAS, COLUNAS, LACUNA_TAMANHO
from .peca import Peça

class Tabuleiro:
    def __init__(self):
        self.tabuleiro = []
        self.peca_selecionada = None
        self.cria_tabuleiro()

    def desenha_grid(self,win):
        win.fill(WHITE)
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                pygame.draw.rect(win, BLACK, (linha*LACUNA_TAMANHO, coluna*LACUNA_TAMANHO,LACUNA_TAMANHO,LACUNA_TAMANHO), 2)

    def cria_tabuleiro(self):
        for linha in range(LINHAS):
            self.tabuleiro.append([])
            for coluna in range(COLUNAS):   
                if coluna == 4 and (linha == 0 or linha == 8):
                     self.tabuleiro[linha].append(Peça(linha,coluna,WHITE))
                else:
                    self.tabuleiro[linha].append(0)
                    
    def desenha(self,win):
        self.desenha_grid(win)
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                peca = self.tabuleiro[linha][coluna]
                if peca != 0:
                    peca.desenha(win)