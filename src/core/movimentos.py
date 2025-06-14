def andar(self, direcao, turno):
    jogador = "J1" if turno == 0 else "J2"
    linha, coluna = self.jogadores[jogador]

    movimentos = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}

    if direcao not in movimentos:
        #print("Movimento inválido! Use 'w', 'a', 's' ou 'd'.")
        return False

    d_linha, d_coluna = movimentos[direcao]
    nova_linha, nova_coluna = linha + d_linha, coluna + d_coluna

    # Verifica se a nova posição está ocupada pelo outro jogador
    outro_jogador = "J2" if jogador == "J1" else "J1"
    if (nova_linha, nova_coluna) == self.jogadores[outro_jogador]:
        # Tenta saltar sobre o oponente
        nova_linha += d_linha
        nova_coluna += d_coluna
        # Aqui, uma lógica mais complexa para verificar paredes atrás do oponente seria necessária
        # para um salto válido, mas por enquanto vamos simplificar.

    # Usar dimensões dinâmicas do tabuleiro
    if not (0 <= nova_linha < self.linhas and 0 <= nova_coluna < self.colunas):
        #print("Movimento fora dos limites!")
        return False

    # Verifica se há paredes bloqueando o caminho
    if direcao == "w":
        if linha == 0 or not self.tabuleiro[linha][coluna].pode_mover_para_cima:
            #print("Há uma parede bloqueando o caminho!")
            return False
    if direcao == "s":
        #print(f"[DEBUG] Movimento para baixo (s): linha={linha}, linhas={self.linhas}, ultima_linha={self.linhas-1}")
        #print(f"[DEBUG] Pode mover para baixo = {self.tabuleiro[linha][coluna].pode_mover_para_baixo}")
        if linha == self.linhas - 1 or not self.tabuleiro[linha][coluna].pode_mover_para_baixo:
            #print(f"[DEBUG] Movimento bloqueado: na_ultima_linha={linha == self.linhas-1}, parede_bloqueando={not self.tabuleiro[linha][coluna].pode_mover_para_baixo}")
            return False
    if direcao == "a":
        if coluna == 0 or not self.tabuleiro[linha][coluna].pode_mover_para_esquerda:
           # print("Há uma parede bloqueando o caminho!")
            return False
    if direcao == "d":
        if coluna == self.colunas - 1 or not self.tabuleiro[linha][coluna].pode_mover_para_direita:
           # print("Há uma parede bloqueando o caminho!")
            return False

    # Atualiza o tabuleiro se ele existir
    if hasattr(self, "tabuleiro"):
        # Limpa a posição antiga
        if 0 <= linha < self.linhas and 0 <= coluna < self.colunas:
            self.tabuleiro[linha][coluna].tem_jogador = False
        # Define a nova posição
        if 0 <= nova_linha < self.linhas and 0 <= nova_coluna < self.colunas:
            self.tabuleiro[nova_linha][nova_coluna].tem_jogador = True

    self.jogadores[jogador] = (nova_linha, nova_coluna)
    return True
