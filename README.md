# 🗺️ Navegador OSM - Visualizador de Grafos

Aplicativo desktop para visualização e manipulação de grafos, com suporte a dados OSM (OpenStreetMap) e algoritmo de Dijkstra.

## 🚀 Como Executar

### Pré-requisitos
- **Python 3.12**
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

**⚠️ Importante**: Devido a compatibilidade com a biblioteca OSMNX, este projeto foi desenvolvido especificamente para Python 3.12 e pode não funcionar corretamente em outras versões.

**💡 Dica**: Se você tem múltiplas versões do Python instaladas, use `py -3.12 main.py` para garantir que a versão correta seja executada.

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
- **Cores Personalizadas** - Diferenciação de tipos de rua com legenda explicativa
- **Exibição de Distâncias** - Pesos das arestas (apenas para grafos criados manualmente com até 150 vértices)

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

### 🚀 Primeiros Passos

#### 1. Importar Mapa OSM
1. **Clique** no botão "📂 Importar OSM"
2. **Selecione** um arquivo .osm no seu computador
3. **Aguarde** o carregamento do mapa
4. **Navegue** usando zoom (scroll) e pan (Ctrl+clique e arrastar)

**💡 Dica**: Arquivos OSM podem ser exportados do site oficial do OpenStreetMap.

#### 2. Criar Grafo Manual
1. **Clique** no botão "✏️ Criar Grafo" na barra lateral
2. **Observe** que o botão fica verde e a borda do canvas muda para verde, o que significa que o modo de edição está ativado
3. **Clique** em áreas vazias do canvas para adicionar vértices
4. **Clique** em dois vértices consecutivos para criar arestas
6. **Clique direito** em vértices ou arestas para removê-los
7. **Gerar Vértices Aleatórios**: Use o botão "🎯 Gerar Vértices"
8. **Gerar Arestas Aleatórias**: Use o botão "🎲 Gerar Arestas" (requer 2+ vértices)

### 🧭 Navegação e Visualização

#### Controles de Navegação
- **🔍 Zoom In**: Scroll do mouse para cima ou botão "🔍+"
- **🔍 Zoom Out**: Scroll do mouse para baixo ou botão "🔍-"
- **🔍 Reset Zoom**: Botão "🔍" para voltar ao zoom padrão
- **🖱️ Pan**: Ctrl+clique e arrastar para mover a visualização

#### Opções de Visualização
- **Exibir Distâncias**: Mostra pesos das arestas (apenas grafos manuais com ≤150 vértices)
- **Identificar Vias**: Diferencia ruas por tipo (apenas grafos OSM)
  - 🔵 Azul: Mão única
  - 🟠 Laranja: Mão dupla
- **Ocultar/Mostrar Vértices**: Controla a exibição dos pontos no mapa

### 🛣️ Calculando Rotas

#### Passo a Passo
1. **Certifique-se** de que há um grafo carregado (OSM ou manual)
2. **Clique** em um vértice para selecionar a origem (aparece em verde)
3. **Clique** em outro vértice para selecionar o destino (aparece em vermelho)
4. **Clique** no botão "🛣️ Calcular Rota" no painel inferior
5. **Observe** o caminho mais curto exibido em vermelho
6. **Verifique** as estatísticas no painel de histórico

#### Informações da Rota
- **Distância Total**: Em metros
- **Tempo de Execução**: Em milissegundos
- **Nós Explorados**: Quantidade de vértices visitados
- **Caminho**: Lista completa de vértices da rota

### 📸 Capturando Imagens

#### Copiar para Clipboard
1. **Configure** a visualização desejada (zoom, cores, etc.)
2. **Clique** no botão "📋 Copiar Imagem"
3. **Cole** em qualquer aplicativo (Ctrl+V)

#### Salvar Arquivo
1. **Configure** a visualização desejada
2. **Clique** no botão "💾 Salvar Imagem"
3. **Escolha** o local e nome do arquivo
4. **Confirme** o salvamento

**📁 Localização**: As imagens são salvas em `assets/capturas/` com títulos automáticos ("Captura 1.", "Captura 2.", etc.)

### 🗑️ Gerenciando Grafos

#### Apagar Grafo Atual
1. **Clique** no botão "🗑️ Apagar Grafo"
2. **Confirme** a ação
3. **Observe** que todos os dados são removidos

#### Limpar Seleção
1. **Clique** no botão "Limpar Seleção" no painel inferior
2. **Observe** que origem e destino são desmarcados
3. **O caminho** calculado é removido

### 📊 Histórico e Estatísticas

#### Painel de Histórico
- **Localização**: Painel lateral direito
- **Rotas**: Lista de todas as rotas calculadas na sessão
- **Capturas**: Lista de todas as imagens salvas
- **Refazer Rota**: Clique no botão "🔄" para recalcular uma rota anterior

#### Informações Exibidas
- **Número da Rota**: Ordem cronológica
- **Origem e Destino**: IDs dos vértices
- **Distância**: Em metros com 2 casas decimais
- **Tempo**: Em milissegundos com 2 casas decimais
- **Nós Explorados**: Quantidade de vértices visitados

#### Otimizações de Performance
- **Zoom Fluido**: Renderização otimizada durante navegação
- **Limite de Vértices**: 150 vértices para exibir distâncias
- **Cache Inteligente**: Reutilização de imagens quando possível
- **Supersample Adaptativo**: Qualidade ajustada conforme necessidade

### ⚠️ Limitações e Considerações

#### Limitações Técnicas
- **Python 3.12**: Versão obrigatória para compatibilidade
- **Arquivos OSM**: Apenas arquivos .osm são suportados
- **Tamanho de Grafo**: Performance pode diminuir com grafos muito grandes
- **Memória**: Grafos muito complexos podem consumir muita memória

## 🛠️ Tecnologias

- **Python 3.12** - Linguagem principal (versão obrigatória)
- **Tkinter** - Interface gráfica
- **OSMNX** - Manipulação de dados OSM
- **NetworkX** - Análise de grafos
- **Pillow** - Processamento de imagens

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos. 