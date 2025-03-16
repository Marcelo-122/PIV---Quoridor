class JogoQuoridor:
    def __init__(self):
        # Posições dos jogadores (tabuleiro 9x9)
        self.jogadores = {
            'J1': (0, 4),  # Posição inicial (linha, coluna)
            'J2': (8, 4)
        }
        
        # Posições das paredes (grades 8x8)
        self.paredes_horizontais = [[False]*8 for _ in range(8)]  # Paredes horizontais entre as linhas
        self.paredes_verticais = [[False]*8 for _ in range(8)]  # Paredes verticais entre as colunas

    def colocar_parede(self, notacao):
        """Coloca uma parede dada uma notação como 'e7h' ou 'd4v'."""
        if len(notacao) != 3:
            print("Notação inválida! Use o formato como 'e7h' ou 'd4v'.")
            return

        letra_coluna, numero_linha, direcao = notacao
        coluna = ord(letra_coluna) - ord('a')  # Converte 'a' para 0, 'b' para 1, ..., 'i' para 8
        linha = int(numero_linha) - 1  # Converte '1'-'9' para 0-8

        if direcao == 'h':  # Parede horizontal
            if linha > 0 and coluna < 7:  # Deve estar dentro da grade 8x8
                self.paredes_horizontais[linha-1][coluna] = True
                self.paredes_horizontais[linha-1][coluna+1] = True
            else:
                print("Posição inválida para parede horizontal")
        
        elif direcao == 'v':  # Parede vertical
            if linha < 7 and coluna > 0:  # Deve estar dentro da grade 8x8
                self.paredes_verticais[linha][coluna-1] = True
                self.paredes_verticais[linha+1][coluna-1] = True
            else:
                print("Posição inválida para parede vertical")

        else:
            print("Direção inválida! Use 'h' para horizontal ou 'v' para vertical.")

    def imprimir_tabuleiro(self):
        print("   " + " ".join(f" {chr(97+i)} " for i in range(9)))  # Rótulos das colunas a-i
        
        for linha in range(9):
            # Imprime a linha dos jogadores com paredes verticais
            linha_str = f"{linha+1} "  # Números das linhas 1-9
            for coluna in range(9):
                # Jogador ou espaço vazio
                if (linha, coluna) == self.jogadores['J1']:
                    linha_str += " J1 "
                elif (linha, coluna) == self.jogadores['J2']:
                    linha_str += " J2 "
                else:
                    linha_str += " · "
                
                # Parede vertical à direita da célula atual
                if coluna < 8 and linha < 8 and self.paredes_verticais[linha][coluna]:
                    linha_str += "│"
                else:
                    linha_str += " "
            
            print(linha_str)
            
            # Imprime paredes horizontais entre as linhas (apenas até a linha 7)
            if linha < 8:
                linha_paredes = "  "
                for coluna in range(9):
                    # Parede horizontal abaixo da célula atual
                    if coluna < 8 and self.paredes_horizontais[linha][coluna]:
                        linha_paredes += "───"
                    else:
                        linha_paredes += "   "
                    
                    # Marcador de interseção
                    if coluna < 8 and (self.paredes_horizontais[linha][coluna] or self.paredes_verticais[linha][coluna]):
                        linha_paredes += "┼"
                    else:
                        linha_paredes += " "
                
                print(linha_paredes)

    def andar(self, direcao,turno):
        jogador = 'J1' if turno == 0 else 'J2'  # Define o jogador atual
        linha, coluna = self.jogadores[jogador]  # Obtém a posição atual do jogador

        # Direções de movimento
        movimentos = {
            'w': (-1, 0),  # Cima
            's': (1, 0),   # Baixo
            'a': (0, -1),  # Esquerda
            'd': (0, 1)    # Direita
        }

        if direcao not in movimentos:
            print("Movimento inválido! Use 'w', 'a', 's' ou 'd'.")
            return

        d_linha, d_coluna = movimentos[direcao]
        nova_linha, nova_coluna = linha + d_linha, coluna + d_coluna

        # Verifica os limites do tabuleiro
        if not (0 <= nova_linha < 9 and 0 <= nova_coluna < 9):
            print("Movimento fora dos limites!")
            return

        # Verifica se há uma parede bloqueando o caminho
        if direcao == 'w' and linha > 0 and self.paredes_horizontais[linha - 1][coluna]:  # Movimento para cima
            print("Há uma parede bloqueando o caminho!")
            return
        if direcao == 's' and self.paredes_horizontais[linha][coluna]:  # Movimento para baixo
            print("Há uma parede bloqueando o caminho!")
            return
        if direcao == 'a' and coluna > 0 and self.paredes_verticais[linha][coluna - 1]:  # Movimento para a esquerda
            print("Há uma parede bloqueando o caminho!")
            return
        if direcao == 'd' and self.paredes_verticais[linha][coluna]:  # Movimento para a direita
            print("Há uma parede bloqueando o caminho!")
            return

        # Atualiza a posição do jogador
        self.jogadores[jogador] = (nova_linha, nova_coluna)
    def verificar_vitoria(self):
        if self.jogadores['J1'][0] == 8:  
            print("Player 1 venceu!")
            return True
        if self.jogadores['J2'][0] == 0:   
            print("Player 2 venceu!")
            return True
        return False 

# Cria o jogo
jogo = JogoQuoridor()

game_over = False
turn = 0  # 0 = Player 1, 1 = Player 2

while not game_over:
    jogo.imprimir_tabuleiro()
    
    player = "Player 1" if turn == 0 else "Player 2"
    print(f"Turno atual: {player}")

    tipo_jogada = input("Escolha: Andar (2) ou Colocar Parede (1)? ")
    
    if tipo_jogada == "1":  # Coloca uma parede
        parede_input = input("Digite a posição da parede (ex: e7h): ")
        jogo.colocar_parede(parede_input)
    
    elif tipo_jogada == "2":  # Anda
        movimento_input = input("Digite o movimento (ex: w, a, s, d): ")
    
    else:
        print("Entrada inválida. Escolha 1 (Parede) ou 2 (Andar).")
        continue

    # Check for game over condition (e.g., if a player reaches the opposite side)
    if jogo.verificar_vitoria():
        game_over = True

    # Faz a troca de turnos 
    turn = (turn + 1) % 2