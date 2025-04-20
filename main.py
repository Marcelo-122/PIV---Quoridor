from quoridor.game import JogoQuoridor
from quoridor.caminho import existe_caminho

# Início do jogo
jogo = JogoQuoridor()
turno = 0  # 0 = Jogador 1, 1 = Jogador 2
jogo_terminado = False

while not jogo_terminado:
    jogo.imprimir_tabuleiro()
    
    jogador_nome = "Jogador 1" if turno == 0 else "Jogador 2"
    print(f"Turno atual: {jogador_nome}")

    tipo_jogada = input("Escolha: Andar (2) ou Colocar Parede (1)? ")

    if tipo_jogada == "1":
        parede_input = input("Digite a posição da parede (ex: e7h): ")
        if not jogo.colocar_parede(parede_input, turno):
            if not existe_caminho('J1', jogo.jogadores['J1'][0], jogo.jogadores['J1'][1], jogo.tabuleiro):
                print("Movimento inválido: J1 ficaria preso.")
                continue  

    elif tipo_jogada == "2":
        movimento_input = input("Digite o movimento (ex: w, a, s, d): ")
        if not jogo.andar(movimento_input, turno):
            if not existe_caminho('J2', jogo.jogadores['J2'][0], jogo.jogadores['J2'][1], jogo.tabuleiro):
                print("Movimento inválido: J2 ficaria preso.")
                continue  

    else:
        print("Entrada inválida. Escolha 1 (Parede) ou 2 (Andar).")
        continue

    if jogo.verificar_vitoria():
        jogo_terminado = True
        
    print(jogo.calcular_utilidade(jogo.serializar_estado(),"J1"))
    print(jogo.calcular_utilidade(jogo.serializar_estado(),"J2"))

    turno = (turno + 1) % 2