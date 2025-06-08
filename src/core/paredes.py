def colocar_parede(self, notacao, turno):
    if len(notacao) != 3:
        print("Notação inválida! Use o formato 'e7h' ou 'd4v'.")
        return False

    letra_coluna, numero_linha, direcao = notacao
    coluna = ord(letra_coluna) - ord("a")
    linha = int(numero_linha) - 1

    if direcao == "h":
        if linha > 0 and coluna < 7:
            # Check if wall already exists by checking path availability
            if not self.tabuleiro[linha - 1][coluna].pode_mover_para_baixo or not self.tabuleiro[linha - 1][coluna + 1].pode_mover_para_baixo:
                print("Já existe uma parede aqui!")
                return False
            # Block movement down from above
            self.tabuleiro[linha - 1][coluna].pode_mover_para_baixo = False
            self.tabuleiro[linha - 1][coluna + 1].pode_mover_para_baixo = False
            # Block movement up from below
            self.tabuleiro[linha][coluna].pode_mover_para_cima = False
            self.tabuleiro[linha][coluna + 1].pode_mover_para_cima = False
        else:
            print("Posição inválida para parede horizontal!")
            return False

    elif direcao == "v":
        if linha < 7 and coluna > 0:
            # Check if wall already exists by checking path availability
            if not self.tabuleiro[linha][coluna - 1].pode_mover_para_direita or not self.tabuleiro[linha + 1][coluna - 1].pode_mover_para_direita:
                print("Já existe uma parede aqui!")
                return False
            # Block movement right from left
            self.tabuleiro[linha][coluna - 1].pode_mover_para_direita = False
            self.tabuleiro[linha + 1][coluna - 1].pode_mover_para_direita = False
            # Block movement left from right
            self.tabuleiro[linha][coluna].pode_mover_para_esquerda = False
            self.tabuleiro[linha + 1][coluna].pode_mover_para_esquerda = False
        else:
            print("Posição inválida para parede vertical!")
            return False

    else:
        print("Direção inválida! Use 'h' para horizontal ou 'v' para vertical.")
        return False

    print("Parede colocada com sucesso.")
    return True
