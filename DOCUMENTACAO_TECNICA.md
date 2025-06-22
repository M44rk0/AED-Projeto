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
- **Restrição**: Botão habilitado apenas para grafos criados manualmente

#### RF03 – Seleção de vértices de origem e destino com marcação visual
- **Descrição**: Sistema de seleção visual com cores diferenciadas
- **Implementação**: `SelectionManager` com cores Verde (origem) e Vermelho (destino)

#### RF04 – Calcular e exibir rota do menor caminho entre dois vértices
- **Descrição**: Implementação do algoritmo de Dijkstra com visualização do caminho
- **Implementação**: `Dijkstra.py` com renderização em vermelho (#ff3333)

#### RF05 – Criação e edição de grafos com interface gráfica
- **Descrição**: Modo de edição completo com clique do mouse
- **Implementação**: `EventManager._processar_clique_edicao()` para adicionar/remover vértices e arestas
- **Controle**: Botão "Gerar Arestas" habilitado apenas com 2+ vértices

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

#### RNF01 – Os vértices e as arestas do grafo devem ter cores distintas
- **Implementação**: Vértices em cinza claro (245,245,245,200), arestas em cinza médio (#77787C)

#### RNF02 – Diferenciar aresta representativa de via de mão única da aresta de via de mão dupla
- **Implementação**: Mão única em azul (#2196f3), mão dupla em laranja (#ff9800)

#### RNF03 – A execução do programa deve ser otimizada para grandes grafos (milhares de vértices e arestas)
- **Implementação**: Dijkstra com heap binário O((V+E) log V), renderização otimizada com supersampling

#### RNF04 – O tempo de resposta para cálculos deve ser inferior a 2 segundos para grafos médios (~500 nós)
- **Implementação**: Algoritmo otimizado com métricas de performance e heap binário

#### RNF05 – Uso eficiente de memória para evitar sobrecarga em grafos extensos
- **Implementação**: Gerenciamento otimizado de imagens, limpeza automática de recursos

#### RNF06 – Interface intuitiva e de fácil manipulação para usuários não técnicos
- **Implementação**: Design responsivo com tooltips, feedback visual e controles contextuais

#### RNF07 – Suporte aos sistemas operacionais Windows ou Linux
- **Implementação**: Testado em Windows 10/11 e Ubuntu 18.04+, uso de bibliotecas cross-platform

#### RNF08 – Código modular e bem documentado para facilitar a manutenção
- **Implementação**: Arquitetura modular com separação clara de responsabilidades, documentação completa

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
- `ZoomPanTool.py` - Ferramentas de zoom e pan

#### 2.2.2 Camada de Gerenciadores (Managers Layer)
- `EventManager.py` - Gerenciamento de eventos
- `UIManager.py` - Gerenciamento de estado da interface e controle contextual
- `ViewManager.py` - Gerenciamento de visualização
- `ToggleManager.py` - Gerenciamento de toggles
- `TooltipManager.py` - Gerenciamento de tooltips
- `HistoryManager.py` - Gerenciamento de histórico com numeração sequencial
- `ImageManager.py` - Gerenciamento de imagens

#### 2.2.3 Camada Core (Core Layer)
- `GraphManager.py` - Gerenciamento de grafos com detecção de tipos
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

#### 2.3.5 State Pattern
- UIManager gerencia estados dos botões baseado no contexto

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
MapaAED/
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
│   └── ZoomPanTool.py        # Ferramentas de zoom e pan
├── managers/                  # Gerenciadores
│   ├── EventManager.py       # Gerenciamento de eventos
│   ├── UIManager.py          # Gerenciamento de UI e estados
│   ├── ViewManager.py        # Gerenciamento de visualização
│   ├── ToggleManager.py      # Gerenciamento de toggles
│   ├── TooltipManager.py     # Gerenciamento de tooltips
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

### 3.4 Sistema de Controle de Estados

#### 3.4.1 Detecção de Tipo de Grafo
```python
def eh_grafo_osm(self):
    """Detecta se o grafo foi importado do OSM"""
    # Verifica atributos OSM nos nós e arestas
    for _, data in self.grafo.nodes(data=True):
        if 'osmid' in data:
            return True
    for _, _, data in self.grafo.edges(data=True):
        if 'highway' in data or 'osmid' in data or 'geometry' in data:
            return True
    return False
```

#### 3.4.2 Controle Contextual de Botões
```python
def atualizar_estado_botoes(self):
    """Atualiza o estado de todos os botões baseado no contexto"""
    grafo_osm = self.main_app.graph_manager.eh_grafo_osm()
    tem_grafo_valido = self.main_app.graph_manager.existe_grafo()
    
    # Controle específico para cada tipo de botão
    self.main_app.sidebar.configurar_estado_distancias(not grafo_osm and tem_grafo_valido)
    self.main_app.sidebar.habilitar_botoes_edicao(True)  # Com validação interna
```

#### 3.4.3 Validação de Vértices para Geração de Arestas
```python
def habilitar_botoes_edicao(self, habilitar=True):
    """Habilita ou desabilita os botões de edição com validação"""
    estado = tk.NORMAL if habilitar else tk.DISABLED
    self.buttons['gerar_vertices'].config(state=estado)
    
    # Validação específica para gerar arestas
    if habilitar and self.main_app.graph_manager.existe_grafo():
        tem_vertices_suficientes = len(self.main_app.graph_manager.grafo.nodes) >= 2
        estado_arestas = tk.NORMAL if tem_vertices_suficientes else tk.DISABLED
    else:
        estado_arestas = estado
    self.buttons['gerar_arestas'].config(state=estado_arestas)
```

### 3.5 Sistema de Capturas

#### 3.5.1 Títulos Simplificados
```python
def atualizar_historico(self):
    """Atualiza o histórico com numeração sequencial"""
    for i, info in enumerate(historico_completo, 1):
        if info['tipo'] == 'captura':
            tk.Label(inner, text=f"Captura {len(historico_completo)-i+1}.", 
                   bg="#262a2f", fg="#00ffcc", font=("Segoe UI", 11, "bold"))
```

### 3.6 Cálculo de Distâncias

#### 3.6.1 Para Grafos OSM
```python
def calcular_distancia(self, lat1, lon1, lat2, lon2):
    """Calcula distância usando fórmula de Haversine"""
    R = 6371000  # Raio da Terra em metros
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c
```

#### 3.6.2 Para Grafos Manuais
```python
# Usa o peso salvo na aresta (weight attribute)
peso = data.get('weight', 0)
txt = f"{peso:.0f}m"
```

---

## 4. ALGORITMOS IMPLEMENTADOS

### 4.1 Algoritmo de Dijkstra
- **Complexidade**: O((V+E) log V) com heap binário
- **Implementação**: `Dijkstra.py`
- **Funcionalidades**: Cálculo de menor caminho, estatísticas de performance

### 4.2 Detecção de Tipo de Grafo
- **Implementação**: `GraphManager.eh_grafo_osm()`
- **Critérios**: Presença de atributos OSM (osmid, highway, geometry)

### 4.3 Sistema de Estados da Interface
- **Implementação**: `UIManager.atualizar_estado_botoes()`
- **Funcionalidades**: Controle contextual de botões baseado no estado atual

---

## 5. TESTES E VALIDAÇÃO

### 5.1 Testes de Funcionalidade
- Importação de arquivos OSM
- Criação manual de grafos
- Cálculo de rotas com Dijkstra
- Controle de estados da interface

### 5.2 Testes de Performance
- Grafos com até 10.000 vértices
- Tempo de resposta < 2 segundos para grafos médios
- Uso de memória otimizado

### 5.3 Testes de Usabilidade
- Interface intuitiva e responsiva
- Feedback visual adequado
- Controles contextuais funcionais

---

## 6. CONCLUSÕES

O sistema implementa com sucesso todos os requisitos funcionais e não funcionais especificados, oferecendo uma interface robusta e intuitiva para visualização e manipulação de grafos. As funcionalidades de controle contextual e detecção automática de tipos de grafo melhoram significativamente a experiência do usuário.