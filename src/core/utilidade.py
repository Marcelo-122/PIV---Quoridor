from collections import deque

def shortest_path_length(jogador, pos, tabuleiro):
    # Determinar as dimensões do tabuleiro dinamicamente
    num_linhas = len(tabuleiro)
    num_colunas = len(tabuleiro[0]) if num_linhas > 0 else 0
    
    visitado = [[False for _ in range(num_colunas)] for _ in range(num_linhas)]
    fila = deque()
    fila.append((pos[0], pos[1], 0))  # (linha, coluna, distancia)
    objetivo = num_linhas - 1 if jogador == "J1" else 0

    while fila:
        linha, coluna, dist = fila.popleft()
        if visitado[linha][coluna]:
            continue
        visitado[linha][coluna] = True

        # Condição de vitória
        if (jogador == "J1" and linha == objetivo) or (jogador == "J2" and linha == objetivo):
            return dist

        # Movimentos possíveis
        if linha > 0 and tabuleiro[linha][coluna].pode_mover_para_cima and not visitado[linha-1][coluna]:
            fila.append((linha-1, coluna, dist+1))
        if linha < num_linhas - 1 and tabuleiro[linha][coluna].pode_mover_para_baixo and not visitado[linha+1][coluna]:
            fila.append((linha+1, coluna, dist+1))
        if coluna > 0 and tabuleiro[linha][coluna].pode_mover_para_esquerda and not visitado[linha][coluna-1]:
            fila.append((linha, coluna-1, dist+1))
        if coluna < num_colunas - 1 and tabuleiro[linha][coluna].pode_mover_para_direita and not visitado[linha][coluna+1]:
            fila.append((linha, coluna+1, dist+1))
    return 99  # Sem caminho

def calcular_utilidade(estado, jogador, tabuleiro=None):
    posicao_j1, posicao_j2, paredes_j1, paredes_j2 = estado
    if tabuleiro is None:
        raise ValueError("O tabuleiro deve ser fornecido para o cálculo do caminho mais curto.")

    j1_path = shortest_path_length("J1", posicao_j1, tabuleiro)
    j2_path = shortest_path_length("J2", posicao_j2, tabuleiro)

    # Um peso maior para a diferença de caminhos força a IA a ser mais estratégica.
    peso_caminho = 2.5
    # Um peso menor para as paredes, usado como critério de desempate.
    peso_parede = 0.1

    if jogador == "J1":
        diff_caminho = j2_path - j1_path
        diff_paredes = paredes_j1 - paredes_j2
    else:  # jogador == "J2"
        diff_caminho = j1_path - j2_path
        diff_paredes = paredes_j2 - paredes_j1

    utilidade = (diff_caminho * peso_caminho) + (diff_paredes * peso_parede)

    return utilidade
