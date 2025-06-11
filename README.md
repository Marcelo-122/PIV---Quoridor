# Quoridor

Este é um projeto de implementação do jogo Quoridor com inteligência artificial avançada. O projeto inclui um agente AI que utiliza o algoritmo minimax com poda alfa-beta, e outro agente com q-learning entre outras otimizações.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
PIV---Quoridor/
├── .git/
├── .gitignore
├── .venv/
├── __init__.py
├── main.py
├── gui/
│   ├── __init__.py
│   └── quoridor_gui.py
├── src/
│   ├── __init__.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── iterative_deepening.py
│   │   ├── minimax.py
│   │   └── minimax_core.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── caminho.py
│   │   ├── constantes.py
│   │   ├── game.py
│   │   ├── movimento_util.py
│   │   ├── movimentos.py
│   │   ├── paredes.py
│   │   ├── square.py
│   │   └── utilidade.py
│   └── utils/
│       ├── __init__.py
│       └── print.py
└── README.md
└── requirements.txt
```

## Funcionalidades

- **Minimax com poda alfa-beta**: Implementação do algoritmo minimax otimizado para o jogo Quoridor.
- **Tabela de transposição**: Utilizada para cachear estados e melhorar a eficiência.
- **Ordenação de movimentos**: Para um corte mais eficiente durante a poda.
- **Otimização de primeiro movimento**: Usando movimentos de abertura predefinidos.
- **Deepening iterativo**: Para busca limitada por tempo.
- **Função de utilidade sofisticada**: Considera comprimentos de caminho, contagem de paredes e qualidade de movimento.
- **Q-Learning Tabular**: Implementação do algoritmo Q-Learning otimizado para o jogo Quoridor.

## Requisitos

- Python 3.x
- Numpy 1.24.4

## Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/Marcelo-122/PIV---Quoridor.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o jogo:
   ```bash
   python main.py
   ```

## Contribuição

Sinta-se à vontade para contribuir com o projeto. Para isso, faça um fork do repositório, crie uma nova branch para suas alterações e envie um pull request.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
