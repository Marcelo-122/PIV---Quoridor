def colocar_parede(self, notacao, turno):
    jogador = "J1" if turno == 0 else "J2"

    if self.paredes_restantes[jogador] <= 0:
        print(f"{jogador} não tem mais paredes disponíveis!")
        return False

    if len(notacao) != 3:
        print("Notação inválida! Use o formato 'e7h' ou 'd4v'.")
        return False

    letra_coluna, numero_linha, direcao = notacao
    coluna = ord(letra_coluna) - ord("a")
    linha = int(numero_linha) - 1

    if direcao == "h":
        if linha > 0 and coluna < 7:
            if self.paredes_horizontais[linha - 1][coluna]:
                print("Já existe uma parede aqui!")
                return False
            self.paredes_horizontais[linha - 1][coluna] = True
            self.paredes_horizontais[linha - 1][coluna + 1] = True
        else:
            print("Posição inválida para parede horizontal!")
            return False

    elif direcao == "v":
        if linha < 7 and coluna > 0:
            if self.paredes_verticais[linha][coluna - 1]:
                print("Já existe uma parede aqui!")
                return False
            self.paredes_verticais[linha][coluna - 1] = True
            self.paredes_verticais[linha + 1][coluna - 1] = True
        else:
            print("Posição inválida para parede vertical!")
            return False

    else:
        print("Direção inválida! Use 'h' para horizontal ou 'v' para vertical.")
        return False

    self.paredes_restantes[jogador] -= 1
    print(f"{jogador} agora tem {self.paredes_restantes[jogador]} paredes restantes.")
    return True
