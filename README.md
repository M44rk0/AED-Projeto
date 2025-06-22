# 🗺️ Navegador OSM - Visualizador de Grafos

Um aplicativo desktop completo para visualização e manipulação de grafos, com suporte a importação de dados OSM (OpenStreetMap), algoritmos de roteamento avançados e interface gráfica moderna.

## 📋 Índice

- [🚀 Como Executar](#-como-executar)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🎯 Funcionalidades](#-funcionalidades)
- [🖥️ Interface do Usuário](#️-interface-do-usuário)
- [🛠️ Arquitetura do Sistema](#️-arquitetura-do-sistema)
- [📚 Guia de Uso](#-guia-de-uso)
- [🔧 Desenvolvimento](#-desenvolvimento)
- [🐛 Troubleshooting](#-troubleshooting)
- [📝 Licença](#-licença)

## 🚀 Como Executar

### Pré-requisitos

- **Python 3.7+** (recomendado: Python 3.9+)
- **Sistema Operacional**: Windows, macOS ou Linux
- **Memória RAM**: Mínimo 4GB (recomendado: 8GB+)
- **Espaço em Disco**: 100MB livres

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd CursorAED
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o aplicativo:**
   ```bash
   python main.py
   ```

### Dependências Principais

- **tkinter** - Interface gráfica (incluído no Python)
- **osmnx** - Manipulação de dados OSM
- **networkx** - Análise de grafos
- **PIL (Pillow)** - Processamento de imagens
- **matplotlib** - Visualização (dependência do osmnx)

## 📁 Estrutura do Projeto

```
CursorAED/
├── main.py                 # 🚀 Ponto de entrada principal
├── core/                   # 🧠 Lógica e algoritmos principais
│   ├── __init__.py
│   ├── GraphManager.py     # Gerenciamento de grafos
│   ├── GraphDrawer.py      # Renderização de grafos
│   ├── Dijkstra.py         # Algoritmo de Dijkstra
│   ├── GraphOperations.py  # Operações de grafo
│   └── SelectionManager.py # Gerenciamento de seleção
├── ui/                     # 🖥️ Interface gráfica
│   ├── __init__.py
│   ├── MapaTkinter.py      # Janela principal
│   ├── Sidebar.py          # Painel lateral
│   ├── ActionPanel.py      # Painel de ações
│   ├── ZoomPanel.py        # Controles de zoom
│   ├── HistoryPanel.py     # Painel de histórico
│   ├── TooltipManager.py   # Gerenciamento de tooltips
│   ├── UIManager.py        # Gerenciamento de UI
│   ├── ViewManager.py      # Gerenciamento de visualização
│   ├── EventManager.py     # Gerenciamento de eventos
│   ├── ToggleManager.py    # Gerenciamento de toggles
│   └── ZoomPanTool.py      # Ferramentas de zoom/pan
├── managers/               # 📋 Gerenciadores auxiliares
│   ├── __init__.py
│   ├── ImageManager.py     # Gerenciamento de imagens
│   └── HistoryManager.py   # Gerenciamento de histórico
├── assets/                 # 🖼️ Recursos (imagens, capturas)
│   └── capturas/           # Capturas de tela salvas
├── .git/                   # 📦 Controle de versão
├── .gitignore             # 🚫 Arquivos ignorados
├── requirements.txt        # 📦 Dependências do projeto
└── README.md              # 📚 Este arquivo
```

## 🎯 Funcionalidades

### 📂 Importação de Dados
- **Arquivos OSM (.osm)** - Importação de mapas reais do OpenStreetMap
- **Criação Manual** - Construção de grafos do zero
- **Geração Aleatória** - Vértices e arestas automáticas
- **Validação de Dados** - Verificação de integridade dos arquivos

### 🎨 Visualização Avançada
- **Zoom Fluido** - Zoom suave com scroll do mouse
- **Pan Intuitivo** - Arrastar para navegar (Ctrl+clique ou botão do meio)
- **Grid de Fundo** - Grade de referência visual
- **Cores Personalizadas** - Diferenciação de tipos de rua
- **Exibição de Distâncias** - Pesos das arestas em tempo real

### 🧮 Algoritmos de Roteamento
- **Dijkstra Otimizado** - Cálculo do caminho mais curto
- **Estatísticas Detalhadas** - Tempo de execução e nós explorados
- **Histórico de Rotas** - Salvamento e reutilização de caminhos
- **Validação de Caminhos** - Verificação de conectividade

### 🖥️ Interface Moderna
- **Design Responsivo** - Adaptação a diferentes resoluções
- **Tooltips Contextuais** - Dicas inteligentes baseadas no contexto
- **Histórico Visual** - Cards com informações detalhadas
- **Captura de Imagens** - Salvamento e cópia para clipboard
- **Modo de Edição** - Interface especializada para criação de grafos

## 🖥️ Interface do Usuário

### 🎛️ Painel Lateral (Sidebar)
- **📂 Importar OSM** - Carregar arquivos de mapa
- **✏️ Criar Grafo** - Alternar modo de edição
- **🎯 Gerar Vértices** - Criar nós aleatórios
- **🎲 Gerar Arestas** - Conectar vértices automaticamente
- **🗑️ Apagar Grafo** - Limpar dados atuais
- **📋 Copiar Imagem** - Copiar para área de transferência
- **💾 Salvar Imagem** - Salvar captura de tela
- **📏 Exibir Distâncias** - Mostrar pesos das arestas
- **🎨 Identificar Ruas** - Cores por tipo de via

### 🎮 Painel de Ações (Action Panel)
- **Limpar Seleção** - Resetar seleção atual
- **🛣️ Calcular Rota** - Executar algoritmo de Dijkstra
- **👁️ Mostrar/Ocultar Vértices** - Toggle de visualização

### 🔍 Controles de Zoom (Zoom Panel)
- **🔍-** - Zoom out
- **🔍** - Reset zoom (100%)
- **🔍+** - Zoom in

### 📜 Painel de Histórico (History Panel)
- **Rotas Calculadas** - Lista de caminhos anteriores
- **Capturas Salvas** - Imagens do grafo
- **🔄 Refazer Rota** - Replicar caminho anterior
- **📂 Abrir Imagem** - Visualizar captura salva

## 🛠️ Arquitetura do Sistema

### 🏗️ Padrão de Design
O projeto segue o padrão **MVC (Model-View-Controller)** adaptado:

- **Model (core/)** - Lógica de negócio e dados
- **View (ui/)** - Interface gráfica e apresentação
- **Controller (managers/)** - Coordenação entre Model e View

### 🔄 Fluxo de Dados
```
Usuário → EventManager → GraphOperations → GraphManager → GraphDrawer → Canvas
   ↑                                                                    ↓
   └── UIManager ← ViewManager ← SelectionManager ← HistoryManager ←──┘
```

### 📦 Módulos Principais

#### Core (Lógica de Negócio)
- **GraphManager**: Gerenciamento central de grafos
- **GraphDrawer**: Renderização e visualização
- **Dijkstra**: Algoritmo de roteamento
- **GraphOperations**: Operações de alto nível
- **SelectionManager**: Estado de seleção

#### UI (Interface)
- **MapaTkinter**: Janela principal e coordenação
- **Sidebar**: Controles principais
- **ActionPanel**: Ações secundárias
- **ZoomPanel**: Controles de navegação
- **HistoryPanel**: Histórico de ações

#### Managers (Coordenação)
- **ImageManager**: Captura e salvamento de imagens
- **HistoryManager**: Gerenciamento de histórico
- **EventManager**: Processamento de eventos
- **UIManager**: Estado da interface
- **ViewManager**: Coordenação de visualização

## 📚 Guia de Uso

### 🗺️ Primeiros Passos

1. **Iniciar o Aplicativo**
   ```bash
   python main.py
   ```

2. **Importar um Mapa OSM**
   - Clique em "📂 Importar OSM"
   - Selecione um arquivo .osm
   - O mapa será carregado automaticamente

3. **Navegar no Mapa**
   - **Zoom**: Scroll do mouse
   - **Pan**: Ctrl+clique e arrastar
   - **Reset**: Clique no botão 🔍

### 🛣️ Calculando Rotas

1. **Selecionar Origem**
   - Clique em um vértice (ponto no mapa)
   - O vértice ficará verde

2. **Selecionar Destino**
   - Clique em outro vértice
   - O vértice ficará vermelho

3. **Calcular Rota**
   - Clique em "🛣️ Calcular Rota"
   - O caminho mais curto será destacado em vermelho

### ✏️ Modo de Edição

1. **Ativar Modo de Edição**
   - Clique em "✏️ Criar Grafo"
   - A interface mudará para modo de edição

2. **Criar Vértices**
   - Clique em áreas vazias do canvas
   - Vértices serão criados automaticamente

3. **Criar Arestas**
   - Clique em um vértice (origem)
   - Clique em outro vértice (destino)
   - Digite o peso da aresta

4. **Remover Elementos**
   - **Vértice**: Clique direito no vértice
   - **Aresta**: Clique direito próximo à aresta

### 📸 Capturando Imagens

1. **Copiar para Clipboard**
   - Clique em "📋 Copiar Imagem"
   - A imagem será copiada para área de transferência

2. **Salvar Arquivo**
   - Clique em "💾 Salvar Imagem"
   - Escolha local e nome do arquivo
   - A imagem será salva em `assets/capturas/`

## 🔧 Desenvolvimento

### 🏗️ Estrutura Modular
O projeto foi organizado para facilitar manutenção e extensão:

- **Separação de Responsabilidades**: Cada módulo tem uma função específica
- **Baixo Acoplamento**: Módulos se comunicam através de interfaces bem definidas
- **Alta Coesão**: Funcionalidades relacionadas estão agrupadas

### ➕ Adicionando Novas Funcionalidades

#### Novos Algoritmos
1. Crie o arquivo em `core/`
2. Implemente a lógica do algoritmo
3. Adicione métodos de interface em `GraphOperations`
4. Conecte à interface em `MapaTkinter`

#### Novos Componentes de UI
1. Crie o arquivo em `ui/`
2. Implemente a classe do componente
3. Adicione ao `__init__.py` da pasta
4. Integre em `MapaTkinter`

#### Novos Gerenciadores
1. Crie o arquivo em `managers/`
2. Implemente a lógica de gerenciamento
3. Conecte aos eventos apropriados
4. Atualize a documentação

### 🧪 Testes
Para adicionar testes automatizados:

1. Crie uma pasta `tests/`
2. Adicione arquivos de teste para cada módulo
3. Use `pytest` ou `unittest`
4. Execute com: `python -m pytest tests/`

### 📦 Distribuição
Para criar um executável:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Criar executável
pyinstaller --onefile --windowed main.py
```

## 🐛 Troubleshooting

### ❌ Problemas Comuns

#### Erro: "ModuleNotFoundError"
**Sintomas**: Erro ao importar módulos do projeto
**Solução**: 
```bash
# Certifique-se de estar na pasta raiz
cd CursorAED

# Execute o main.py
python main.py
```

#### Erro: "No module named 'osmnx'"
**Sintomas**: Erro ao importar bibliotecas externas
**Solução**:
```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instalar manualmente
pip install osmnx networkx pillow
```

#### Performance Lenta
**Sintomas**: Interface lenta com grafos grandes
**Soluções**:
- Reduza o zoom para melhor performance
- Use grafos menores para testes
- Feche outros aplicativos para liberar memória

#### Imagem Não Salva
**Sintomas**: Erro ao salvar capturas
**Solução**:
- Verifique permissões da pasta `assets/capturas/`
- Certifique-se de ter espaço em disco
- Tente salvar em local diferente

### 🔍 Debug

#### Logs de Erro
Para ver logs detalhados, execute:
```bash
python main.py 2>&1 | tee debug.log
```

#### Verificar Dependências
```bash
# Listar versões instaladas
pip list | grep -E "(osmnx|networkx|pillow)"

# Verificar compatibilidade
python -c "import osmnx; print(osmnx.__version__)"
```

### 📞 Suporte
Se encontrar problemas não listados:

1. Verifique se está usando Python 3.7+
2. Confirme que todas as dependências estão instaladas
3. Teste com um arquivo OSM simples
4. Verifique os logs de erro

## 📝 Licença

Este projeto é de uso **educacional e de demonstração**. 

### 🎓 Uso Educacional
- Livre para uso em cursos e estudos
- Pode ser modificado para fins educacionais
- Atribuição é apreciada mas não obrigatória

### 🚫 Limitações
- Não para uso comercial sem autorização
- Não para redistribuição como produto final
- Não garante compatibilidade com todos os sistemas

### 🤝 Contribuições
Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Teste thoroughly
5. Submeta um pull request

---

**Desenvolvido para o estudo de algoritmos de grafos e visualização de dados geográficos.** 