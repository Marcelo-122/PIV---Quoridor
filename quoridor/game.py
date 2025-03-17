class JogoQuoridor:
    def __init__(self):
        # Posições dos jogadores (tabuleiro 9x9)
        self.jogadores = {
            "J1": (0, 4),  # Posição inicial (linha, coluna)
            "J2": (8, 4)   
        }

        # Grades 8x8 para paredes
        self.paredes_horizontais = [[False] * 8 for _ in range(8)]
        self.paredes_verticais = [[False] * 8 for _ in range(8)]

        # Máximo de 10 paredes por jogador
        self.paredes_restantes = {"J1": 10, "J2": 10}

    def colocar_parede(self, notacao, turno):
        """Coloca uma parede dada uma notação como 'e7h' ou 'd4v'."""
        jogador = "J1" if turno == 0 else "J2" 

        if self.paredes_restantes[jogador] <= 0:
            print(f"{jogador} não tem mais paredes disponíveis!")
            return False

        if len(notacao) != 3:
            print("Notação inválida! Use o formato 'e7h' ou 'd4v'.")
            return False

        letra_coluna, numero_linha, direcao = notacao
        coluna = ord(letra_coluna) - ord("a")  # Converte 'a' para 0, ..., 'i' para 8
        linha = int(numero_linha) - 1          # Converte '1'-'9' para 0-8

        if direcao == "h":  # Parede horizontal
            if linha > 0 and coluna < 7:  
                if self.paredes_horizontais[linha - 1][coluna]:
                    print("Já existe uma parede aqui!")
                    return False
                self.paredes_horizontais[linha - 1][coluna] = True
                self.paredes_horizontais[linha - 1][coluna + 1] = True
            else:
                print("Posição inválida para parede horizontal!")
                return False

        elif direcao == "v":  # Parede vertical
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

    def imprimir_tabuleiro(self):
        print("   " + " ".join(f" {chr(97+i)} " for i in range(9)))  # Rótulos das colunas
        
        for linha in range(9):
            linha_str = f"{linha+1} "  # Números das linhas
            for coluna in range(9):
                if (linha, coluna) == self.jogadores["J1"]:
                    linha_str += " J1 "
                elif (linha, coluna) == self.jogadores["J2"]:
                    linha_str += " J2 "
                else:
                    linha_str += " · "
                
                if coluna < 8 and linha < 8 and self.paredes_verticais[linha][coluna]:
                    linha_str += "│"
                else:
                    linha_str += " "
            
            print(linha_str)
            
            if linha < 8:
                linha_paredes = "  "
                for coluna in range(9):
                    if coluna < 8 and self.paredes_horizontais[linha][coluna]:
                        linha_paredes += "───"
                    else:
                        linha_paredes += "   "
                    
                    if coluna < 8 and (self.paredes_horizontais[linha][coluna] or self.paredes_verticais[linha][coluna]):
                        linha_paredes += "┼"
                    else:
                        linha_paredes += " "
                
                print(linha_paredes)

    def andar(self, direcao, turno):
        jogador = "J1" if turno == 0 else "J2"
        linha, coluna = self.jogadores[jogador]

        movimentos = {
            "w": (-1, 0),  # Cima
            "s": (1, 0),   # Baixo
            "a": (0, -1),  # Esquerda
            "d": (0, 1)    # Direita
        }

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

    def verificar_vitoria(self):
        if self.jogadores["J1"][0] == 8:  
            print("Player 1 venceu!")
            return True
        if self.jogadores["J2"][0] == 0:   
            print("Player 2 venceu!")
            return True
        return False 
