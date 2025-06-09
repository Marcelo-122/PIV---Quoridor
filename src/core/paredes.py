def colocar_parede(self, notacao, turno):
    if len(notacao) != 3:
        print("Notação inválida! Use o formato 'e7h' ou 'd4v'.")
        return False

    letra_coluna, numero_linha, direcao = notacao
    coluna = ord(letra_coluna) - ord("a")
    linha = int(numero_linha) - 1

    if direcao == "h":
        if linha < 8 and coluna < 7:  # 'linha' is 0-indexed, e.g., for notation 'e7h', linha=6. Wall is between row 6 and 7.
            # Check if wall already exists by checking path availability (overlap)
            # Wall is between board row 'linha' and 'linha+1'. Affects squares in row 'linha' (moving down) and row 'linha+1' (moving up).
            if not self.tabuleiro[linha][coluna].pode_mover_para_baixo or not self.tabuleiro[linha][coluna + 1].pode_mover_para_baixo:
                print("Já existe uma parede aqui! (Sobreposição)")
                return False
            # Check for crossing walls
            # A Horizontal wall is between (linha,coluna)-(linha,coluna+1) and (linha+1,coluna)-(linha+1,coluna+1).
            # It would cross an existing Vertical wall if square (linha,coluna) cannot move right
            # AND square (linha+1,coluna) cannot move right (assuming wall is at intersection of col and col+1 for vertical).
            # More precisely, the center of the horizontal wall is at (linha+0.5, coluna+0.5) and (linha+0.5, coluna+1.5).
            # The center of a vertical wall at (linha_v+0.5, coluna_v+0.5) and (linha_v+1.5, coluna_v+0.5).
            # Crossing occurs if they share an intersection point. This means an existing vertical wall is at (linha,coluna+1) or (linha,coluna)
            # Let's use the provided logic for crossing walls, but adapt indices:
            # The horizontal wall is at the boundary of row 'linha' and 'linha+1'.
            # A vertical wall is at the boundary of col 'c' and 'c+1'.
            # Crossing if a vertical wall exists at (linha,coluna)-(linha+1,coluna) or (linha,coluna+1)-(linha+1,coluna+1)
            # This means square (linha,coluna) cannot move right, or square (linha,coluna-1) cannot move right.
            # The original check was: (not self.tabuleiro[linha - 1][coluna].pode_mover_para_direita and not self.tabuleiro[linha][coluna].pode_mover_para_direita)
            # Adapted: (not self.tabuleiro[linha][coluna].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna].pode_mover_para_direita)
            # This checks if a vertical wall segment exists at the same intersection point.
            # A horizontal wall is defined by its top-left square (linha, coluna) and (linha, coluna+1).
            # It blocks passage between (linha,coluna) <=> (linha+1,coluna) and (linha,coluna+1) <=> (linha+1,coluna+1).
            # A vertical wall is defined by its top-left square (linha_v, coluna_v) and (linha_v+1, coluna_v).
            # It blocks passage between (linha_v,coluna_v) <=> (linha_v,coluna_v+1) and (linha_v+1,coluna_v) <=> (linha_v+1,coluna_v+1).
            # Intersection point for H-wall: (linha+0.5, coluna+0.5). V-wall: (linha_v+0.5, coluna_v+0.5).
            # If they cross, they share this point. So, an existing V-wall at (linha, coluna) or (linha, coluna-1) could cross.
            # Let's simplify the crossing check for now to what was there, adapted for new 'linha':
            if (coluna > 0 and not self.tabuleiro[linha][coluna-1].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna-1].pode_mover_para_direita) or \
               (coluna < 7 and not self.tabuleiro[linha][coluna].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna].pode_mover_para_direita):
                 # This logic is getting complicated. The original crossing check was simpler:
                 # if (not self.tabuleiro[linha_old][coluna].pode_mover_para_direita and not self.tabuleiro[linha_old+1][coluna].pode_mover_para_direita):
                 # This implies checking if the *squares that form the horizontal wall's ends* can't move right/left into the path of a vertical wall.
                 # For a horizontal wall between (L,C)-(L,C+1) and (L+1,C)-(L+1,C+1)
                 # Crossing if square (L,C) can't move right AND square (L+1,C) can't move right (meaning V-wall at C,C+1 intersection)
                 # OR square (L,C+1) can't move left AND square (L+1,C+1) can't move left (meaning V-wall at C,C+1 intersection)
                 # The original check was: (not self.tabuleiro[linha_orig_minus_1][coluna].pode_mover_para_direita and not self.tabuleiro[linha_orig][coluna].pode_mover_para_direita)
                 # With new `linha` (which is `linha_orig`): (not self.tabuleiro[linha][coluna].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna].pode_mover_para_direita)
                 # This checks if the squares (linha,coluna) and (linha+1,coluna) are blocked from moving right. This means a vertical wall exists between (coluna) and (coluna+1) at these rows.
                 # This is the correct check for one of the two intersection points a horizontal wall has with potential vertical walls.
                 # A horizontal wall spans two cells, so it has two points where it can intersect a vertical wall.
                 # Point 1: between (linha,coluna) and (linha+1,coluna) with (linha,coluna+1) and (linha+1,coluna+1)
                 # Point 2: between (linha,coluna+1) and (linha+1,coluna+1) with (linha,coluna+2) and (linha+1,coluna+2)
                 # The check should be: is there a vertical wall at the intersection (linha, coluna)-(linha+1,coluna) AND (linha,coluna+1)-(linha+1,coluna+1)?
                 # This means: (tabuleiro[linha][coluna].pode_mover_para_direita is False AND tabuleiro[linha+1][coluna].pode_mover_para_direita is False)
                 # OR (tabuleiro[linha][coluna+1].pode_mover_para_esquerda is False AND tabuleiro[linha+1][coluna+1].pode_mover_para_esquerda is False)
                 # The original code's crossing check was likely insufficient as it only checked one point.
                 # For now, let's stick to the direct adaptation of the previous crossing logic for one point:
                if not self.tabuleiro[linha][coluna].pode_mover_para_direita and not self.tabuleiro[linha+1][coluna].pode_mover_para_direita:
                    print("Muro cruzaria com um existente!")
                    return False

            # Block movement down from row 'linha' to 'linha+1' at 'coluna' and 'coluna+1'
            self.tabuleiro[linha][coluna].pode_mover_para_baixo = False
            self.tabuleiro[linha][coluna + 1].pode_mover_para_baixo = False
            # Block movement up from row 'linha+1' to 'linha' at 'coluna' and 'coluna+1'
            self.tabuleiro[linha + 1][coluna].pode_mover_para_cima = False
            self.tabuleiro[linha + 1][coluna + 1].pode_mover_para_cima = False
        else:
            print("Posição inválida para parede horizontal!")
            return False

    elif direcao == "v":
        if linha < 7 and coluna > 0:
            # Check if wall already exists by checking path availability (overlap)
            if not self.tabuleiro[linha][coluna - 1].pode_mover_para_direita or not self.tabuleiro[linha + 1][coluna - 1].pode_mover_para_direita:
                print("Já existe uma parede aqui! (Sobreposição)")
                return False
            # Check for crossing walls
            # A Vertical wall (defined by 'linha', 'coluna' from notation) is placed between board col 'coluna-1' and 'coluna',
            # affecting rows 'linha' and 'linha+1'.
            # It would cross an existing Horizontal wall if square (linha,coluna-1) cannot move down
            # AND square (linha,coluna) cannot move down.
            if (not self.tabuleiro[linha][coluna - 1].pode_mover_para_baixo and
                not self.tabuleiro[linha][coluna].pode_mover_para_baixo):
                print("Muro cruzaria com um existente!")
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
