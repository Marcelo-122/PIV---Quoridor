from quoridor.game import JogoQuoridor

# Início do jogo
jogo = JogoQuoridor()
game_over = False
turn = 0  # 0 = Player 1, 1 = Player 2

while not game_over:
    jogo.imprimir_tabuleiro()
    
    player = "Player 1" if turn == 0 else "Player 2"
    print(f"Turno atual: {player}")

    tipo_jogada = input("Escolha: Andar (2) ou Colocar Parede (1)? ")

    if tipo_jogada == "1":
        parede_input = input("Digite a posição da parede (ex: e7h): ")
        if not jogo.colocar_parede(parede_input, turn):
            continue  

    elif tipo_jogada == "2":
        movimento_input = input("Digite o movimento (ex: w, a, s, d): ")
        if not jogo.andar(movimento_input, turn):
            continue  

    else:
        print("Entrada inválida. Escolha 1 (Parede) ou 2 (Andar).")
        continue

    if jogo.verificar_vitoria():
        game_over = True


    print(jogo.serializar_estado())
    print(jogo.calcular_utilidade(jogo.serializar_estado(),"J1"))
    print(jogo.calcular_utilidade(jogo.serializar_estado(),"J2"))

    turn = (turn + 1) % 2