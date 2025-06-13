def andar(self, direcao, turno):
    jogador = "J1" if turno == 0 else "J2"
    oponente = "J2" if turno == 0 else "J1"
    linha, coluna = self.jogadores[jogador]

    movimentos = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}

    if direcao not in movimentos:
        return False

    d_linha, d_coluna = movimentos[direcao]
    nova_linha, nova_coluna = linha + d_linha, coluna + d_coluna

    # Verifica se o movimento está dentro dos limites do tabuleiro
    if not (0 <= nova_linha < 9 and 0 <= nova_coluna < 9):
        return False

    # Verifica se há uma parede bloqueando o caminho
    if direcao == "w" and not self.tabuleiro[linha][coluna].pode_mover_para_cima:
        return False
    if direcao == "s" and not self.tabuleiro[linha][coluna].pode_mover_para_baixo:
        return False
    if direcao == "a" and not self.tabuleiro[linha][coluna].pode_mover_para_esquerda:
        return False
    if direcao == "d" and not self.tabuleiro[linha][coluna].pode_mover_para_direita:
        return False

    # Lógica de Pulo
    if (nova_linha, nova_coluna) == self.jogadores[oponente]:
        linha_pulo, coluna_pulo = nova_linha + d_linha, nova_coluna + d_coluna

        # Verifica se o pulo está dentro dos limites
        if not (0 <= linha_pulo < 9 and 0 <= coluna_pulo < 9):
            return False

        # Verifica se há uma parede bloqueando o pulo
        if (
            direcao == "w"
            and not self.tabuleiro[nova_linha][nova_coluna].pode_mover_para_cima
        ):
            return False
        if (
            direcao == "s"
            and not self.tabuleiro[nova_linha][nova_coluna].pode_mover_para_baixo
        ):
            return False
        if (
            direcao == "a"
            and not self.tabuleiro[nova_linha][nova_coluna].pode_mover_para_esquerda
        ):
            return False
        if (
            direcao == "d"
            and not self.tabuleiro[nova_linha][nova_coluna].pode_mover_para_direita
        ):
            return False

        # Se o pulo for válido, atualiza a posição para a casa do pulo
        nova_linha, nova_coluna = linha_pulo, coluna_pulo

    # Verifica se a casa final (após pulo ou não) já está ocupada
    if (nova_linha, nova_coluna) == self.jogadores[oponente]:
        return False

    # Atualiza o tabuleiro
    if hasattr(self, "tabuleiro"):
        # Limpa a posição antiga
        if 0 <= linha < 9 and 0 <= coluna < 9:
            self.tabuleiro[linha][coluna].tem_jogador = False
        # Define a nova posição
        if 0 <= nova_linha < 9 and 0 <= nova_coluna < 9:
            self.tabuleiro[nova_linha][nova_coluna].tem_jogador = True

    self.jogadores[jogador] = (nova_linha, nova_coluna)

    return True
