import copy


# Minimax com poda alfa-beta e tabela de transposição
def minimax_alfabeta(
    jogo,
    profundidade,
    turno_max,
    jogador,
    transposition_table,
    gerar_movimentos_possiveis,
    criar_move_info,
    aplicar_movimento,
    atualizar_move_info,
    hash_estado,
    profundidade_maxima=4,
    alfa=float("-inf"),
    beta=float("inf"),
):
    """
    Implementação do algoritmo Minimax com poda alfa-beta e tabela de transposição.

    Args:
        jogo: Estado atual do jogo
        profundidade: Profundidade atual da busca
        turno_max: Se True, é o turno do jogador MAX; se False, é o turno do jogador MIN
        jogador: Jogador para o qual calcular a utilidade ('J1' ou 'J2')
        transposition_table: Tabela de transposição para armazenar estados já calculados
        gerar_movimentos_possiveis: Função para gerar movimentos possíveis
        criar_move_info: Função para criar informações sobre o movimento
        aplicar_movimento: Função para aplicar um movimento ao jogo
        atualizar_move_info: Função para atualizar informações do movimento
        hash_estado: Função para gerar um hash do estado do jogo
        profundidade_maxima: Profundidade máxima de busca
        alfa: Valor alfa para poda alfa-beta
        beta: Valor beta para poda alfa-beta

    Returns:
        Valor da utilidade do estado atual
    """
    # Verifica a tabela de transposição
    estado = jogo.serializar_estado()
    estado_hash = hash_estado(estado)

    if estado_hash in transposition_table:
        prof_armazenada, valor, _ = transposition_table[estado_hash]
        if prof_armazenada >= profundidade:
            return valor

    # Se o jogo acabou ou se a profundidade é máxima
    if jogo.verificar_vitoria() or profundidade == 0:
        valor = jogo.calcular_utilidade(estado, jogador)
        transposition_table[estado_hash] = (profundidade, valor, None)
        return valor

    melhor_movimento = None

    if turno_max:  # turno do MAX
        valor = float("-inf")
        for movimento in gerar_movimentos_possiveis(jogo, 0 if jogador == "J1" else 1):
            jogo_copia = copy.deepcopy(jogo)
            move_info = criar_move_info(
                jogo_copia, movimento, 0 if jogador == "J1" else 1
            )
            aplicar_movimento(jogo_copia, movimento, 0 if jogador == "J1" else 1)
            move_info = atualizar_move_info(
                jogo_copia, move_info, 0 if jogador == "J1" else 1
            )

            # Use the direct result from the recursive call
            eval_do_filho = minimax_alfabeta(
                jogo_copia,
                profundidade - 1,
                False,  # Turno do MIN
                jogador,
                transposition_table,
                gerar_movimentos_possiveis,
                criar_move_info,
                aplicar_movimento,
                atualizar_move_info,
                hash_estado,
                profundidade_maxima,
                alfa,
                beta,
            )

            if eval_do_filho > valor:
                valor = eval_do_filho
                melhor_movimento = movimento

            alfa = max(alfa, valor)
            if beta <= alfa:
                break  # Poda beta

        # Armazena na tabela de transposição
        transposition_table[estado_hash] = (profundidade, valor, melhor_movimento)
        return valor
    else:  # turno no MIN
        valor = float("inf")
        oponente = "J2" if jogador == "J1" else "J1"
        for movimento in gerar_movimentos_possiveis(jogo, 0 if oponente == "J1" else 1):
            jogo_copia = copy.deepcopy(jogo)
            move_info = criar_move_info(
                jogo_copia, movimento, 0 if oponente == "J1" else 1
            )
            aplicar_movimento(jogo_copia, movimento, 0 if oponente == "J1" else 1)
            move_info = atualizar_move_info(
                jogo_copia, move_info, 0 if oponente == "J1" else 1
            )

            # Use the direct result from the recursive call
            eval_do_filho = minimax_alfabeta(
                jogo_copia,
                profundidade - 1,
                True,  # Turno do MAX
                jogador,
                transposition_table,
                gerar_movimentos_possiveis,
                criar_move_info,
                aplicar_movimento,
                atualizar_move_info,
                hash_estado,
                profundidade_maxima,
                alfa,
                beta,
            )

            if eval_do_filho < valor:
                valor = eval_do_filho
                melhor_movimento = movimento

            beta = min(beta, valor)
            if beta <= alfa:
                break  # Poda alfa

        # Armazena na tabela de transposição
        transposition_table[estado_hash] = (profundidade, valor, melhor_movimento)
        return valor


# Encontrar o melhor movimento do computador usando minimax com poda alfa-beta (retorna também o valor)
def melhor_jogada_agente_poda_com_valor(
    jogo,
    turno,
    profundidade_maxima,
    transposition_table,
    gerar_movimentos_possiveis,
    criar_move_info,
    aplicar_movimento,
    atualizar_move_info,
    hash_estado,
):
    """
    Encontra o melhor movimento para o jogador atual usando minimax com poda alfa-beta.

    Args:
        jogo: Estado atual do jogo
        turno: Turno atual (0 para J1, 1 para J2)
        profundidade_maxima: Profundidade máxima de busca
        transposition_table: Tabela de transposição para armazenar estados já calculados
        gerar_movimentos_possiveis: Função para gerar movimentos possíveis
        criar_move_info: Função para criar informações sobre o movimento
        aplicar_movimento: Função para aplicar um movimento ao jogo
        atualizar_move_info: Função para atualizar informações do movimento
        hash_estado: Função para gerar um hash do estado do jogo

    Returns:
        Tupla (melhor_jogada, valor) com o melhor movimento encontrado e seu valor
    """
    jogador = "J1" if turno == 0 else "J2"
    melhor_valor = float("-inf")
    melhor_jogada = None
    alfa = float("-inf")
    beta = float("inf")

    for movimento in gerar_movimentos_possiveis(
        jogo, turno, transposition_table=transposition_table
    ):
        jogo_copia = copy.deepcopy(jogo)
        move_info = criar_move_info(jogo_copia, movimento, turno)
        aplicar_movimento(jogo_copia, movimento, turno)
        move_info = atualizar_move_info(jogo_copia, move_info, turno)

        # Use the direct result from the minimax_alfabeta call
        valor_do_movimento = minimax_alfabeta(
            jogo_copia,
            profundidade_maxima - 1,
            False,  # Após o MAX jogar, é a vez do MIN
            jogador,
            transposition_table,
            gerar_movimentos_possiveis,
            criar_move_info,
            aplicar_movimento,
            atualizar_move_info,
            hash_estado,
            profundidade_maxima,
            alfa,
            beta,
        )

        if valor_do_movimento > melhor_valor:
            melhor_valor = valor_do_movimento
            melhor_jogada = movimento

        alfa = max(alfa, melhor_valor)
        # Não há poda beta aqui, pois este é o nível raiz para o jogador MAX

    # Armazena o resultado da raiz na tabela de transposição se necessário
    return melhor_jogada, melhor_valor
