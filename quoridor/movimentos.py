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

    if direcao == "w" and linha > 0 and self.paredes_horizontais[linha - 1][coluna]:
        print("Há uma parede bloqueando o caminho!")
        return False

    if direcao == "s" and self.paredes_horizontais[linha][coluna]:
        print("Há uma parede bloqueando o caminho!")
        return False

    if direcao == "a" and coluna > 0 and self.paredes_verticais[linha][coluna - 1]:
        print("Há uma parede bloqueando o caminho!")
        return False

    if direcao == "d" and self.paredes_verticais[linha][coluna]:
        print("Há uma parede bloqueando o caminho!")
        return False

    self.jogadores[jogador] = (nova_linha, nova_coluna)
    return True
