class Square:
    def __init__(self):
        # Disponibilidade do caminho: True se o movimento é permitido nessa direção
        self.pode_mover_para_cima = True
        self.pode_mover_para_baixo = True
        self.pode_mover_para_esquerda = True
        self.pode_mover_para_direita = True
        # Indica se um jogador está atualmente nesse quadrado
        self.tem_jogador = False

    def __repr__(self):
        return (f"Square(U:{self.pode_mover_para_cima}, D:{self.pode_mover_para_baixo}, "
                f"L:{self.pode_mover_para_esquerda}, R:{self.pode_mover_para_direita}, "
                f"P:{self.tem_jogador})")
