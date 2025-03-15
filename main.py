import pygame
from quoridor.constantes import LARGURA, ALTURA
from quoridor.tabuleiro import Tabuleiro

FPS = 60
WIN = pygame.display.set_mode((LARGURA,ALTURA))
pygame.display.set_caption('Quoridor')

def main():
    run = True
    clock = pygame.time.Clock()
    tabuleiro = Tabuleiro()

    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

        tabuleiro.desenha(WIN)
        pygame.display.update()

    pygame.quit()

main()