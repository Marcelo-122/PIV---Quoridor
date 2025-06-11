def visualizar_tabuleiro(jogo):
    """Cria uma representação visual do tabuleiro para depuração"""
    linhas = jogo.linhas
    colunas = jogo.colunas
    tabuleiro = [["." for _ in range(colunas)] for _ in range(linhas)]

    # Marcar jogadores
    j1_lin, j1_col = jogo.jogadores["J1"]
    j2_lin, j2_col = jogo.jogadores["J2"]
    tabuleiro[j1_lin][j1_col] = "1"
    tabuleiro[j2_lin][j2_col] = "2"

    # Detectar paredes horizontais e verticais a partir do tabuleiro
    # Paredes horizontais: quadrados que não permitem movimento para baixo
    for lin in range(linhas - 1):
        for col in range(colunas):
            if not jogo.tabuleiro[lin][col].pode_mover_para_baixo:
                if col < colunas - 1:  # Marcamos dois caracteres para cada parede
                    tabuleiro[lin][col] = "-"
                    if col + 1 < colunas:
                        tabuleiro[lin][col + 1] = "-"

    # Paredes verticais: quadrados que não permitem movimento para direita
    for lin in range(linhas):
        for col in range(colunas - 1):
            if not jogo.tabuleiro[lin][col].pode_mover_para_direita:
                if lin < linhas - 1:  # Marcamos dois caracteres para cada parede
                    tabuleiro[lin][col] = "|"
                    if lin + 1 < linhas:
                        tabuleiro[lin + 1][col] = "|"

    # Construir string de saída
    output = []
    for i, linha in enumerate(tabuleiro):
        output.append(f"{i} " + " ".join(linha))
    output.append("  " + " ".join(str(i) for i in range(colunas)))
    return "\n".join(output)
