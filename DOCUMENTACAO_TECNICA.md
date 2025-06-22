# 📋 DOCUMENTAÇÃO TÉCNICA - NAVEGADOR OSM
## Sistema de Visualização e Manipulação de Grafos

---

## 1. ESPECIFICAÇÃO DE REQUISITOS

### 1.1 Objetivo do Sistema
Desenvolver uma aplicação desktop para visualização, manipulação e análise de grafos com suporte a dados do OpenStreetMap (OSM), implementando algoritmos de roteamento e oferecendo interface gráfica intuitiva.

### 1.2 Requisitos Funcionais

#### RF01 – Importar mapas reais (arquivos .osm) e converter para grafos
- **Descrição**: Sistema permite importar arquivos OSM contendo dados reais de mapas
- **Implementação**: `GraphManager.importar_osm()` e `GraphOperations.importar_osm()`

#### RF02 – Enumerar vértices e rotular arestas com pesos (distâncias)
- **Descrição**: Numeração automática de vértices e exibição de pesos nas arestas
- **Implementação**: `GraphManager.obter_proximo_id_vertice()` e toggle "Exibir Distâncias"

#### RF03 – Seleção de vértices de origem e destino com marcação visual
- **Descrição**: Sistema de seleção visual com cores diferenciadas
- **Implementação**: `SelectionManager` com cores Verde (origem) e Vermelho (destino)

#### RF04 – Calcular e exibir rota do menor caminho entre dois vértices
- **Descrição**: Implementação do algoritmo de Dijkstra com visualização do caminho
- **Implementação**: `Dijkstra.py` com renderização em vermelho (#ff3333)

#### RF05 – Criação e edição de grafos com interface gráfica
- **Descrição**: Modo de edição completo com clique do mouse
- **Implementação**: `EventManager._processar_clique_edicao()` para adicionar/remover vértices e arestas

#### RF06 – Suporte a diferentes tipos de grafos (ponderado, direcionado/não direcionado)
- **Descrição**: Suporte a grafos ponderados e vias de mão única/dupla
- **Implementação**: Detecção de `oneway` attribute com cores diferenciadas

#### RF07 – Exibir estatísticas sobre execução do algoritmo
- **Descrição**: Sistema de estatísticas de execução
- **Implementação**: `Dijkstra.get_estatisticas()` com tempo, nós explorados e custo total

#### RF08 – Copiar imagem do grafo para área de transferência
- **Descrição**: Funcionalidade de captura e cópia de imagem
- **Implementação**: `ImageManager.copiar_imagem()` com `ImageGrab`

### 1.3 Requisitos Não Funcionais

#### RNF01 – Vértices e arestas com cores distintas
- **Implementação**: Vértices em cinza claro, arestas em cinza médio, caminho em vermelho

#### RNF02 – Diferenciar vias de mão única e mão dupla
- **Implementação**: Mão única em azul (#2196f3), mão dupla em laranja (#ff9800)

#### RNF03 – Otimização para grandes grafos
- **Implementação**: Dijkstra com heap binário O((V+E) log V)

#### RNF04 – Tempo de resposta inferior a 2 segundos para grafos médios
- **Implementação**: Algoritmo otimizado com métricas de performance

#### RNF05 – Interface intuitiva e fácil manipulação
- **Implementação**: Design responsivo com tooltips e feedback visual

#### RNF06 – Suporte aos sistemas Windows e Linux
- **Implementação**: Testado em Windows 10/11 e Ubuntu 18.04+

---

## 2. ARQUITETURA DO SISTEMA

### 2.1 Visão Geral
O sistema segue uma arquitetura **modular baseada em componentes**:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   INTERFACE     │    │   GERENCIADORES │    │   CORE LOGIC    │
│   (UI Layer)    │◄──►│   (Managers)    │◄──►│      (Core)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 Camadas da Arquitetura

#### 2.2.1 Camada de Interface (UI Layer)
- `MapaTkinter.py` - Classe principal da aplicação
- `Sidebar.py` - Painel lateral de controles
- `ActionPanel.py` - Painel de ações
- `ZoomPanel.py` - Controles de navegação
- `HistoryPanel.py` - Painel de histórico
- `EventManager.py` - Processamento de eventos
- `UIManager.py` - Gerenciamento de estado da interface
- `ViewManager.py` - Gerenciamento de visualização

#### 2.2.2 Camada de Gerenciadores (Managers Layer)
- `HistoryManager.py` - Gerenciamento de histórico
- `ImageManager.py` - Gerenciamento de imagens

#### 2.2.3 Camada Core (Core Layer)
- `GraphManager.py` - Gerenciamento de grafos
- `GraphOperations.py` - Operações de alto nível
- `Dijkstra.py` - Algoritmo de roteamento
- `GraphDrawer.py` - Renderização de grafos
- `SelectionManager.py` - Gerenciamento de seleção

### 2.3 Padrões de Design Utilizados

#### 2.3.1 Manager Pattern
- Todos os gerenciadores centralizam responsabilidades específicas

#### 2.3.2 Delegate Pattern
- MapaTkinter delega operações para gerenciadores especializados

#### 2.3.3 Observer Pattern
- EventManager observa mudanças no canvas

#### 2.3.4 Strategy Pattern
- Diferentes algoritmos de renderização em GraphDrawer

---

## 3. IMPLEMENTAÇÃO

### 3.1 Tecnologias Utilizadas
- **Python 3.9+**: Linguagem principal
- **Tkinter**: Framework de interface gráfica
- **OSMNX 1.8.1**: Manipulação de dados OSM
- **NetworkX 3.2.1**: Análise de grafos
- **Pillow 10.2.0**: Processamento de imagens

### 3.2 Estrutura de Arquivos

```
CursorAED/
├── main.py                    # Ponto de entrada
├── core/                      # Lógica de negócio
│   ├── GraphManager.py       # Gerenciamento de grafos
│   ├── GraphDrawer.py        # Renderização
│   ├── Dijkstra.py           # Algoritmo de roteamento
│   ├── GraphOperations.py    # Operações de alto nível
│   └── SelectionManager.py   # Gerenciamento de seleção
├── ui/                        # Interface gráfica
│   ├── MapaTkinter.py        # Classe principal
│   ├── Sidebar.py            # Painel lateral
│   ├── ActionPanel.py        # Painel de ações
│   ├── ZoomPanel.py          # Controles de zoom
│   ├── HistoryPanel.py       # Painel de histórico
│   ├── EventManager.py       # Processamento de eventos
│   ├── UIManager.py          # Gerenciamento de UI
│   └── ViewManager.py        # Gerenciamento de visualização
├── managers/                  # Gerenciadores
│   ├── HistoryManager.py     # Gerenciamento de histórico
│   └── ImageManager.py       # Gerenciamento de imagens
└── assets/                    # Recursos
    └── capturas/             # Imagens salvas
```

### 3.3 Estrutura de Dados

#### 3.3.1 Grafo (NetworkX)
```python
grafo = nx.Graph()  # Grafo não direcionado
# ou
grafo = nx.DiGraph()  # Grafo direcionado
```

#### 3.3.2 Nó (Node)
```python
node_data = {
    'x': float,           # Coordenada X (longitude)
    'y': float,           # Coordenada Y (latitude)
    'osmid': int,         # ID OSM (se importado)
    'highway': str,       # Tipo de via (se OSM)
}
```

#### 3.3.3 Aresta (Edge)
```python
edge_data = {
    'weight': float,      # Peso (distância em metros)
    'highway': str,       # Tipo de via (se OSM)
    'oneway': bool,       # Via de mão única
    'osmid': int,         # ID OSM (se importado)
}
```