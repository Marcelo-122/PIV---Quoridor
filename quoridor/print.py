def imprimir_tabuleiro(self):
    print("   " + " ".join(f" {chr(97 + i)} " for i in range(9)))

    for linha in range(9):
        linha_str = f"{linha + 1} "
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
                if coluna < 8 and (
                    self.paredes_horizontais[linha][coluna]
                    or self.paredes_verticais[linha][coluna]
                ):
                    linha_paredes += "┼"
                else:
                    linha_paredes += " "
            print(linha_paredes)
