# 🗺️ Navegador OSM - Visualizador de Grafos

Aplicativo desktop para visualização e manipulação de grafos, com suporte a dados OSM (OpenStreetMap) e algoritmo de Dijkstra.

## 🚀 Como Executar

### Pré-requisitos
- **Python 3.7+**
- **Windows, macOS ou Linux**
- **4GB RAM**

### Instalação
```bash
# Clone o repositório
git clone <https://github.com/M44rk0/AED-Projeto>
cd AED-Projeto

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
python main.py
```

## 📁 Estrutura do Projeto

```
MapaAED/
├── main.py                 # Ponto de entrada
├── core/                   # Lógica principal
│   ├── GraphManager.py     # Gerenciamento de grafos
│   ├── GraphDrawer.py      # Renderização
│   ├── Dijkstra.py         # Algoritmo de Dijkstra
│   ├── GraphOperations.py  # Operações de grafo
│   └── SelectionManager.py # Gerenciamento de seleção
├── ui/                     # Interface gráfica
│   ├── MapaTkinter.py      # Janela principal
│   ├── Sidebar.py          # Painel lateral
│   ├── ActionPanel.py      # Painel de ações
│   ├── ZoomPanel.py        # Controles de zoom
│   ├── HistoryPanel.py     # Painel de histórico
│   └── ZoomPanTool.py      # Ferramentas de zoom e pan
├── managers/               # Gerenciadores
│   ├── EventManager.py     # Gerenciamento de eventos
│   ├── UIManager.py        # Gerenciamento de UI
│   ├── ViewManager.py      # Gerenciamento de visualização
│   ├── ToggleManager.py    # Gerenciamento de toggles
│   ├── TooltipManager.py   # Gerenciamento de tooltips
│   ├── ImageManager.py     # Gerenciamento de imagens
│   └── HistoryManager.py   # Gerenciamento de histórico
└── assets/                 # Recursos
    └── capturas/           # Imagens salvas
```

## 🎯 Funcionalidades

### 📂 Importação de Dados
- **Arquivos OSM (.osm)** - Importação de mapas reais
- **Criação Manual** - Construção de grafos do zero
- **Geração Aleatória** - Vértices e arestas automáticas

### 🎨 Visualização
- **Zoom e Pan** - Navegação intuitiva
- **Cores Personalizadas** - Diferenciação de tipos de rua
- **Exibição de Distâncias** - Pesos das arestas (apenas para grafos criados manualmente)

### 🧮 Algoritmo de Dijkstra
- **Cálculo de Rota** - Caminho mais curto entre dois pontos
- **Estatísticas** - Tempo de execução e nós explorados
- **Histórico** - Salvamento de rotas calculadas

### 🖥️ Interface
- **Design Moderno** - Interface responsiva
- **Tooltips** - Dicas contextuais
- **Captura de Imagens** - Salvamento e cópia com títulos simplificados
- **Modo de Edição** - Criação de grafos
- **Controles Inteligentes** - Botões habilitados/desabilitados conforme contexto

## 📚 Guia de Uso

### 1. Importar Mapa OSM
- Clique em "📂 Importar OSM"
- Selecione um arquivo .osm
- O mapa será carregado automaticamente
- **Nota**: O botão "Exibir Distâncias" fica desabilitado para grafos OSM

### 2. Navegar no Mapa
- **Zoom**: Scroll do mouse
- **Pan**: Ctrl+clique e arrastar
- **Reset**: Botão de reset no painel de zoom

### 3. Calcular Rota
- Clique em dois vértices para selecionar origem e destino
- Clique em "🛣️ Calcular Rota"
- O caminho mais curto será exibido em vermelho

### 4. Editar Grafo
- Clique em "✏️ Criar Grafo" para entrar no modo de edição
- **Adicionar vértice**: Clique em área vazia
- **Adicionar aresta**: Clique em dois vértices consecutivos
- **Remover**: Clique direito no elemento
- **Gerar arestas**: Botão habilitado apenas quando há 2+ vértices

### 5. Capturar Imagem
- Clique em "📋 Copiar Imagem" para copiar para clipboard
- Clique em "💾 Salvar Imagem" para salvar arquivo
- **Títulos**: As capturas são salvas como "Captura 1.", "Captura 2.", etc.

## 🔧 Controles Inteligentes

### Botões Contextuais
- **"Exibir Distâncias"**: Habilitado apenas para grafos criados manualmente
- **"Gerar Arestas"**: Habilitado apenas quando há 2 ou mais vértices
- **Botões de Edição**: Habilitados apenas no modo de edição

### Detecção Automática
- **Grafos OSM**: Detectados automaticamente por atributos específicos
- **Grafos Manuais**: Criados pelo usuário no modo de edição

## 🛠️ Tecnologias

- **Python 3.9+** - Linguagem principal
- **Tkinter** - Interface gráfica
- **OSMNX** - Manipulação de dados OSM
- **NetworkX** - Análise de grafos
- **Pillow** - Processamento de imagens

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos. 