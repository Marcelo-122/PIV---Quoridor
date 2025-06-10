def andar(self, direcao, turno):
    jogador = "J1" if turno == 0 else "J2"
    linha, coluna = self.jogadores[jogador]

    movimentos = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}

    if direcao not in movimentos:
        print("Movimento inválido! Use 'w', 'a', 's' ou 'd'.")
        return False

    d_linha, d_coluna = movimentos[direcao]
    nova_linha, nova_coluna = linha + d_linha, coluna + d_coluna

    if not (0 <= nova_linha < 9 and 0 <= nova_coluna < 9):
        print("Movimento fora dos limites!")
        return False

    # Verifica se há paredes bloqueando o caminho
    if direcao == "w":
        if linha == 0 or not self.tabuleiro[linha][coluna].pode_mover_para_cima:
            print("Há uma parede bloqueando o caminho!")
            return False
    if direcao == "s":
        if linha == 8 or not self.tabuleiro[linha][coluna].pode_mover_para_baixo:
            print("Há uma parede bloqueando o caminho!")
            return False
    if direcao == "a":
        if coluna == 0 or not self.tabuleiro[linha][coluna].pode_mover_para_esquerda:
            print("Há uma parede bloqueando o caminho!")
            return False
    if direcao == "d":
        if coluna == 8 or not self.tabuleiro[linha][coluna].pode_mover_para_direita:
            print("Há uma parede bloqueando o caminho!")
            return False

    # Atualiza o tabuleiro se ele existir
    if hasattr(self, "tabuleiro"):
        # Limpa a posição antiga
        if 0 <= linha < 9 and 0 <= coluna < 9:
            self.tabuleiro[linha][coluna].tem_jogador = False
        # Define a nova posição
        if 0 <= nova_linha < 9 and 0 <= nova_coluna < 9:
            self.tabuleiro[nova_linha][nova_coluna].tem_jogador = True

    self.jogadores[jogador] = (nova_linha, nova_coluna)
    return True
