# Sistema de Navegação Primitivo

Este é um sistema de navegação que implementa o algoritmo de Dijkstra para encontrar o caminho mais curto entre dois pontos em um grafo.

## Requisitos

- Python 3.8 ou superior
- Bibliotecas Python listadas em `requirements.txt`

## Instalação

1. Clone este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o programa:
```bash
python navegacao.py
```

2. Use o botão "Importar Mapa" para carregar um arquivo de mapa no formato .txt
3. O arquivo de mapa deve estar no formato:
```
origem destino peso
```
Por exemplo:
```
A B 10
B C 5
C D 8
```

4. Após importar o mapa, você pode:
   - Selecionar origem e destino clicando nos vértices
   - Calcular a rota mais curta usando o botão "Calcular Rota"
   - Visualizar estatísticas de execução

## Funcionalidades

- Importação de mapas reais
- Visualização de grafos com pesos
- Cálculo do caminho mais curto usando Dijkstra
- Estatísticas de execução
- Interface gráfica intuitiva 