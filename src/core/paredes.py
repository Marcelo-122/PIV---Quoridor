def colocar_parede(self, notacao, turno):
    if len(notacao) != 3:
        # print("Notação inválida! Use o formato 'e7h' ou 'd4v'.")
        return False

    letra_coluna, numero_linha, direcao = notacao
    coluna = ord(letra_coluna) - ord("a")
    linha = int(numero_linha) - 1
    
    # Determinar dimensões do tabuleiro
    num_linhas = len(self.tabuleiro)
    num_colunas = len(self.tabuleiro[0]) if num_linhas > 0 else 0

    if direcao == "h":
        if linha < num_linhas - 1 and coluna < num_colunas - 1:
            if not self.tabuleiro[linha][coluna].pode_mover_para_baixo or not self.tabuleiro[linha][coluna + 1].pode_mover_para_baixo:
                # print("Já existe uma parede aqui! (Sobreposição)")
                return False
            if (coluna > 0 and not self.tabuleiro[linha][coluna-1].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna-1].pode_mover_para_direita) or \
               (coluna < num_colunas - 1 and not self.tabuleiro[linha][coluna].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna].pode_mover_para_direita):
                if not self.tabuleiro[linha][coluna].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna].pode_mover_para_direita:
                    # print("Muro cruzaria com um existente!")
                    return False

            self.tabuleiro[linha][coluna].pode_mover_para_baixo = False
            self.tabuleiro[linha][coluna + 1].pode_mover_para_baixo = False
            self.tabuleiro[linha + 1][coluna].pode_mover_para_cima = False
            self.tabuleiro[linha + 1][coluna + 1].pode_mover_para_cima = False
        else:
            # print("Posição inválida para parede horizontal!")
            return False

    elif direcao == "v":
        if linha < num_linhas - 1 and coluna > 0:
            if not self.tabuleiro[linha][coluna - 1].pode_mover_para_direita or not self.tabuleiro[linha + 1][coluna - 1].pode_mover_para_direita:
                # print("Já existe uma parede aqui! (Sobreposição)")
                return False
            if (not self.tabuleiro[linha][coluna - 1].pode_mover_para_baixo and
                not self.tabuleiro[linha][coluna].pode_mover_para_baixo):
                # print("Muro cruzaria com um existente!")
                return False
            self.tabuleiro[linha][coluna - 1].pode_mover_para_direita = False
            self.tabuleiro[linha + 1][coluna - 1].pode_mover_para_direita = False
            self.tabuleiro[linha][coluna].pode_mover_para_esquerda = False
            self.tabuleiro[linha + 1][coluna].pode_mover_para_esquerda = False
        else:
            # print("Posição inválida para parede vertical!")
            return False

    else:
        # print("Direção inválida! Use 'h' para horizontal ou 'v' para vertical.")
        return False

    # print("Parede colocada com sucesso.")
    return True
